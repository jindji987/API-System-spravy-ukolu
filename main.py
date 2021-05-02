from fastapi import FastAPI
import databases, sqlalchemy
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "postgresql://postgres:605341@127.0.0.1:5432/dbtest"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

ukoly = sqlalchemy.Table(
    "Ukoly",
    metadata,
    sqlalchemy.Column("id"                 , sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("Datum_Vytvoreni"    , sqlalchemy.DateTime),
    sqlalchemy.Column("Datum_Splneni"      , sqlalchemy.DateTime),
    sqlalchemy.Column("Nazev_Ukolu"        , sqlalchemy.String),
    sqlalchemy.Column("Popis_Ukolu"        , sqlalchemy.String),

)

tagy = sqlalchemy.Table(
    "Tagy",
    metadata,
    sqlalchemy.Column("id"                 , sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("Nazev"              , sqlalchemy.String),
)





engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

class SeznamUkolu(BaseModel):
    id          : str
    Nazev_Ukolu : str


app = FastAPI()
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/Ukoly", response_model=List[SeznamUkolu])
async def ZobrazVsechnyUkoly():
    query = ukoly.select()
    return await database.fetch_all(query)

@app.put("/Ukoly", response_model=List[SeznamUkolu])
async def UkolUpdate():
    query = ukoly.update()
    return await database.fetch_all(query)