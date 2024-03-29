"""flipcards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from flipcards.cards import views

app_name = 'cards'

urlpatterns = [
    path('dashboard/', views.handle_dashboard, name="handle_dashboard"),
    path('collection/new/', views.add_collection, name="add_collection"),
    path('collection/<int:col_id>/change/', views.edit_collection, name="edit_collection"),
    path('collection/<int:col_id>/delete/', views.delete_collection, name="delete_collection"),
    #
    path('collection/<int:col_id>/topic/new/', views.add_topic, name="add_topic"),
    path('collection/<int:col_id>/topic/<int:top_id>/change/', views.edit_topic, name="edit_topic"),
    path('collection/<int:col_id>/topic/<int:top_id>/delete/', views.delete_topic, name="delete_topic"),
    #
    path('collection/<int:col_id>/topic/<int:top_id>/card/new/', views.add_card, name="add_card"),
    path('collection/<int:col_id>/topic/<int:top_id>/card/<int:card_id>/change/', views.edit_card, name="edit_topic"),
    path('collection/<int:col_id>/topic/<int:top_id>/card/<int:card_id>/delete/', views.delete_card,
         name="delete_topic"),
]
