import uuid

from django.db import models

from flipcards.accounts.models import User


class CardCollection(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False, blank=True, null=True)


class CardTopic(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(CardCollection, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField()


class Card(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(CardTopic, on_delete=models.CASCADE)
    front = models.CharField(max_length=50)
    back = models.CharField(max_length=50)
