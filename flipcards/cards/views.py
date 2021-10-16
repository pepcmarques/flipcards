from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from flipcards.cards.forms import CollectionForm, CollectionSuperForm, TopicForm
from flipcards.cards.models import CardCollection, CardTopic, Card
from flipcards.cards.services import serialize_qs


def get_obj_collection(request, external_id):
    try:
        collection = CardCollection.objects.get(external_id=external_id)
    except CardCollection.DoesNotExist:
        messages.add_message(request, messages.INFO, "Couldn't find collection")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    return collection


@login_required()
def add_topic(request, col_id=None):
    if col_id is None:
        messages.add_message(request, messages.INFO, "Topic couldn't be created under this Collection")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    #
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Topic couldn't be created under this Collection")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if collection.owner != request.user:
        messages.add_message(request, messages.INFO, "Topic couldn't be created under this Collection")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            # Here I can add another attribute
            topic.collection = collection
            try:
                topic.save()
            except IntegrityError as e:
                messages.add_message(request, messages.INFO, "Topic name already exists")
            return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    else:
        form = TopicForm()
    return render(request, 'topic.html', context={"form": form})


@login_required()
def delete_topic(request, col_id=None, top_id=None):
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO,
                             "Topic doesn't exist or you don't have permission to delete it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    #
    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO,
                             "Topic doesn't exist or you don't have permission to delete it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    #
    if topic.collection.owner != request.user:
        messages.add_message(request, messages.INFO,
                             "Topic doesn't exist or you don't have permission to delete it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if request.method == 'POST':
        if topic.delete():
            messages.add_message(request, messages.INFO, f"Topic {topic.name} was deleted")
        else:
            messages.add_message(request, messages.ERROR, f"Couldn't delete the topic {topic.name}")
        return redirect(reverse('cards:handle_dashboard'))

    return render(request, 'delete_topic.html', context={"topic": topic})


@login_required()
def edit_topic(request, col_id=None, top_id=None):
    try:
        CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Topic doesn't exist or you don't have permission to edit it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    try:
        topic = CardTopic.objects.get(pk=top_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Topic doesn't exist or you don't have permission to edit it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if topic.collection.owner != request.user:
        messages.add_message(request, messages.INFO, "Topic doesn't exist or you don't have permission to edit it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    form = TopicForm(request.POST or None, instance=topic)
    if form.is_valid():
        form.save()
        return redirect(reverse('cards:handle_dashboard'))
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
            try:
                collection.save()
            except IntegrityError as e:
                messages.add_message(request, messages.INFO, "Collection name already exists")
                return HttpResponseRedirect(reverse('cards:handle_dashboard'))
            return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    else:
        if request.user.is_superuser:
            form = CollectionSuperForm()
        else:
            form = CollectionForm()
    return render(request, 'collection.html', context={"form": form})


@login_required()
def delete_collection(request, col_id):
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO,
                             "Collection doesn't exist or you don't have permission to delete it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    if collection.owner != request.user:
        messages.add_message(request, messages.INFO,
                             "Collection doesn't exist or you don't have permission to delete it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if request.method == 'POST':
        if collection.delete():
            messages.add_message(request, messages.INFO, f"Collection {collection.name} was deleted")
        else:
            messages.add_message(request, messages.ERROR, f"Couldn't delete the collection {collection.name}")
        return redirect(reverse('cards:handle_dashboard'))

    return render(request, 'delete_collection.html', context={"collection": collection})


@login_required()
def edit_collection(request, col_id):
    try:
        collection = CardCollection.objects.get(pk=col_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Collection doesn't exist or you don't have permission to edit it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))
    if collection.owner != request.user:
        messages.add_message(request, messages.INFO, "Collection doesn't exist or you don't have permission to edit it")
        return HttpResponseRedirect(reverse('cards:handle_dashboard'))

    if request.user.is_superuser:
        form = CollectionSuperForm(request.POST or None, instance=collection)
    else:
        form = CollectionForm(request.POST or None, instance=collection)
    if form.is_valid():
        form.save()
        return redirect(reverse('cards:handle_dashboard'))
    return render(request, 'collection.html', {'form': form, 'collection': collection})


@login_required()
def handle_dashboard(request):
    card_collections = CardCollection.objects.filter(owner=request.user)
    card_topics = CardTopic.objects.filter(collection__in=card_collections)
    cards = Card.objects.filter(topic__in=card_topics)
    #
    print(request.method)
    print(request.GET)
    collection_id = request.GET.get("collection_id", None)
    topic_id = request.GET.get("topic_id", None)
    #
    print(f"Collection = {collection_id}\nTopic = {topic_id}")
    return render(request,
                  'dashboard.html',
                  context={"card_collections": serialize_qs(card_collections),
                           "card_topics": serialize_qs(card_topics),
                           "cards": serialize_qs(cards)
                           }
                  )


