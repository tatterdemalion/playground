from django.db import models


class Entry(models.Model):
    title = models.CharField(max_length=512, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return self.title


class Attachment(models.Model):
    uploaded = models.FileField(upload_to='attachment')
    question = models.ForeignKey("qa.Entry")

    def __unicode__(self):
        return self.uploaded.url
