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
import numpy as np


def get_cacher(name):
    from django.core.cache import caches
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


import matplotlib
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

    def get_cacher(self):
        return self._cacher

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
            return NotImplementedError
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
        q = 'SELECT meta, status, score FROM %s WHERE status != %d AND score > 0' % \
            (self.table, self.model.SKIP)
        res = self.db.execute(q)
        data = []
        data_fields = []
        for row in res:
            meta = json.loads(row[0])
            extra = meta['extra']
            status = self.model.status_id_to_text(row[1])
            extra['status'] = status
            extra['score'] = min(row[2] * 100, 100)
            try:
                extra['died_age'] = int(extra['died_age'])
            except (ValueError, TypeError):
                extra['died_age'] = None

            if type(extra['died_age']) is not int:
                extra['died_age'] = None
            data.append(extra)

            for k, v in meta['rating_breakdown'].items():
                data_fields.append(dict(field=k, status=status, score=min(v*100, 100), amount=1))

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
        logger.info(stats)

        fig = plt.figure(figsize=(9, 4))
        ax = fig.gca()
        ax = sns.countplot(data=stats['ratings'], y="field", order=stats['ratings'].field.value_counts().index,
                           figure=fig, ax=ax)
        ax.set_title('Data used to calculate ratings')
        return fig

    def scores_kde1(self, lim=None):
        if lim is None:
            lim = (0, 10)
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

        ax.set_xlabel('score (in %)')
        ax.set_ylabel('Kernel density')
        ax.set_title('scores distribution and kernel density')
        fig.subplots_adjust(bottom=0.15)
        # plt.xlim(*lim)
        return fig

    def scores_kde2(self):
        return self.scores_kde1((10, 50))

    def scores_kde3(self):
        return self.scores_kde1((50, 100))

    def scores_status_impact(self):
        stats = self._usersegmentations()
        stats = stats['ratings']
        stats = stats[stats.status != self.model.status_id_to_text(self.model.UNDEFINED)]

        fig = plt.figure(figsize=(6, 9))
        ax = fig.gca()
        ax = sns.swarmplot(data=stats, x='score', y='field', hue='status', figure=fig, ax=ax, size=3)
        ax.set_title('Partial scores per field\n(for manually attested items)')
        fig.subplots_adjust(left=0.25)
        return fig

    def scores_field_impact(self):
        stats = self._usersegmentations()

        fig = plt.figure(figsize=(6, 9))
        ax = fig.gca()
        ax = sns.boxplot(data=stats['ratings'], y='score', x='field', ax=ax)
        ax.set_title('Partial scores per field')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
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
        order = getattr(stats, kind).value_counts().index if sort else None
        ax = sns.countplot(data=stats, y=kind, order=order,
                           figure=fig, ax=ax)
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
        ax.set_title('Died age distribution\n(%d/%s with no valid age)' % (totlen-newlen,totlen))
        return fig



