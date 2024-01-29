from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
from pydantic import BaseModel
import json


# un simple test

from fastapi.testclient import TestClient
import unittest


# testt

app = FastAPI()

# git comment


# git comment


# Configuration de la base de données
DATABASE_URL = "postgresql://aziz:aziz@172.17.0.3:5432/aziz"


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)  # Faire la connexion avec psycopg2
    return conn  # retourner la resultat


conn = get_connection()  # faire la connexion


def create_table():
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                age INTEGER
            );
            """
        )
    conn.commit()  # etablir


# Appel à la fonction pour créer la table au démarrage de l'application
create_table()


class Person(BaseModel):
    first_name: str
    last_name: str
    age: int


def create_person(person: Person):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO people (first_name, last_name, age) VALUES (%s, %s, %s) RETURNING id;",
            (person.first_name, person.last_name, person.age),
        )
        person_id = cursor.fetchone()[
            0
        ]  # Récupère l'ID de la personne nouvellement insérée à partir du résultat de la requête RETURNING.
        conn.commit()
        return Person(
            id=person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            age=person.age,
        )


def get_people():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM people;")
        people = (
            cursor.fetchall()
        )  # Récupère toutes les entrées de la table et les stocke dans la variable people.
        return [
            {"id": p[0], "first_name": p[1], "last_name": p[2], "age": p[3]}
            for p in people
        ]


@app.post("/people", response_model=Person)
async def create_person_api(person: Person):
    return create_person(person)


@app.get("/people", response_model=list[Person])
async def get_people_api():
    return get_people()


class DeletedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


@app.delete("/people/{person_id}", response_model=DeletedPersonResponse)
def delete_person(person_id: int):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id , first_name , last_name , age FROM people WHERE id = %s; ",
            (person_id,),
        )
        existing_person = cursor.fetchone()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=406, detail="Person not available")
        deleted_person = DeletedPersonResponse(
            id=existing_person[0],
            first_name=existing_person[1],
            last_name=existing_person[2],
            age=existing_person[3],
        )

        cursor.execute("DELETE FROM people where id = %s;", (person_id,))
        conn.commit()

        return deleted_person


class UpdatedPersonRequest(BaseModel):
    first_name: str = ...
    last_name: str = ...
    age: int = ...


class UpdatedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


@app.put("/people/{person_id}", response_model=UpdatedPersonResponse)
def update_person(person_id=int, updated_person: UpdatedPersonRequest = None):
    if not updated_person or len(updated_person.dict()) == 0:
        raise HTTPException(status_code=422, detail="EMPTY REQUEST BODY")

    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE people SET first_name = %s , last_name = %s , age = %s WHERE id = %s RETURNING id , first_name , last_name , age ;",
            (
                updated_person.first_name,
                updated_person.last_name,
                updated_person.age,
                person_id,
            ),
        )
        # fetchone pour la recuperation de la ligne
        # updated_person = cursor.fetchone()
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Person not available")

        return UpdatedPersonResponse(
            id=person_id,
            first_name=updated_person.first_name,
            last_name=updated_person.last_name,
            age=updated_person.age,
        )


class PatchPersonRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None


class PatchedPersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int


@app.patch("/people/{person_id}", response_model=PatchedPersonResponse)
def patch_person(person_id: int, patch_request: PatchPersonRequest):
    with conn.cursor() as cursor:
        update = {
            cle: value
            for cle, value in patch_request.dict().items()
            if value is not None
        }
        set_clause = ", ".join([f"{field} = %s" for field in update])
        query = f"UPDATE people SET {set_clause} WHERE id = %s RETURNING id , first_name , last_name , age;"
        cursor.execute(query, (*update.values(), person_id))
        updated_person = cursor.fetchone()
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=406, detail="Person not available")

        return PatchedPersonResponse(
            id=updated_person[0],
            first_name=updated_person[1],
            last_name=updated_person[2],
            age=updated_person[3],
        )


# test for webhook

# test for webhook


class TestApp(unittest.TestCase):
    def setUp(self):
        create_table()
        self.client = TestClient(app)

    def tearDown(self):
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS people;")
            conn.commit()

    def test_create_person(self):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO people (first_name, last_name, age) VALUES (%s, %s, %s);",
                ("Aziz", "FAFI", 21),
            )
            conn.commit()

        person_data = {"first_name": "Aziz", "last_name": "FAFI", "age": 21}

        response = self.client.post("/people", json=person_data)

        print(response.content)

        self.assertEqual(response.status_code, 200)

    def test_get_people(self):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO people (first_name, last_name, age) VALUES (%s, %s, %s);",
                ("Aziz", "FAFI", 21),
            )
            conn.commit()

        response = self.client.get("/people")

        print(response.content)

        self.assertEqual(response.status_code, 200)

    def test_delete_person(self):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO people (id, first_name, last_name, age) VALUES (%s, %s, %s, %s) RETURNING id;",
                (985, "Aziz", "FAFI", 21),
            )
            person_id = cursor.fetchone()[0]
            conn.commit()

        response = self.client.delete(f"/people/{person_id}")
        self.assertEqual(response.status_code, 200)

        # response_get = self.client.get(f"/people/{person_id}")
        # self.assertEqual(response_get.status_code, 404)

    def test_update_person(self):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO people (first_name, last_name, age) VALUES (%s, %s, %s) RETURNING id;",
                ("Aziz", "FAFI", 21),
            )
            person_id = cursor.fetchone()[0]
            conn.commit()

        updated_data = {"first_name": "Achref", "last_name": "KHMIRI", "age": 30}

        response = self.client.put(f"/people/{person_id}", json=updated_data)
        self.assertEqual(response.status_code, 200)

        # response_get = self.client.get(f"/people/{person_id}")
        # self.assertEqual(response_get.status_code, 200)
        # self.assertEqual(
        #     response_get.json(),
        #     {
        #         "id": person_id,
        #         "first_name": "Achref",
        #         "last_name": "KHMIRI",
        #         "age": 30,
        #     },
        # )


if __name__ == "__main__":
    unittest.main()
