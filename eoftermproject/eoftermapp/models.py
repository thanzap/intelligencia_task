from django.db import models
from django.contrib.postgres.fields import ArrayField


class EFOterm(models.Model):
    efo_term_id = models.CharField(max_length=1000, unique=True)
    term_name = models.CharField(max_length=1000)
    synonyms = ArrayField(models.CharField(max_length=1000), null=True, blank=True)

    class Meta:
        verbose_name = "EFO Term"
        verbose_name_plural = "EFO Terms"

class ParentRelationship(models.Model):
    term = models.ForeignKey(EFOterm, on_delete=models.CASCADE, related_name='parent_relations')
    parent = models.ForeignKey(EFOterm, on_delete=models.CASCADE, related_name='child_relations')