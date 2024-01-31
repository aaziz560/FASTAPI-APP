from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from fastapi.testclient import TestClient
import unittest

DATABASE_URL = "postgresql://aziz:aziz@localhost:5432/aziz"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

people = Table(
    "people",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("first_name", String(100)),
    Column("last_name", String(100)),
    Column("age", Integer),
)


class PersonDB(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    age = Column(Integer)


app = FastAPI()


def create_table():
    with engine.connect() as connection:
        if not connection.dialect.has_table(connection, "people"):
            Base.metadata.create_all(bind=engine)


create_table()


class Person(BaseModel):
    first_name: str
    last_name: str
    age: int


class DeletedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


class UpdatedPersonRequest(BaseModel):
    first_name: str = ...
    last_name: str = ...
    age: int = ...


class UpdatedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


class PatchPersonRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None


class PatchedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


class PersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


def create_person(person: Person, sessionLocal):
    db_person = PersonDB(**person.dict())
    with sessionLocal as db:
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
    return db_person


def get_people(sessionLocal):
    with sessionLocal as db:
        people_query = db.query(PersonDB).all()
        return people_query


def delete_person(person_id: int, sessionLocal):
    with sessionLocal as db:
        existing_person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not existing_person:
            raise HTTPException(status_code=406, detail="Person not available")

        db.delete(existing_person)
        db.commit()
        return existing_person


def update_person(person_id: int, updated_person: UpdatedPersonRequest, sessionLocal):
    with sessionLocal as db:
        existing_person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not existing_person:
            raise HTTPException(status_code=404, detail="Person not available")

        for field, value in updated_person.dict(exclude_unset=True).items():
            setattr(existing_person, field, value)

        db.commit()
        return UpdatedPersonResponse(
            id=existing_person.id,
            first_name=existing_person.first_name,
            last_name=existing_person.last_name,
            age=existing_person.age,
        )


def patch_person(person_id: int, patch_request: PatchPersonRequest):
    with SessionLocal() as db:
        existing_person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not existing_person:
            raise HTTPException(status_code=406, detail="Person not available")

        for field, value in patch_request.dict(exclude_unset=True).items():
            setattr(existing_person, field, value)

        db.commit()
        return existing_person


@app.post("/people", response_model=PersonResponse)
async def create_person_api(person: Person):
    db_person = create_person(person, SessionLocal)
    return PersonResponse(**db_person.__dict__)


@app.get("/people", response_model=List[PersonResponse])
async def get_people_api():
    people_query = get_people(SessionLocal)
    return [PersonResponse(**person.__dict__) for person in people_query]


@app.delete("/people/{person_id}", response_model=DeletedPersonResponse)
def delete_person_api(person_id: int):
    db_person = delete_person(person_id, SessionLocal)
    return DeletedPersonResponse(**db_person.__dict__)


@app.put("/people/{person_id}", response_model=UpdatedPersonResponse)
def update_person_api(person_id: int, updated_person: UpdatedPersonRequest):
    db_person = update_person(person_id, updated_person, SessionLocal)
    return UpdatedPersonResponse(**db_person.__dict__)


@app.patch("/people/{person_id}", response_model=PatchedPersonResponse)
def patch_person_api(person_id: int, patch_request: PatchPersonRequest):
    db_person = patch_person(person_id, patch_request)
    return PatchedPersonResponse(**db_person.__dict__)
