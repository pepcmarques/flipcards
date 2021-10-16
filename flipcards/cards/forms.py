from django.forms import ModelForm

from flipcards.cards.models import CardCollection, CardTopic


class CollectionForm(ModelForm):
    class Meta:
        model = CardCollection
        fields = ['name', 'description']


class CollectionSuperForm(ModelForm):
    class Meta:
        model = CardCollection
        fields = ['name', 'is_public', 'description']


class TopicForm(ModelForm):
    class Meta:
        model = CardTopic
        fields = ['name', 'description']
