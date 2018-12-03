from django.db.models import Count
from django.http.response import HttpResponse
from io import BytesIO
from collections import OrderedDict
from pythonmodules.config import Config
import pandas as pd
from pythonmodules.db import DB
import seaborn as sns
import logging
import json
from . import models
import pythonmodules.decorators as decorators
from django.core.cache.backends.base import InvalidCacheBackendError
from pythonmodules.cache import WrapperCacher
import matplotlib


def get_cacher(name):
    from django.core.cache import caches
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


matplotlib.use('Agg')
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)


class Stats:
    format_to_type = {
        "svg": "image/svg+xml",
        "png": "image/png",
        "jpg": "image/jpeg",
    }

    def __init__(self, model=None):
        if model is None:
            model = models.Link
        self.model = model
        self.db = DB(Config(section='db')['connection_url'])
        self.table = model._meta.db_table
        self._cacher = WrapperCacher(get_cacher('stats'))
        sns.set(font_scale=.8)

    @staticmethod
    def ticklabels_to_pct(ax, axis=None, precision=2, factor=100):
        if axis is None:
            axis = 'x'
        ticks = [('%.'+str(precision)+'f%%') % (tick*factor,) for tick in getattr(ax, 'get_%sticks' % axis)()]
        getattr(ax, 'set_%sticklabels' % axis)(ticks)

    @staticmethod
    def ticklabels_add_pct(ax, value_counts, axis=None, precision=2, factor=100, total=None):
        if axis is None:
            axis = 'x'

        if total is None:
            total = sum(value_counts)
        ticklabels = getattr(ax, 'get_%sticklabels' % axis)()
        ticks = getattr(ax, 'get_%sticks' % axis)()
        sep = '\n' if len(ticklabels) < 5 or axis == 'x' else ' '

        for i, txt in enumerate(ticklabels):
            txt_str = txt.get_text()
            if txt_str not in value_counts:
                val = ticks[i]
                txt_str = '%.0f' % (ticks[i],)
            else:
                val = value_counts[txt_str]
            # if txt_str == '':
            #     txt_str = str(ticks[i])
            txt_str = ('%s%s(%.' + str(precision) + 'f%%)') % (txt_str, sep, val / total * factor)
            txt.set_text(txt_str)

        getattr(ax, 'set_%sticklabels' % axis)(ticklabels)

    def get_cacher(self):
        return self._cacher

    @decorators.classcache
    def _stats_matches(self):
        fields = ('COUNT(DISTINCT pid)', 'COUNT(DISTINCT nmlid)', 'SUM(CEIL(score))', 'COUNT(*)', 'SUM(score)')
        fieldnames = ('Amount of newspaper pages with matches', 'Amount of IFFM names with matches',
                      'Amount of matches with a score > 0', 'Total amount of matches',
                      'Average score',
                      '% of matches with score > 0')
        res = self.db.execute('SELECT %s FROM %s' % (', '.join(fields), self.table))
        res = list(map(int, res.fetchone()))
        res[-1] = '%.2f%%' % (res[-1]/res[2] * 100)
        res.append('%.2f%%' % (res[2]/res[3] * 100,))
        return OrderedDict(zip(fieldnames, res))

    def _stats_attestation(self):
        model = self.model
        data = model.objects.all().values('status').annotate(total=Count('status'))
        data = [p for p in data if p['status'] not in [model.SKIP]]
        x = [[l[1] for l in model.STATUS_CHOICES if l[0] == p['status']][0] for p in data]
        y = [p['total'] for p in data]
        return dict(zip(x, y))

    def _output(self, kind, format_=None):
        if not hasattr(self, kind):
            raise NotImplementedError()
        fig = getattr(self, kind)()
        return self._get_plt_response(format_, fig)

    def _get_plt_response(self, format_=None, fig=None):
        cls = type(self)
        if format_ is None:
            format_ = 'svg'
        content_type = cls.format_to_type[format_] if format_ in cls.format_to_type else ('image/%s' % (format_,))
        io = BytesIO()

        fig.savefig(io, format=format_)
        # fig.clf()
        plt.close(fig=fig)
        return HttpResponse(io.getvalue(), content_type=content_type)

    @decorators.classcache
    def _usersegmentations(self):
        fields = ('meta', 'nmlid', 'status', 'score')
        q = 'SELECT %s FROM %s WHERE status != %d AND score > 0' % \
            (', '.join(fields), self.table, self.model.SKIP)
        res = self.db.execute(q)
        data = []
        data_fields = []
        for row in res:
            row = dict(zip(fields, row))
            meta = json.loads(row['meta'])
            extra = meta['extra']
            status = self.model.status_id_to_text(row['status'])
            extra['status'] = status
            extra['score'] = min(row['score'], 1)
            extra['name'] = meta['name']
            extra['subtitle'] = meta['subtitle']
            extra['pid'] = meta['full_pid']
            splitpid = extra['pid'].split('_')
            extra['nmlid'] = row['nmlid']
            extra['url'] = 'https://hetarchief.be/pid/%s/%d' % (splitpid[0], int(splitpid[2]))
            extra['nmlurl'] = 'https://database.namenlijst.be/#/person/_id=%s' % extra['nmlid']
            try:
                extra['died_age'] = int(extra['died_age'])
            except (ValueError, TypeError):
                extra['died_age'] = None

            if type(extra['died_age']) is not int:
                extra['died_age'] = None

            data.append(extra)

            for k, v in meta['rating_breakdown'].items():
                data_fields.append(dict(field=k, status=status, score=min(v, 1), amount=1))

        extra = pd.DataFrame.from_dict(data)
        ratings = pd.DataFrame.from_dict(data_fields)
        return dict(extra=extra, ratings=ratings)

    def attestationcounts(self):
        stats = self._stats_attestation()
        undef_title = self.model.status_id_to_text(self.model.UNDEFINED)
        notdone_count = stats[undef_title]
        del stats[undef_title]
        x = stats.keys()
        y = stats.values()

        fig = plt.figure(figsize=(4, 6))
        ax = fig.gca()
        ax.bar(x, y, label='amount')
        ax.set_title('Attestation counts\n(%d not yet manually attested)' % notdone_count)
        ax.legend()
        return fig

    def scores_data_counts(self):
        stats = self._usersegmentations()

        fig = plt.figure(figsize=(9, 4))
        ax = fig.gca()
        value_counts = stats['ratings'].field.value_counts()
        ax = sns.countplot(data=stats['ratings'], y="field", order=value_counts.index,
                           figure=fig, ax=ax)
        ax.set_title('Data used to calculate ratings')
        fig.subplots_adjust(left=0.20, bottom=0.15)
        return fig

    def scores_kde1(self, lim=None):
        if lim is None:
            lim = (0, .10)
        stats = self._usersegmentations()
        scores = stats['extra'].score
        scores = scores[(scores > lim[0]) & (scores <= lim[1])]

        fig = plt.figure(figsize=(6, 3))
        ax = fig.gca()
        # ax = sns.kdeplot(scores, shade=True, legend=True)
        # plt.xlim(*lim)
        ax.set_xlim(*lim)
        ax = sns.kdeplot(scores, shade=True, ax=ax)

        sns.distplot(scores, bins=10, ax=ax)
        # plt.xlim(*lim)

        ax.set_xlabel('score')
        ax.set_ylabel('Kernel density')
        ax.set_title('scores distribution and kernel density')
        self.ticklabels_to_pct(ax, 'x')
        self.ticklabels_to_pct(ax, 'y', precision=0, factor=1)
        fig.subplots_adjust(bottom=0.15)
        # plt.xlim(*lim)
        return fig

    def scores_kde2(self):
        return self.scores_kde1((.10, .50))

    def scores_kde3(self):
        return self.scores_kde1((.50, 1))

    def scores_status_impact(self):
        stats = self._usersegmentations()
        stats = stats['ratings']
        stats = stats[stats.status != self.model.status_id_to_text(self.model.UNDEFINED)]

        fig = plt.figure(figsize=(6, 9))
        ax = fig.gca()
        ax = sns.swarmplot(data=stats, x='score', y='field', hue='status', figure=fig, ax=ax, size=3)
        ax.set_title('Partial scores per field\n(for manually attested items)')
        self.ticklabels_to_pct(ax, 'x', precision=0)
        fig.subplots_adjust(left=0.25, bottom=0.09, top=0.9)
        return fig

    def scores_field_impact(self):
        stats = self._usersegmentations()

        fig = plt.figure(figsize=(6, 9))
        ax = fig.gca()
        ax = sns.boxplot(data=stats['ratings'], y='score', x='field', ax=ax)
        ax.set_title('Partial scores per field')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        self.ticklabels_to_pct(ax, 'y')
        fig.subplots_adjust(bottom=0.25, top=0.95)
        return fig

    def _segmentations(self, kind=None, sort=None):
        if sort is None:
            sort = True

        if kind is None:
            kind = 'born_country'

        stats = self._usersegmentations()
        stats = stats['extra']

        fig = plt.figure(figsize=(9, 4))
        ax = fig.gca()
        value_counts = getattr(stats, kind).value_counts()
        order = value_counts.index if sort else None
        ax = sns.countplot(data=stats, y=kind, order=order,
                           figure=fig, ax=ax)
        self.ticklabels_add_pct(ax, value_counts, 'y')
        self.ticklabels_add_pct(ax, value_counts, 'x', precision=1)
        fig.subplots_adjust(left=0.15, bottom=0.17)
        ax.set_title('Segmented per %s' % kind)
        return fig

    def segment_died_country(self):
        return self._segmentations('died_country')

    def segment_gender(self):
        return self._segmentations('gender')

    def segment_victim_type(self):
        return self._segmentations('victim_type')

    def segment_victim_type_details(self):
        return self._segmentations('victim_type_details')

    def segment_born_country(self):
        return self._segmentations('born_country')

    def segment_died_age(self):
        stats = self._usersegmentations()
        stats = stats['extra']
        totlen = len(stats)
        stats = stats[(~stats['died_age'].isnull()) & (stats['died_age'] < 200)]
        newlen = len(stats)
        # stats.loc[stats.died_age is]

        fig = plt.figure(figsize=(9, 4))
        ax = fig.gca()

        ax.set_xlim((0, stats.died_age.max()))
        ax = sns.distplot(stats.died_age, hist=True, kde=True, ax=ax)
        self.ticklabels_to_pct(ax, 'y')
        ax.set_title('Died age distribution\n(%d/%s with no valid age)' % (totlen - newlen, totlen))
        return fig

    def swarm_scores_status(self, kind=None):
        if kind is None:
            kind = 'swarm'
        kind = '%splot' % (kind,)
        stats = self._usersegmentations()
        stats = stats['ratings']
        stats = stats[stats.status != self.model.status_id_to_text(self.model.UNDEFINED)]

        fig = plt.figure(figsize=(5, 6))
        ax = fig.gca()
        # ax = sns.violinplot(data=stats, y='score', x='status', ax=ax) # size=2
        ax = getattr(sns, kind)(data=stats, y='score', x='status', ax=ax, size=2)
        ax.set_title('Scores per status')
        self.ticklabels_to_pct(ax, axis='y', precision=0)
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        # self.ticklabels_to_pct(ax, 'y')
        fig.subplots_adjust(top=0.95, left=0.20)
        return fig

    def violin_scores_status(self):
        return self.swarm_scores_status('violin')

    def _highest_scores(self):
        stats = self._usersegmentations()
        nomatch = self.model.status_id_to_text(self.model.NO_MATCH)
        stats = stats['extra']
        stats = stats[stats.status != nomatch]
        return stats.nlargest(20, columns='score')

    def _young_deaths(self):
        stats = self._usersegmentations()
        stats = stats['extra']
        nomatch = self.model.status_id_to_text(self.model.NO_MATCH)
        stats = stats[stats.status != nomatch]
        stats = stats[stats.score > 0]
        stats = stats[stats.died_age.notnull()]
        stats = stats[stats.died_age <= 8]
        return stats.nlargest(10, columns='score')

    def _old_deaths(self):
        stats = self._usersegmentations()
        stats = stats['extra']
        nomatch = self.model.status_id_to_text(self.model.NO_MATCH)
        stats = stats[stats.status != nomatch]
        stats = stats[stats.score > 0]
        stats = stats[stats.died_age.notnull()]
        stats = stats[stats.died_age > 75]
        return stats.nlargest(10, columns='score')

    def _segmented_deaths(self, segment):
        stats = self._usersegmentations()
        stats = stats['extra']
        nomatch = self.model.status_id_to_text(self.model.NO_MATCH)
        stats = stats[stats.status != nomatch]
        stats = stats[stats.score > 0]
        # stats = stats[stats[segment].notnull()]
        stats = stats.sort_values('score', ascending=False).groupby(segment)
        amount = 1 if len(stats) > 8 else 3
        return stats.head(amount)

