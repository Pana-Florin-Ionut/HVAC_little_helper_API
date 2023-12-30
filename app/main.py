from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
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
    products,
)

from . import table_models_required
from fastapi.middleware.cors import CORSMiddleware

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    # "http://http://localhost:5173",
    "http://localhost:5173/",
    "http://localhost:5173",
    "http://localhost:5173/login",
    "http://localhost:4173",
]


table_models_required.Base.metadata.create_all(bind=engine)


# offers_table = "offers"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(offer_body.router)
app.include_router(offers.router)
app.include_router(auth.router)
app.include_router(prices.router)
app.include_router(company_connections.router)
app.include_router(products.router)


@app.get("/")
def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}
