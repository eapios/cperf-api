import pytest
from rest_framework.test import APIClient

from components.models import Component
from cpu.models import CpuComponent
from dram.models import DramComponent


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def cpu_component(db: None) -> Component:
    return CpuComponent.objects.create(
        name="Intel Core i9-14900K",
        description="24-core desktop processor",
        cores=24,
        threads=32,
        clock_speed="3.20",
        boost_clock="6.00",
        tdp=253,
        socket="LGA1700",
    )


@pytest.fixture
def dram_component(db: None) -> Component:
    return DramComponent.objects.create(
        name="G.Skill Trident Z5 RGB",
        description="32GB DDR5-6000 kit",
        capacity_gb=32,
        speed_mhz=6000,
        ddr_type="DDR5",
        modules=2,
        cas_latency=30,
    )
