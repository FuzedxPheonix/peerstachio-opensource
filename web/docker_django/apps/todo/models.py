from django.db import models

class Item(models.Model):
    text = models.TextField(blank=False, null=False)
    date_posted = models.DateField(auto_now=True)
    def __str__(self):  # __unicode__ for Python 2
        return "item"