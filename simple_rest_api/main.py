'''simple-rest-api main entry -> all global inits go here'''


from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi

from .version import __version__, __description__, __title__
from . import config
from .routers.v1 import status


# Main app entry
app = FastAPI(
    title=__title__,
    version=__version__,
    description=__description__
)

# Include all routers
app.include_router(status.router)

# Default root
@app.get('/')
async def root():
    return app.openapi()['info']