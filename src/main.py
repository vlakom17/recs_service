from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.routes import recommend
from src.core.dependencies import setup_dependencies
from src.core.config import cfg
from src.core.logging import LOGGING
import logging
import uvicorn

app = FastAPI(default_response_class=ORJSONResponse)

app.include_router(recommend.router, prefix="")


def start_app(config):
    level = None
    match config.log_level:
        case "info":
            level = logging.INFO
        case "debug":
            level = logging.DEBUG
        case "error":
            level = logging.ERROR

    uvicorn.run(
        "src.main:app",
        host="localhost",
        port=config.port,
        log_config=LOGGING,
        log_level=level,
    )


setup_dependencies(app)

if __name__ == "__main__":
    start_app(cfg)
