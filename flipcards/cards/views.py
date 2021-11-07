from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render

from flipcards.cards.forms import CollectionForm, CollectionSuperForm, TopicForm, CardForm
from flipcards.cards.models import CardCollection, CardTopic, Card
from flipcards.cards.services import serialize_qs


@login_required()
def add_card(request, col_id=None, top_id=None):
    error = False
    # No id received
    if col_id is None or top_id is None:
        error = True
    # Does this collescion exist?
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True
    # Does this topic exist?
    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        error = True
    # Is this topic under this collection
    if topic.collection != collection:
        error = True
    # Is this the owner?
    if collection.owner != request.user:
        error = True
    #
    if error:
        messages.add_message(request, messages.INFO, "Card couldn't be created under this Topic")
        return handle_dashboard(request, col_id=col_id, top_id=top_id)
    #
    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            # Here I can add another attribute
            card.topic = topic
            card_id = None
            try:
                card.save()
                card_id = card.id
            except IntegrityError:
                messages.add_message(request, messages.INFO, "Card 'front & back' already exists")
            return handle_dashboard(request, col_id=col_id, top_id=top_id, card_id=card_id)
    else:
        form = CardForm()
    return render(request, 'card.html', context={"form": form})


@login_required()
def delete_card(request, col_id=None, top_id=None, card_id=None):
    error = False
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True
    #
    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        error = True
    #
    try:
        card = Card.objects.get(pk=card_id)
    except ObjectDoesNotExist:
        error = True
    #
    if card.topic != topic:
        error = True
    #
    if topic.collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO,
                             "Card doesn't exist or you don't have permission to delete it")
        return handle_dashboard(request, col_id=col_id, top_id=top_id)

    if request.method == 'POST':
        if card.delete():
            messages.add_message(request, messages.INFO, f"Card {card.front}/{card.back} was deleted")
        else:
            messages.add_message(request, messages.ERROR, f"Couldn't delete the card {card.front}/{card.back}")
        return handle_dashboard(request, col_id=col_id, top_id=top_id)

    return render(request, 'delete_card.html', context={"card": card})


@login_required()
def edit_card(request, col_id=None, top_id=None, card_id=None):
    error = False
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True

    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        error = True

    if topic.collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO, "Card doesn't exist or you don't have permission to edit it")
        return handle_dashboard(request, col_id=col_id, top_id=top_id, card_id=card_id)

    form = CardForm(request.POST or None, instance=topic)
    if form.is_valid():
        form.save()
        return handle_dashboard(request, col_id=col_id, top_id=top_id, card_id=card_id)
    return render(request, 'card.html', {'form': form, 'card': card_id})


@login_required()
def add_topic(request, col_id=None):
    error = False

    if col_id is None:
        error = True
    #
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True

    if collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO, "Topic couldn't be created under this Collection")
        return handle_dashboard(request, col_id=col_id)

    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            # Here I can add another attribute
            topic.collection = collection
            try:
                topic.save()
                top_id = topic.id
            except IntegrityError:
                messages.add_message(request, messages.INFO, "Topic name already exists")
                return handle_dashboard(request, col_id=col_id)

            return handle_dashboard(request, col_id=col_id, top_id=top_id)
    else:
        form = TopicForm()
    return render(request, 'topic.html', context={"form": form})


@login_required()
def delete_topic(request, col_id=None, top_id=None):
    error = False
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True
    #
    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        error = True
    #
    if topic.collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO,
                             "Topic doesn't exist or you don't have permission to delete it")
        return handle_dashboard(request, col_id=col_id, top_id=top_id)

    if request.method == 'POST':
        if topic.delete():
            messages.add_message(request, messages.INFO, f"Topic {topic.name} was deleted")
        else:
            messages.add_message(request, messages.ERROR, f"Couldn't delete the topic {topic.name}")
        return handle_dashboard(request, col_id=col_id)

    return render(request, 'delete_topic.html', context={"topic": topic})


@login_required()
def edit_topic(request, col_id=None, top_id=None):
    error = False
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True

    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        error = True

    if not error and topic.collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO, "Topic doesn't exist or you don't have permission to edit it")
        return handle_dashboard(request, col_id=col_id, top_id=top_id)

    form = TopicForm(request.POST or None, instance=topic)
    if form.is_valid():
        form.save()
        return handle_dashboard(request, col_id=col_id, top_id=top_id)
    return render(request, 'topic.html', {'form': form, 'topic': topic})


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
            collection.owner = request.user
            col_id = None
            try:
                collection.save()
                col_id = collection.id
            except IntegrityError:
                messages.add_message(request, messages.INFO, "Collection name already exists")
                return handle_dashboard(request)
            return handle_dashboard(request, col_id=col_id)
    else:
        if request.user.is_superuser:
            form = CollectionSuperForm()
        else:
            form = CollectionForm()
    return render(request, 'collection.html', context={"form": form})


@login_required()
def delete_collection(request, col_id):
    error = False
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True

    if collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO,
                             "Collection doesn't exist or you don't have permission to delete it")
        return handle_dashboard(request, col_id=col_id)

    if request.method == 'POST':
        if collection.delete():
            messages.add_message(request, messages.INFO, f"Collection {collection.name} was deleted")
        else:
            messages.add_message(request, messages.ERROR, f"Couldn't delete the collection {collection.name}")
        return handle_dashboard(request)

    return render(request, 'delete_collection.html', context={"collection": collection})


@login_required()
def edit_collection(request, col_id):
    error = False
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        error = True

    if collection.owner != request.user:
        error = True

    if error:
        messages.add_message(request, messages.INFO, "Collection doesn't exist or you don't have permission to edit it")
        return handle_dashboard(request, col_id=col_id)

    if request.user.is_superuser:
        form = CollectionSuperForm(request.POST or None, instance=collection)
    else:
        form = CollectionForm(request.POST or None, instance=collection)
    if form.is_valid():
        form.save()
        return handle_dashboard(request, col_id=col_id)
    return render(request, 'collection.html', {'form': form, 'collection': collection})


@login_required()
def handle_dashboard(request, col_id=None, top_id=None, card_id=None):
    card_collections = CardCollection.objects.filter(owner=request.user)
    card_topics = CardTopic.objects.filter(collection__in=card_collections)
    cards = Card.objects.filter(topic__in=card_topics)
    #
    try:
        card_collections.get(id=col_id)
    except ObjectDoesNotExist:
        col_id = None
    #
    try:
        card_topics.get(id=top_id)
    except ObjectDoesNotExist:
        top_id = None
    #
    try:
        cards.get(id=card_id)
    except ObjectDoesNotExist:
        card_id = None
    #
    if col_id is None:
        top_id = None
    if top_id is None:
        card_id = None
    #
    return render(request,
                  'dashboard.html',
                  context={"card_collections": serialize_qs(card_collections),
                           "card_topics": serialize_qs(card_topics),
                           "cards": serialize_qs(cards, "front"),
                           "col_id": col_id,
                           "top_id": top_id,
                           "card_id": card_id
                           }
                  )
