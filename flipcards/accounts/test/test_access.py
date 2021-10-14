import pytest
from django.urls import reverse


@pytest.mark.parametrize("url,ret", [(reverse("accounts:login"), 200),
                                     (reverse("accounts:signup"), 200),
                                     ("/any/", 404)])
def test_status_code_user_not_lagged(client, url, ret):
    resp = client.get(url)
    assert resp.status_code == ret


@pytest.mark.parametrize("url,ret", [(reverse("accounts:login"), 302),
                                     (reverse("accounts:signup"), 200),
                                     ("/any/", 404)])
def test_status_code_user_lagged(logged_user_client, url, ret):
    resp = logged_user_client.get(url)
    assert resp.status_code == ret
