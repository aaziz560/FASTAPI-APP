import unittest
from main import create_person, get_people, delete_person, update_person
from main import Person, PersonDB

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = "postgresql://aziz:aziz@test-postgres:5432/aziz"


engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_table():
    with engine.connect() as connection:
        if not connection.dialect.has_table(connection, "people"):
            Base.metadata.create_all(bind=engine)

class TestApp(unittest.TestCase):
    def setUp(self):
        create_table()

    def tearDown(self):
        with SessionLocal() as db:
            db.query(PersonDB).delete()
            db.commit()

    def test_create_person(self):
        person_data = Person(first_name="Aziz", last_name="FAFI", age=25)
        db_person = create_person(person_data)
        self.assertEqual(db_person.first_name, "Aziz")
        self.assertEqual(db_person.last_name, "FAFI")
        self.assertEqual(db_person.age, 25)
        delete_person(db_person.id)

    def test_get_people(self):
        person_data = Person(first_name="Aziz", last_name="FAFI", age=26)
        db_person = create_person(person_data)
        people = get_people()
        self.assertEqual(len(people), 1)
        self.assertEqual(db_person.first_name, "Aziz")
        self.assertEqual(db_person.last_name, "FAFI")
        self.assertEqual(db_person.age, 26)
        delete_person(db_person.id)

    def test_delete_person(self):
        person_data = Person(first_name="Aziz", last_name="FAFI", age=28)
        person = create_person(person_data)
        deleted_person = delete_person(person.id)
        self.assertEqual(deleted_person.first_name, "Aziz")

    def test_update_person(self):
        person_data = Person(first_name="Aziz", last_name="FAFI", age=29)
        person = create_person(person_data)
        updated_data = Person(first_name="Achref", last_name="KHMIRI", age=30)
        updated_person = update_person(person.id, updated_data)
        self.assertEqual(updated_person.first_name, "Achref")
        self.assertEqual(updated_person.last_name, "KHMIRI")
        self.assertEqual(updated_person.age, 30)
        delete_person(updated_person.id)


if __name__ == "__main__":
    unittest.main()
