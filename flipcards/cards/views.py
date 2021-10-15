from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.forms.models import model_to_dict

from flipcards.accounts.models import User
from flipcards.cards.forms import CollectionForm, CollectionSuperForm
from flipcards.cards.models import CardCollection, CardTopic, Card


def get_obj_collection(request, external_id):
    # return CardCollection(id=1, name="Colecao 1", is_public=True, description="Minha colecao", owner=request.user)
    try:
        collection = CardCollection.objects.get(external_id=external_id)
    except CardCollection.DoesNotExist:
        messages.add_message(request, messages.INFO, "Couldn't find collection")
        return reverse('cards:handle_dashboard')
    return collection


def create_collection(request):
    pass


def edit_collection(request, collection):
    pass


def serialize_qs(qs):
    return [model_to_dict(item) for item in qs]


def list_collections(request):
    card_collections = CardCollection.objects.filter(owner=request.user)
    card_topics = CardTopic.objects.filter(collection__in=card_collections)
    cards = Card.objects.filter(topic__in=card_topics)
    #
    """
    c1 = CardCollection(id=1, name="Colecao 1", is_public=True, description="Minha colecao 1", owner=request.user)
    c2 = CardCollection(id=2, name="Colecao 2", is_public=True, description="Minha colecao 2", owner=request.user)

    t1 = CardTopic(id=1, name="Topic 1", description="Meu Topic 1", collection=c1)
    t2 = CardTopic(id=2, name="Topic 2", description="Meu Topic 2", collection=c1)
    t3 = CardTopic(id=3, name="Topic 3", description="Meu Topic 3", collection=c1)
    t4 = CardTopic(id=4, name="Topic 4", description="Meu Topic 4", collection=c2)

    k1 = Card(id=1, front="Card 1", back="Minha cards 1", topic=t1)
    k2 = Card(id=2, front="Card 2", back="Minha cards 2", topic=t1)
    k3 = Card(id=3, front="Card 3", back="Minha cards 3", topic=t3)
    k4 = Card(id=4, front="Front 4-1", back="Back 4-1", topic=t4)
    k5 = Card(id=5, front="Front 4-2", back="Back 4-2", topic=t4)
    k6 = Card(id=6, front="Front 4-3", back="Back 4-3", topic=t4)
    k7 = Card(id=7, front="Front 4-4", back="Back 4-4", topic=t4)

    card_collections = [model_to_dict(c1), model_to_dict(c2)]
    card_topics = [model_to_dict(t1), model_to_dict(t2), model_to_dict(t3), model_to_dict(t4)]
    cards = [model_to_dict(k1),
             model_to_dict(k2),
             model_to_dict(k3),
             model_to_dict(k4),
             model_to_dict(k5),
             model_to_dict(k6),
             model_to_dict(k7)]
    #
    if card_collections:
        card_topics = CardTopic.objects.filter(collection=card_collections[0])
        if card_topics:
            cards = Card.objects.filter(topic=card_topics[0])
    """

    return render(request,
                  'dashboard.html',
                  context={"card_collections": serialize_qs(card_collections),
                           "card_topics": serialize_qs(card_topics),
                           "cards": serialize_qs(cards)
                           }
                  )


def get_collection(request, external_id):
    if external_id:
        collection = get_obj_collection(request, external_id)
        template = ''
        context = ''
        return HttpResponseRedirect(request, template, context)
    return list_collections(request)


@login_required()
def handle_dashboard(request, external_id=None):
    if request.method == "GET":
        return get_collection(request, external_id)
    elif request.method == "POST":
        return create_collection(request, external_id)
    elif request.method == "PUT":
        return edit_collection(request, external_id)
    return reverse('myapp:home')


@login_required()
def add_collection(request):
    if request.method == "POST":
        if request.user.is_superuser:
            form = CollectionSuperForm(request.POST)
        else:
            form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            # Here I can add another attribute
            # user = User.objects.get(pk=request.user)
            collection.owner = request.user
            collection.save()
            return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    else:
        if request.user.is_superuser:
            form = CollectionSuperForm()
        else:
            form = CollectionForm()
    return render(request, 'collection.html', context={"form": form})
