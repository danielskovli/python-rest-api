'''Yr weather service interface'''

from fastapi import APIRouter
from .. import BASE_URL
from .... import utils, security, config


router = APIRouter(
    prefix=BASE_URL + '/remote/yr-forecast',
    dependencies=[
        security.qapi_key_dependency(
            required_roles=security.ApiKeyRole.remote
        )
    ]
)


def _get_yr_json(lat: float, lon: float):
    return utils.requests.get_json(
        url=config.RemoteEndpoints.yr_forecast.format(
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