from datetime import datetime
from fastapi import FastAPI
import databases, sqlalchemy
from pydantic import BaseModel, Field
from typing import List
import psycopg2 as pg

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime

app = FastAPI()

connection = pg.connect(user="postgres",
                        password="605341",
                        host="127.0.0.1",
                        port="5432",
                        database="dbtest")
cur = connection.cursor()

DATABASE_URL = "postgresql://postgres:605341@127.0.0.1:5432/dbtest"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
Base = declarative_base()
engine = sqlalchemy.create_engine(
    DATABASE_URL
)

class Ukol(Base):
   __tablename__ = 'ukol'

   id = Column(Integer, primary_key = True)
   nazev_ukolu = Column(String)
   text_ukolu = Column(String)
   datum_vytvoreni = Column(String)
   datum_splneni = Column(String)

   

class Tagy(Base):
   __tablename__ = 'tagy'

   id = Column(Integer, primary_key = True)
   nazev_tagu = Column(String)
  # task = relationship("Task")

class Task(Base):
   __tablename__ = 'task'

   id = Column(Integer, primary_key = True)
   tag_id = Column(Integer, ForeignKey('tagy.id'))
   ukol_id = Column(Integer, ForeignKey('ukol.id'))
   
   tag = relationship("Tagy", back_populates = "task")
   uko = relationship("Ukol", back_populates = "task")



Tagy.task = relationship("Task", order_by = Task.id, back_populates = "tag")
Ukol.task = relationship("Task", order_by = Task.id, back_populates = "uko")

class Uzivatele(Base):
   __tablename__ = 'uzivatele'

   id = Column(Integer, primary_key = True)
   uziv_jmeno = Column(String)


class Role(Base):
   __tablename__ = 'role'

   id = Column(Integer, primary_key = True)
   nazev_role = Column(String)

class Autorizace(Base):
   __tablename__ = 'autorizace'

   id = Column(Integer, primary_key = True)
   tag_id = Column(Integer)
   povoleni = Column(Integer)
   
class Uziv_role(Base):
   __tablename__ = 'uziv_role'

   id = Column(Integer, primary_key = True)
   uzivatel_id = Column(Integer, ForeignKey('uzivatele.id'))
   role_id = Column(Integer, ForeignKey('role.id'))

   rol = relationship("Role", back_populates = "uziv_role")
   uzivatel = relationship("Uzivatele", back_populates = "uziv_role")

Role.uziv_role = relationship("Uziv_role", order_by = Uziv_role.id, back_populates = "rol")
Uzivatele.uziv_role = relationship("Uziv_role", order_by = Uziv_role.id, back_populates = "uzivatel")


class Autoriz_role(Base):
   __tablename__ = 'autoriz_role'

   id = Column(Integer, primary_key = True)
   autorizace_id = Column(Integer, ForeignKey('autorizace.id'))
   role_id = Column(Integer, ForeignKey('role.id'))

   rol = relationship("Role", back_populates = "autoriz_role")
   autoriz = relationship("Autorizace", back_populates = "autoriz_role")

Role.autoriz_role = relationship("Autoriz_role", order_by = Autoriz_role.id, back_populates = "rol")
Autorizace.autoriz_role = relationship("Autoriz_role", order_by = Autoriz_role.id, back_populates = "autoriz")



Base.metadata.create_all(engine)

statement = ("DELETE FROM uziv_role *")
engine.execute(statement)
statement = ("DELETE FROM autoriz_role *")
engine.execute(statement)
statement = ("DELETE FROM task *")
engine.execute(statement)
statement = ("DELETE FROM role *")
engine.execute(statement)
statement = ("DELETE FROM tagy *")
engine.execute(statement)
statement = ("DELETE FROM autorizace *")
engine.execute(statement)
statement = ("DELETE FROM ukol *")
engine.execute(statement)
statement = ("DELETE FROM uzivatele *")
engine.execute(statement)

statement = ("INSERT INTO role (nazev_role, id) VALUES ('Kybernetika-RW',1)")
engine.execute(statement)
statement = ("INSERT INTO role (nazev_role, id) VALUES ('Kybernetika-R',2)")
engine.execute(statement)
statement = ("INSERT INTO role (nazev_role,id) VALUES ('Strojirenstvi-RW',3)")
engine.execute(statement)
statement = ("INSERT INTO role (nazev_role,id) VALUES ('Strojirenstvi-R',4)")
engine.execute(statement)

statement = ("INSERT INTO tagy (nazev_tagu,id) VALUES ('Kybernetika',1)")
engine.execute(statement)
statement = ("INSERT INTO tagy (nazev_tagu,id) VALUES ('Strojirenstvi',2)")
engine.execute(statement)
statement = ("INSERT INTO tagy (nazev_tagu,id) VALUES ('Elektro',3)")
engine.execute(statement)
statement = ("INSERT INTO tagy (nazev_tagu,id) VALUES ('StalyStav',4)")
engine.execute(statement)

statement = ("INSERT INTO autorizace (tag_id, povoleni,id) VALUES (1, 1,1)") # 1 W/R - 2 R
engine.execute(statement)
statement = ("INSERT INTO autorizace (tag_id, povoleni,id) VALUES (1, 2,2)")
engine.execute(statement)
statement = ("INSERT INTO autorizace (tag_id, povoleni,id) VALUES (2, 1,3)") 
engine.execute(statement)
statement = ("INSERT INTO autorizace (tag_id, povoleni,id) VALUES (2, 2,4)")
engine.execute(statement)


statement = ("INSERT INTO autoriz_role (autorizace_id, role_id,id) VALUES (1,1,1 )") 
engine.execute(statement)
statement = ("INSERT INTO autoriz_role (autorizace_id, role_id,id) VALUES (2, 2,2)")
engine.execute(statement)
statement = ("INSERT INTO autoriz_role (autorizace_id, role_id,id) VALUES (3, 3,3)") 
engine.execute(statement)
statement = ("INSERT INTO autoriz_role (autorizace_id, role_id,id) VALUES (4, 4,4)")
engine.execute(statement)

pom_uzivatele=[]
pom_ukoly=[]
id_prihlaseneho_uzivatele = 3
autorizovane_povoleni=0
id_autorizovaneho_tagu=0

class Ukol(BaseModel):
    nazev: str
    text: str
    dvytvoreni: datetime
    dsplneni: datetime
    tag: int #(1-4)

class Uzivatel(BaseModel):
    nazev: str
    role: int



#Funkce PridejUzivatele: Do tabulky 'uzivatele' prida noveho uzivatele       Input(uz_jmeno(str) = Jmeno noveho uzivatele, uz_role(int) = Cislo jeho role(1-4))
def PridejUzivatele(uz_jmeno: str, uz_role: int):
    statement = ("INSERT INTO uzivatele (uziv_jmeno) VALUES ('{0}')".format(uz_jmeno))
    engine.execute(statement)
    
    cur.execute("SELECT id FROM uzivatele WHERE uziv_jmeno = '{0}'".format(uz_jmeno))
    id_uzivatele = cur.fetchone()
    PropojUzivatelRole(id_uzivatele[0], uz_role)
#Funkce PropojUzivatele: Propojí tabulky 'uzivatele' a 'role'               Input(uz_id(int) = ID prave pridaneho uzivatele, rol_id(int) = ID role, kterou ma)
def PropojUzivatelRole(uz_id: int, rol_id: int):
    print(uz_id)
    print(rol_id)
    statement = ("INSERT INTO uziv_role (uzivatel_id, role_id) VALUES ({}, {})".format(uz_id,rol_id))
    engine.execute(statement)

def PridejUkol(nazev: str, text:str, dvytvoreni:datetime, dsplneni:datetime, tag:int):
    statement = ("INSERT INTO ukol (nazev_ukolu, text_ukolu, datum_vytvoreni, datum_splneni) VALUES ('{}','{}','{}','{}')".format(nazev,text,dvytvoreni,dsplneni))
    engine.execute(statement)
    
    cur.execute("SELECT id FROM ukol WHERE nazev_ukolu = '{0}'".format(nazev))
    id_ukolu = cur.fetchone()
    PropojTagUkol(tag,id_ukolu[0])

def PropojTagUkol(tag_ID: int, ukol_ID: int):
    statement = ("INSERT INTO task (tag_id, ukol_id) VALUES ({}, {})".format(tag_ID,ukol_ID))
    engine.execute(statement)

def Autorizace():
    cur.execute("SELECT role_id FROM uziv_role WHERE uzivatel_id = '{0}'".format(id_prihlaseneho_uzivatele))
    id_prihlasene_role = cur.fetchone()
    print(id_prihlasene_role[0])
    cur.execute("SELECT autorizace_id FROM autoriz_role WHERE role_id = '{0}'".format(id_prihlasene_role[0]))
    id_prihlasene_autorizace = cur.fetchone()
    cur.execute("SELECT tag_id FROM autorizace WHERE id = '{0}'".format(id_prihlasene_autorizace[0]))
    id_autorizovaneho_tagu = cur.fetchone()
    cur.execute("SELECT povoleni FROM autorizace WHERE id = '{0}'".format(id_prihlasene_autorizace[0]))
    autorizovane_povoleni = cur.fetchone()
    
    print ("Ziskane autorizovane povoleni: ",autorizovane_povoleni[0])
    print("Ziskany autorizovany tag: ", id_autorizovaneho_tagu[0])


#FAST API
@app.post("/api/Uzivatel/")
#Funkce VytvorUzivatele: Vklada uzivatele do slovniku a vola funkci PridejUzivatele   Input(Uzivatel(BaseModel) = Prepripraveny model uzivatelu) Output(Volá funkci PridejUzivatele())
def VytvorUzivatele(uziv: Uzivatel):
    pom_uzivatele.append(uziv.dict())

    return (PridejUzivatele(pom_uzivatele[-1]['nazev'], pom_uzivatele[-1]['role']))

@app.post("/api/Ukol/")
def VytvorUkol(uk: Ukol):
    pom_ukoly.append(uk.dict())
    return (PridejUkol(pom_ukoly[-1]['nazev'], pom_ukoly[-1]['text'], pom_ukoly[-1]['dvytvoreni'], pom_ukoly[-1]['dsplneni'], pom_ukoly[-1]['tag']))



#@app.get("/api/Uzivatel/")
#async def get_headers():
#    return db_pom

