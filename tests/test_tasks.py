import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from database import connect, setup
from user import register, login
from task import add_task, view_tasks, get_task, update_task, delete_task

class TaskTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        environment = patch.dict(os.environ, {"TASK_MANAGER_DB": str(Path(tmp.name)/"test.db")})
        environment.start()
        self.addCleanup(environment.stop)
        setup()
        self.assertTrue(register("alice","passphrase-one"))
        self.assertTrue(register("bob","passphrase-two"))
        self.a = login("alice","passphrase-one")[0]
        self.b = login("bob","passphrase-two")[0]

    def test_password_hash_and_login(self):
        with connect() as db:
            stored = db.execute("SELECT password_hash FROM users WHERE username=?",("alice",)).fetchone()[0]
        self.assertTrue(stored.startswith("pbkdf2_sha256$"))
        self.assertNotIn("passphrase-one",stored)
        self.assertIsNone(login("alice","wrong"))
        self.assertFalse(register("alice","another-password"))

    def test_crud(self):
        task_id = add_task(self.a,"Study Python","high","2026-11-02")
        self.assertEqual(len(view_tasks(self.a)),1)
        self.assertTrue(update_task(self.a,task_id,"Finish API","low",None))
        self.assertEqual(get_task(self.a,task_id)["title"],"Finish API")
        self.assertTrue(delete_task(self.a,task_id))
        self.assertIsNone(get_task(self.a,task_id))

    def test_task_ownership(self):
        task_id = add_task(self.a,"Private task")
        self.assertEqual(view_tasks(self.b),[])
        self.assertIsNone(get_task(self.b,task_id))
        self.assertFalse(update_task(self.b,task_id,"Stolen","low",None))
        self.assertFalse(delete_task(self.b,task_id))
        self.assertIsNotNone(get_task(self.a,task_id))

    def test_validation(self):
        with self.assertRaises(ValueError):
            add_task(self.a,"  ")
        with self.assertRaises(ValueError):
            add_task(self.a,"test","urgent")
        with self.assertRaises(ValueError):
            register("new","short")
