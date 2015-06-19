from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    IDENTIFIERS = (
        (1, 'isbn13'),
        (2, 'isbn10'),
        (3, 'sallamasyon'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=60, unique=True)
    identifier_type = models.IntegerField(choices=IDENTIFIERS)
    identifier = models.CharField(max_length=13)
    author = models.ManyToManyField('Author')

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('identifier', 'identifier_type')
