from __future__ import annotations

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from gateway.api.schemas import DispatchRequest, DispatchResponse
from gateway.config.settings import settings
from gateway.core.bootstrap import seed_routes
from gateway.core.dispatcher import Dispatcher
from gateway.storage.db import Base, engine, get_db


app = FastAPI(title=settings.app_name, debug=settings.app_debug)
dispatcher = Dispatcher()


@app.on_event('startup')
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_routes(db)


@app.get('/healthz')
def healthz(db: Session = Depends(get_db)) -> dict:
    db.execute(text('SELECT 1'))
    return {'ok': True}


@app.post('/v1/dispatch', response_model=DispatchResponse)
async def dispatch(request: DispatchRequest, db: Session = Depends(get_db)) -> DispatchResponse:
    return await dispatcher.dispatch(db, request)
