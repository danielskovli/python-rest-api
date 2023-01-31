'''Just grab a random Wikipedia article'''

from fastapi import APIRouter

from .. import BASE_URL
from ....utils import requests
from ....config import RemoteEndpoints
from ....middleware.route_handlers import InterceptDbErrorRoute


router = APIRouter(
    prefix=BASE_URL + '/remote/yr-forecast',
    route_class=InterceptDbErrorRoute
)


def _get_yr_json(lat: float, lon: float):
    return requests.get_json(
        url=RemoteEndpoints.yr_forecast.format(
            lat=lat,
            lon=lon
        ),

        # NOTE: Workaround for a slightly over-zealous user agent check at Yr
        fallback_plaintext=True,
        user_agent=None
    )


@router.get("/")
async def get_forecast(lat: float, lon: float):
    return _get_yr_json(lat, lon)


@router.get("/oslo")
async def get_forecast_oslo():
    return _get_yr_json(59.9, 10.8)


@router.get("/sogndal")
async def get_forecast_signdal():
    return _get_yr_json(61.23, 7.1)