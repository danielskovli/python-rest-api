'''simple-rest-api main entry -> all global inits go here'''

from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi

from . import config, security, utils
from .version import __version__, __description__, __title__
from .routers.v1 import status, pizza


# Populate some sample db-data
print('Creating db tables')
utils.init_db.create_tables()

print('Populating sample data')
utils.init_db.populate_demo_data()


# Main app entry
app = FastAPI(
    title=__title__,
    version=__version__,
    description=__description__,
    dependencies=[
        Depends(security.ApiKeyAuthScheme())
    ]
)


# Include all routers
app.include_router(status.router, tags=[config.Tags.misc])
app.include_router(pizza.main.router, tags=[config.Tags.pizza])
app.include_router(pizza.rating.router, tags=[config.Tags.pizza])


# Default root
@app.get('/', tags=[config.Tags.misc])
async def info():
    return app.openapi()['info']


# Error handling for non-prod environments
if not config.Environment.is_prod_server:
    @app.exception_handler(Exception) # type: ignore
    async def debug_exception_handler(request: Request, exc: Exception):
        import traceback

        return Response(
            content=''.join(
                traceback.format_exception(
                    type(exc), exc, exc.__traceback__
                )
            ),
            status_code=500 # NOTE: This is not necessarily correct, but serves our purpose for now
        )


# Custom OpenApi implementation. Merge the new app name+key security scheme pairings
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=__title__,
        version=__version__,
        description=__description__,
        routes=app.routes,
    )

    for path in openapi_schema.get("paths", []):
        for http_method in openapi_schema["paths"][path]:
            securities = openapi_schema["paths"][path][http_method].get("security")
            if securities:
                merged = security.merge_securities(securities)
                openapi_schema["paths"][path][http_method]["security"] = merged

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi