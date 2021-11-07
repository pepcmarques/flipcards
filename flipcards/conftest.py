import pytest
from model_bakery import baker


@pytest.fixture
def user(db, django_user_model):
    model_user = baker.make(django_user_model, email="circularis@email.com", first_name="Circularis")
    password = 'any_password'
    model_user.set_password(password)
    model_user.save()
    model_user.plain_password = password
    return model_user


@pytest.fixture
def logged_user_client(user, client):
    client.force_login(user)
    return client
