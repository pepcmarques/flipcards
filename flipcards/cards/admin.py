from django.contrib import admin

from flipcards.cards.models import CardCollection, CardTopic, Card

admin.site.register(CardCollection)
admin.site.register(CardTopic)
admin.site.register(Card)
