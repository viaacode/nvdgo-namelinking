from django.db import models


class Link(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    article_id = models.CharField(max_length=50)
    entity = models.CharField(max_length=300)
    article_date = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)
    nmlid = models.CharField(max_length=300)
    status = models.CharField(max_length=3)
    kind = models.CharField(max_length=300)
    extras = models.CharField(max_length=300)
