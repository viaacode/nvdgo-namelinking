from django.db import models


#from psqlextra.models import PostgresModel

class Link(models.Model):
    UNDEFINED = 0
    MATCH = 1
    NO_MATCH = 2
    UNCERTAIN = 3

    STATUS_CHOICES = (
        (UNDEFINED, 'Not yet determined'),
        (MATCH, 'Match'),
        (NO_MATCH, 'No match'),
        (UNCERTAIN, 'Unknown')
    )

    pid = models.CharField(max_length=26, db_index=True, default='')
    nmlid = models.CharField(max_length=300, default='')
    entity = models.CharField(max_length=300, default='')
    distance = models.PositiveSmallIntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNDEFINED, db_index=True)
    kind = models.CharField(max_length=300, default='')
    extras = models.CharField(max_length=300, default='')

    class Meta:
        unique_together = (("pid", "nmlid"),)
