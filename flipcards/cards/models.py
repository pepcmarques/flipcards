from django.db import models

from flipcards.accounts.models import User


class CardCollection(models.Model):
    # external_id = models.UUIDField(default=uuid.uuid4, editable=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        unique_together = [['owner', 'name']]


class CardTopic(models.Model):
    # external_id = models.UUIDField(default=uuid.uuid4, editable=True)
    collection = models.ForeignKey(CardCollection, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [['collection', 'name']]


class Card(models.Model):
    # external_id = models.UUIDField(default=uuid.uuid4, editable=True)
    topic = models.ForeignKey(CardTopic, on_delete=models.CASCADE)
    front = models.CharField(max_length=50)
    back = models.CharField(max_length=50)

    class Meta:
        unique_together = [['topic', 'front', 'back']]
