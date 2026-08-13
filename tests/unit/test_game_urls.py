import pytest
from django.urls import Resolver404, resolve


@pytest.mark.django_db
def test_development_tester_endpoint_is_not_exposed(client):
    with pytest.raises(Resolver404):
        resolve("/tester/")

    response = client.get("/tester/")

    assert response.status_code == 404
