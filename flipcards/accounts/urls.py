from django.urls import path
from django.views.generic import TemplateView

from flipcards.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.sign_in, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('profile/', views.update_user, name='profile'),

    path('users', views.list_users, name='list_users'),
    path('create/', views.create_user, name='create_user'),
    path('update/', views.update_user, name='update_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('forgotten/', views.forgotten_password, name='forgotten'),
    path('forgotten/done/', TemplateView.as_view(template_name='forgotten_password_done.html'),
         name='forgotten_password_done'),
    path('password_change/<int:user_id>/', views.password_change, name='password_change'),
]

"""
accounts/login/ [name='login']
accounts/logout/ [name='logout']
accounts/password_change/ [name='password_change']
accounts/password_change/done/ [name='password_change_done']
accounts/password_reset/ [name='password_reset']
accounts/password_reset/done/ [name='password_reset_done']
accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/reset/done/ [name='password_reset_complete']
"""
