from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from . import table_models_optional
from .database import engine, get_db
from . import tables
from .database_model import Database as db
from . import oauth2
from .database_connection import conn
from . import user_permissions
from .schemas import offers as offers_schemas
from .schemas import users as users_schemas


from .routers import (
    companies,
    company_connections,
    prices,
    offer_body,
    projects,
    users,
    offers,
    auth,
)

from . import table_models_required


# class Offer(BaseModel):

db = db(conn)

table_models_required.Base.metadata.create_all(bind=engine)


offers_table = "offers"


app = FastAPI()

app.include_router(projects.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(offer_body.router)
app.include_router(offers.router)
app.include_router(auth.router)
app.include_router(prices.router)
app.include_router(company_connections.router)


@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}
