from django.db import models
from pythonmodules.namenlijst import Namenlijst
from pythonmodules.mediahaven import MediaHaven
from pythonmodules.matcher import Matcher
from pythonmodules.profiling import timeit


class LinkBase(models.Model):
    UNDEFINED = 0
    MATCH = 1
    NO_MATCH = 2
    UNCERTAIN = 3
    SKIP = 4

    STATUS_CHOICES = (
        (UNDEFINED, 'Not yet determined'),
        (MATCH, 'Match'),
        (NO_MATCH, 'No match'),
        (UNCERTAIN, 'Unknown'),
        (SKIP, 'Skip')
    )

    pid = models.CharField(max_length=26, db_index=True, default='')
    nmlid = models.CharField(max_length=300, default='')
    entity = models.CharField(max_length=300, default='')
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNDEFINED, db_index=True)
    kind = models.CharField(max_length=300, default='')
    extras = models.CharField(max_length=300, default='')
    # todo
    # score = models.PositiveIntegerField(default=0)

    @property
    def url(self):
        return 'https://database.namenlijst.be/publicsearch/#/person/_id=%s' % self.nmlid
        # return 'https://database.namenlijst.be/#/person/_id=%s' % self.nmlid

    @property
    def status_class(self):
        return self.status_text.lower().replace(' ', '-')

    @property
    def status_text(self):
        names = next(filter(lambda x: x[0] == self.status, self.STATUS_CHOICES))
        if not len(names):
            return None
        return names[1]

    class Meta:
        unique_together = (("pid", "nmlid"),)
        abstract = True


class Link(LinkBase):
    pass


class LinkNew(LinkBase):
    pass


class LinkKunstenaars(LinkBase):
    @property
    def url(self):
        return None

    pass


class Entities(models.Model):
    doc_index = models.PositiveSmallIntegerField(db_index=True)
    entity = models.CharField(max_length=300, default='', db_index=True)
    entity_type = models.CharField(max_length=1, default='')
    pid = models.CharField(max_length=26, db_index=True)
    entity_full = models.TextField()
    index = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (("doc_index", "index"),)
        # abstract = True


LinkNamenlijst = LinkNew


class Texts(models.Model):
    id = models.IntegerField(primary_key=True)
    pid = models.CharField(max_length=26, db_index=True, default='')
    text = models.TextField()


class Words(models.Model):
    word_hash = models.BigIntegerField(db_index=True)
    texts = models.ForeignKey('Texts', on_delete=models.CASCADE)

    class Meta:
        unique_together = (("word_hash", "texts"),)
