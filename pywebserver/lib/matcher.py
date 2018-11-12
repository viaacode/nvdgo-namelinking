import re
import unidecode
from collections import namedtuple, defaultdict, OrderedDict
from itertools import chain
from pythonmodules.profiling import timeit
from pythonmodules.namenlijst import Namenlijst
from pythonmodules.translations import Translator
from pythonmodules.config import Config
import logging
from pysolr import Solr
from .solrimport import Importer
from pythonmodules.ner import normalize
from functools import partial


logger = logging.getLogger(__name__)

Score = namedtuple('Score', ('text', 'min_distance', 'match', 'distances'))
Scores = namedtuple('Scores', ('amount', 'score', 'matches', 'rating', 'source'))
Rating = namedtuple('Rating', ('scores', 'total'))
Lookup = namedtuple('Lookup', ('value', 'multiplier', 'alternate_spellings', 'max_distance'))


class Matcher:
    def __init__(self, text, base):
        self.text = self.normalize(text)
        if type(base) is str:
            base = [base]
        
        self.indices = list(chain(*[[found.span() for found in self.find(b)] for b in base]))

        if not len(self.indices):
            logger.warning('Could not find base text "%s"', base)
            raise IndexError('Could not find base text "%s"' % base)

    @staticmethod
    def normalize(txt):
        return normalize(txt).strip()

    @classmethod
    def search_term(cls, term):
        """
        eg. 'Victor Hugo' -> 'v\\s*i\\s*c\\s*t\\s*o\\s*r\\s*h\\s*u\\s*g\\s*o'
        :param term: str
        """
        term = cls.normalize(term).replace(' ', '')
        if not term.isdigit():
            term = '\s*'.join(term)

        return re.compile(term)

    def find(self, text):
        term = self.search_term(text)
        return re.finditer(term, self.text)

    def score(self, text, lookup: Lookup):
        matches = dict()
        max_distance = lookup.max_distance if lookup else 100

        # find closest index
        for found in self.find(text):
            # logger.debug('found %s: %s | %s', text, found, self.indices)
            m = found.span()
            found_text = found.group(0)
            distances = []
            best_dist = len(self.text) + 1
            best_idx = []
            for i in self.indices:
                if m[1] > i[1]:
                    # dir = 'right'
                    if (m[1] - i[1]) < best_dist:
                        best_dist = m[1] - i[1]
                        best_idx = (i[1], m[1])
                else:
                    # dir = 'left'
                    if (i[0] - m[0]) < best_dist:
                        best_dist = i[0] - m[0]
                        best_idx = (m[0], i[0])
            # logger.debug('%s m: %s, i: %s, best_dist %d, bestidx %s', dir, m, i, best_dist, best_idx)
            words_distance = max(1, self.text.count(' ', best_idx[0], best_idx[1]+1))

            if words_distance < 10:
                logger.debug('FOUND "%s" (match "%s") in text "%s"', text, found_text, self.text[best_idx[0]:best_idx[1]+1])
            if words_distance > max_distance:
                continue
            distances.append(words_distance)
            if found_text not in matches:
                matches[found_text] = Score(text=text, min_distance=words_distance, match=found_text,
                                            distances=[words_distance])
            else:
                matches[found_text].distances.append(words_distance)
                if words_distance < matches[found_text].min_distance:
                    distances = matches[found_text].distances
                    matches[found_text] = Score(text=text, min_distance=words_distance, match=found_text,
                                                distances=distances)

        logger.debug(matches)

        return matches.values()

    def scores(self, lookups):
        if not len(self.indices):
            return {}
        result = dict()
        done = []
        logger.debug('lookups: %s', lookups)
        for k, lookup in lookups.items():
            if lookup is None:
                logger.debug('check %s: None', k)
                continue
            v, multiplier, vals, max_distance = lookup
            score = []
            logger.debug('check %s: %s', k, vals)
            for val in vals:
                norm_val = self.normalize(val)
                # avoid scores being added multiple times
                if norm_val not in done:
                    score.extend(self.score(val, lookup))
                    done.append(norm_val)

            logger.debug('%s score = %s, (vals: %s)', k, str(score), vals)
            if len(score):
                amount = len(score)
                min_distance = min(s.min_distance for s in score)
                rating = multiplier/(4*(min_distance**1.2))
                result[k] = Scores(amount,
                                   min_distance,
                                   set([str(s.match) for s in score]),
                                   rating,
                                   score)
        return result


class Rater:
    default_max_distance = 100
    _solr = Solr(Config(section='solr')['url'])
    possiblereplacements = dict(
        sergeant=set(['sergent']),
        soldat=set(['soldaat', 'soldier']),
        kaporaal=set(['korporaal']),
    )

    for k in list(possiblereplacements.keys()):
        vals = possiblereplacements[k]
        for val in vals:
            if val not in possiblereplacements:
                possiblereplacements[val] = set()
            possiblereplacements[val].add(k)
            possiblereplacements[val].update(vals)

    def __init__(self, pid, nmlid, name=None):
        if '_' not in pid:
            raise ValueError("Pid '%s' does not seem in correct format" % pid)
        self.pid = pid
        self.nmlid = nmlid
        self.name = name
        self._language = None
        self._alto = None
        self._details = None
        self._lookups = None
        self._text = None

    @staticmethod
    def get_alternate_spellings(val):
        if type(val) is int:
            val = str(val)
        if type(val) is str:
            val = [val]
        values = set(val)

        def add(a, b):
            values.add(v.replace(a, b))
            values.add(v.replace(b, a))

        for v in val:
            add('ks', 'x')   # koksijde -> koxijde
            add('aa', 'ae')  # vlAAr -> vlAEr
            add('c', 'k')    # Corbeek -> Korbeek
            if v in Rater.possiblereplacements:
                values.update(Rater.possiblereplacements[v])
            if 'shire' in v and len(v) > 8:
                values.add(v.replace('shire', ''))

        return values

    @property
    def text(self):
        if self._text is None:
            res = self._solr.search('id:%s' % self.pid, rows=1, fl=['text', 'language'])

            if res.hits == 0:
                # might as well import it now
                importer = Importer()
                importer.process(self.pid)
                res = self._solr.search('id:%s' % self.pid, rows=1, fl=['text', 'language'])

            if not len(res) or not len(res.docs):
                self._text = ''
            else:
                res = res.docs[0]
                self._text = res['text']
                self._language = res['language']
        return self._text

    @property
    def language(self):
        if self._language is None:
            # pre load text fills in language
            text = self.text
        return self._language

    @property
    def details(self):
        if self._details is None:
            with timeit('nml', 1000):
                self._details = Namenlijst().get_person_full(self.nmlid, self.language)
        return self._details

    @property
    def lookups(self):
        if self._lookups is None:
            debug_call = logger.info
            nml = self.details
            self._lookups = OrderedDict()
            err = 'LOOKUP "%s" %s'

            def addlookup(name, f, multiplier=1, min_size=3, allow_numeric=False, max_distance=100,
                          alternate_spellings=None):
                lookup = None
                try:
                    val = f()
                    if type(val) is int:
                        val = str(val)

                    if type(val) is str:
                        val = [val]

                    if not allow_numeric:
                        val = [re.sub(r"[0-9]+", "", v) for v in val]

                    val = list(filter(lambda v: len(Matcher.normalize(v)) >= min_size, val))

                    if not len(val):
                        raise TypeError("too short")

                    if alternate_spellings is None:
                        alternate_spellings = self.get_alternate_spellings(val)
                    lookup = Lookup(val[0], multiplier, alternate_spellings, max_distance)
                except KeyError as e:
                    debug_call(err, name, e)
                except IndexError as e:
                    debug_call(err, name, e)
                except TypeError as e:
                    debug_call(err, name, e)
                finally:
                    self._lookups[name] = lookup

            def homeaddress():
                v = nml.events['where']
                if v['where_reason'] != 'homeaddress':
                    raise KeyError("no homeaddress")
                return v

            def addnumlookup(name, f, multiplier=1, max_distance=20, buffer=0, min_len=None):
                lookup = None
                try:
                    strv = f()
                    val = int(strv)
                    if type(strv) is not str:
                        strv = str(strv)

                    if val is None or val == 0:
                        raise KeyError('too low')

                    if buffer > 0:
                        alternate_spellings = tuple(set(map(lambda x: " %d " % x, range(val - buffer, val+buffer+1))))
                    else:
                        alternate_spellings = tuple([' %s ' % strv])

                    if min_len is not None and len(strv) < min_len:
                        raise ValueError('not long enough')
                    # logger.debug('alter %s', alternate_spellings)
                    lookup = Lookup(strv, multiplier, alternate_spellings, max_distance)
                except Exception as e:
                    debug_call(err, name, e)
                finally:
                    self._lookups[name] = lookup

            trs = [Translator.factory(l, self.language) for l in ('nl', 'fr', 'en') if l != self.language]

            def transl(text):
                text = [t.strip() for t in text.split('/')]
                items = list()
                for word in text:
                    items.extend([tr.translate(word) for tr in trs])
                items.append(text)
                return chain(*items)

            addlookup('employer', lambda: nml.events['work']['work_company_name'], 3)
            addlookup('died_place_topo', lambda: nml.events['died']['topo'], 2, max_distance=300)
            addlookup('profession', lambda: nml.events['work']['work_profession'], 2)
            addlookup('school_topo', lambda: nml.events['school']['topo'], 2, max_distance=300)
            addlookup('school_name', lambda: nml.events['school']['school_name'], 2)
            addlookup('homeaddresstopo', lambda: homeaddress()['topo'], 2, max_distance=300)

            addnumlookup('enlisted_number', lambda: nml.events['enlisted']['enlisted_number'].split('/', 1)[1], 10,
                         max_distance=10, min_len=4)

            addlookup('enlisted_rank', lambda: transl(nml.events['enlisted']['enlisted_rank'].lower()), max_distance=5,
                      allow_numeric=True)

            for i in range(0, 3):
                addlookup('enlisted_regt%d' % i,
                          lambda: nml.events['enlisted']['enlisted_regt'].split('/')[i],
                          1)

            addlookup('profession_translated',
                      lambda: transl(nml.events['work']['work_profession'].strip(' .').lower()),
                      2)

            addlookup('victim_type_details',
                      lambda: nml.victim_type_details,
                      max_distance=10)

            for key in ('army', 'sub'):
                key = 'enlisted_%s' % key
                addlookup(key, lambda: nml.events['enlisted'][key], min_size=4, allow_numeric=True)

            addlookup('died_place_locality', lambda: nml.died_place['locality'])
            addlookup('born_place_locality', lambda: nml.born_place['locality'])
            addlookup('homeaddress', lambda: homeaddress()['place']['name'])
            addnumlookup('died_age', lambda: nml.died_age, max_distance=5, buffer=1)

        return self._lookups

    def ratings(self):
        language, nml = self.language, self.details
        names = nml.names.variations_normalized
        if self.name is not None:
            names.add(self.name)
        matcher = Matcher(self.text, names)
        scores = matcher.scores(self.lookups)

        '''
        total_score = \sum_{}\frac{multiplier}{4\sqrt[5]{score^6}}
        '''
        total = min(1, sum(scores[k].rating for k in scores))
        if len(scores) == 1:
            total /= 2
        return Rating(scores, total)
