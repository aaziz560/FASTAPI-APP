import unittest
from main import create_table, create_person, get_people, delete_person, update_person
from main import PersonDB , Person
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


TEST_DATABASE_URL = "postgresql://aziz:aziz@test-postgres:5432/aziz"







class TestApp(unittest.TestCase):
    
            
    def setUp(self):
        create_table()

    def tearDown(self):
        with get_test_session(TEST_DATABASE_URL) as db:
            db.query(PersonDB).delete()
            db.commit()

    def test_create_person(self):
        test_SessionLocal = get_test_session(TEST_DATABASE_URL)
        person_data = Person(first_name="Aziz", last_name="FAFI", age=25)
        db_person = create_person(person_data, test_SessionLocal)
        self.assertEqual(db_person.first_name, "Aziz")
        self.assertEqual(db_person.last_name, "FAFI")
        self.assertEqual(db_person.age, 25)
        delete_person(db_person.id)

    def test_get_people(self):
        test_SessionLocal = get_test_session(TEST_DATABASE_URL)
        person_data = Person(first_name="Aziz", last_name="FAFI", age=26)
        db_person = create_person(person_data, test_SessionLocal)
        people = get_people(SessionLocal)
        self.assertEqual(len(people), 1)
        self.assertEqual(db_person.first_name, "Aziz")
        self.assertEqual(db_person.last_name, "FAFI")
        self.assertEqual(db_person.age, 26)
        delete_person(db_person.id, SessionLocal)

    def test_delete_person(self):
        test_SessionLocal = get_test_session(TEST_DATABASE_URL)
        person_data = Person(first_name="Aziz", last_name="FAFI", age=28)
        person = create_person(person_data, test_SessionLocal)
        deleted_person = delete_person(person.id, SessionLocal)
        self.assertEqual(deleted_person.first_name, "Aziz")

    def test_update_person(self):
        test_SessionLocal = get_test_session(TEST_DATABASE_URL)
        person_data = Person(first_name="Aziz", last_name="FAFI", age=29)
        person = create_person(person_data, test_SessionLocal)
        updated_data = Person(first_name="Achref", last_name="KHMIRI", age=30)
        updated_person = update_person(person.id, updated_data, SessionLocal)
        self.assertEqual(updated_person.first_name, "Achref")
        self.assertEqual(updated_person.last_name, "KHMIRI")
        self.assertEqual(updated_person.age, 30)
        delete_person(updated_person.id)



if __name__ == "__main__":
    unittest.main()
