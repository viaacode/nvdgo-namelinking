from django.db import models


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

    def url(self):
        return 'https://database.namenlijst.be/#/person/_id=%s' % self.nmlid

    class Meta:
        unique_together = (("pid", "nmlid"),)
        abstract = True


class Link(LinkBase):
    pass


class LinkNew(LinkBase):
    pass


class LinkKunstenaars(LinkBase):
    def url(self):
        return None

    pass


class Entities(models.Model):
    _id = models.PositiveSmallIntegerField(db_index=True)
    entity = models.CharField(max_length=300, default='', db_index=True)
    entity_type = models.CharField(max_length=1, default='')
    pid = models.CharField(max_length=26, db_index=True)
    entity_full = models.TextField()
    index = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (("id", "index"),)
        # abstract = True


LinkNamenlijst = Link
