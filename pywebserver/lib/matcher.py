import re
from collections import namedtuple, OrderedDict
from itertools import chain
from pythonmodules.profiling import timeit
from pythonmodules.namenlijst import Namenlijst
from pythonmodules.translations import Translator
from pythonmodules.config import Config
import logging
from pysolr import Solr
from .solrimport import Importer
from pythonmodules.ner import normalize
from pythonmodules.mediahaven import MediaHaven
import json
from babel.dates import format_date, get_date_format


logger = logging.getLogger(__name__)

Score = namedtuple('Score', ('text', 'min_distance', 'match', 'distances'))
Scores = namedtuple('Scores', ('amount', 'score', 'matches', 'rating', 'source'))
Rating = namedtuple('Rating', ('scores', 'total', 'total_multiplier'))
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

            # if words_distance < 10:
            #     logger.debug('FOUND "%s" (match "%s") in text "%s"', text, found_text, self.text[best_idx[0]:best_idx[1]+1])

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
        # logger.debug('lookups: %s', lookups)
        for k, lookup in lookups.items():
            if lookup is None:
                logger.debug('check %s: None', k)
                continue
            v, multiplier, vals, max_distance = lookup
            score = []
            # logger.debug('check %s: %s', k, vals)
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
                # dist_pct = (min_distance / (lookup.max_distance+1))*20
                # rating = multiplier/((80*dist_pct)**1.2)
                rating = multiplier/(3*(min_distance**0.60))
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
        kaporaal=set(['korporaal', 'caporal']),
        handelaar=set(['verkoper', 'marchand', "koopman"])
    )

    possiblereplacements["voyageur de commerce"] = set(['handelaar'])

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
        val = set(map(str.strip, val))
        values = set(val)

        def add(a, b):
            values.add(v.replace(a, b))
            values.add(v.replace(b, a))

        for i in range(2):
            for v in val:
                add('ks', 'x')    # koksijde <-> koxijde
                add('estraat', 'enstraat')  # ravESTRAAT <-> ravENSTRAAT
                add('aa', 'ae')   # vlAAr <-> vlAEr
                add('c', 'k')     # Corbeek <-> Korbeek
                add('ck', 'k')    # werviK <-> werviCK
                add('ghe', 'ge')  # ledeghem <-> ledeGem
                add('ll', 'lj')   # gefusiLLeerd <-> gefusiLJeerd
                add('vam de', 'van de')  # "VAM de" <-> "VAN de"
                add('van de', 'van de')
                add('aa', 'a')
                add('ui', 'uy')   # bUIsingen <-> bUYsingen
                add('z', 's')
                add('niklaas', 'nikolaas')
                add('chasseurs a pied', 'chass a pied')
                add('regiment de', 'reg de')
                add('linieregiment', 'liniereg')
                values.add(v.replace('adjoint', ''))
                if v in Rater.possiblereplacements:
                    values.update(Rater.possiblereplacements[v])
                if 'shire' in v and len(v) > 8:
                    values.add(v.replace('shire', ''))
            val = set(values)

        return values

    @property
    def text(self):
        if self._text is None:
            res = self._solr.search('id:%s' % self.pid, rows=1, fl=['text', 'language'])

            if res.hits == 0:
                logger.warning('%s not yet in solr, import now', self.pid)
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
            self._details = Namenlijst().get_person_full(self.nmlid, self.language)
        return self._details

    @property
    def lookups(self):
        if self._lookups is None:
            debug_call = logger.debug
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
                    val.extend(list(map(Matcher.normalize, val)))

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

            def getdates(d, lang):
                def dformat(x):
                    form = get_date_format(x, lang)
                    form = form.pattern.replace('y', '').replace('Y', '')
                    return str(format_date(d, locale=lang, format=form)).lower()

                formats = list(map(dformat, ('short', 'medium', 'long', 'full')))
                formats.extend([format_.replace('augustus', 'oogst') for format_ in formats])
                return list(set(formats))

            def adddatelookup(name, f, multiplier=1, max_distance=50):
                lookup = None
                try:
                    val = f()

                    langmappings = {
                        "nl": "nl_BE",
                        "fr": "fr_FR",
                        "de": "de_DE",
                        "en": "en_GB",
                    }

                    alternate_spellings = getdates(val, langmappings[self.language])
                    strv = alternate_spellings[0]
                    lookup = Lookup(strv, multiplier, alternate_spellings, max_distance)
                    pass
                except Exception as e:
                    debug_call(err, name, e)
                finally:
                    self._lookups[name] = lookup

            def addnumlookup(name, f, multiplier=1, max_distance=20, buffer=0, min_len=None):
                lookup = None
                try:
                    strv = f()
                    val = int(strv)
                    if type(strv) is not str:
                        strv = str(strv)

                    if val is None or val < 10:
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

            addlookup('employer', lambda: nml.events['work']['work_company_name'], 2)
            addlookup('died_place_topo', lambda: nml.events['died']['topo'], 2, max_distance=300)
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

            addlookup('work_company', lambda: transl(nml.events['work']['work_company_name'].strip(' .').lower()))

            addlookup('profession',
                      lambda: transl(nml.events['work']['work_profession'].strip(' .').lower()),
                      2)

            def victim_type(name):
                victim_types_to_text = dict(
                    executed=['execute', 'shot', 'gefusilleerd', 'fusillade', 'geschoten', 'doodgeschoten', 'geexecuteerd',
                              'gefusiljeerd', 'veroordeeld', 'condamne', 'doodstraf', 'doodvonnis', 'martyr'],

                )
                if name in victim_types_to_text:
                    return victim_types_to_text[name]

                if 'bombardement' in nml.events['died']['death_reason']:
                    return ['bombardement', 'bombardeerd', 'bombarde', 'bommenwerp']

            addlookup('victim_type_details',
                      lambda: victim_type(nml.victim_type_details.lower()),
                      max_distance=50)

            for key in ('army', 'sub'):
                key = 'enlisted_%s' % key
                addlookup(key, lambda: nml.events['enlisted'][key], min_size=4, allow_numeric=True)

            addlookup('died_place_locality', lambda: nml.died_place['locality'])
            addlookup('died_place_name', lambda: nml.died_place['name'])
            addlookup('born_place_locality', lambda: nml.born_place['locality'])
            addlookup('born_place_name', lambda: nml.born_place['name'])
            addlookup('memorated_place_locality', lambda: nml.events['memorated.original']['place']['locality'])
            addlookup('memorated_place_name', lambda: nml.events['memorated.original']['place']['name'])

            addlookup('homeaddress', lambda: homeaddress()['place']['name'])

            adddatelookup('died_date', lambda: nml.died_date, multiplier=2)
            adddatelookup('born_date', lambda: nml.born_date, multiplier=2)
            adddatelookup('memorated_date', lambda: nml.events['memorated.original']['start'], multiplier=2)
            addlookup('work_place_locality', lambda: nml.events['work']['place']['locality'], multiplier=0.5)
            addnumlookup('died_age', lambda: nml.died_age, max_distance=5, buffer=1, multiplier=0.5)

        return self._lookups

    def ratings(self):
        language, nml = self.language, self.details
        names = nml.names.variations_normalized
        if self.name is not None:
            names.add(self.name)
        matcher = Matcher(self.text, names)
        scores = matcher.scores(self.lookups)
        m = len(scores)

        '''
        total_score = \sum_{}\frac{multiplier}{4\sqrt[5]{score^6}}
        '''
        total = sum(scores[k].rating for k in scores)
        total_multiplier = .5 + (m / 5)
        total *= total_multiplier
        total = min(0.99, total)
        return Rating(scores, total, total_multiplier)


class Meta:
    def __init__(self, config=None):
        self.nl = Namenlijst(config)
        self.mh = MediaHaven(config)

    def __call__(self, full_pid, external_id, entity, score, meta):
        nl = self.nl
        mh = self.mh
        attestation_id = 'namenlijst/%s/%s/%s' % (full_pid, external_id, entity.replace(' ', '/'))
        if score > 0.99:
            score = 0.99

        if meta is not None:
            if type(meta) is str:
                meta = json.loads(meta)
        else:
            meta = dict()

        meta['found_name'] = entity
        meta['quality'] = score
        meta['full_pid'] = full_pid
        meta['attestation_id'] = attestation_id

        def notexists(*fields):
            return any(field not in meta or meta[field] is None for field in fields)

        logger.info('Generate meta data for %s', attestation_id)

        keys = ('born_country', 'died_country', 'died_age', 'gender', 'victim_type', 'victim_type_details')
        if notexists('extra', 'subtitle', 'name') or \
           any(f not in meta['extra'] for f in keys):
            person = nl.get_person_full(external_id)
            meta['name'] = person.names.name
            extra = dict()
            extra['born_country'] = person.born_place['country_code'].upper()
            extra['died_country'] = person.died_place['country_code'].upper()
            extra['died_age'] = person.died_age
            extra['gender'] = person.gender
            extra['victim_type'] = person.victim_type
            extra['victim_type_details'] = person.victim_type_details

            if type(person.born_date) is str:
                extra['born_year'] = person.born_date[:4]

            if type(person.died_date) is str:
                extra['died_year'] = person.died_date[:4]

            meta['extra'] = extra

            subtitle = []

            if person.born_date is not None:
                if len(person.born_place['name']):
                    subtitle.append('\u00B0 %d %s' % (person.born_date.year, person.born_place['name']))
                else:
                    subtitle.append('\u00B0 %d' % (person.born_date.year,))

            if person.died_date is not None:
                if len(person.died_place['name']):
                    subtitle.append('\u2020 %d %s' % (person.died_date.year, person.died_place['name']))
                else:
                    subtitle.append('\u2020 %d' % (person.died_date.year,))

            subtitle = ', '.join(subtitle)
            meta['subtitle'] = subtitle

        if notexists('zoom', 'highlight', 'coords_correctionfactor'):
            alto = mh.get_alto(full_pid)
            search_res = alto.search_words([entity.split(' ')])
            extent_textblock = search_res['extent_textblocks']
            extents_highlight = [word['extent'] for word in search_res['words']]

            if search_res['correction_factor'] != 1:
                for word in extents_highlight:
                    word.scale(search_res['correction_factor'], inplace=True)
                extent_textblock.scale(search_res['correction_factor'], inplace=True)

            extent_textblock = extent_textblock.as_coords()
            extents_highlight = [extent.as_coords() for extent in extents_highlight]

            meta["zoom"] = extent_textblock
            meta["highlight"] = extents_highlight
            meta["coords_correctionfactor"] = search_res['correction_factor']

        return meta
