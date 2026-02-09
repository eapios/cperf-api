import pytest
from rest_framework.test import APIClient

from sample.models import SampleItem


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def sample_item(db: None) -> SampleItem:
    return SampleItem.objects.create(
        name="Test Item",
        description="A test item for fixtures",
    )
