import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from api import app

class ApiTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        environment = patch.dict(os.environ, {"TASK_MANAGER_DB": str(Path(tmp.name)/"test.db")})
        environment.start()
        self.addCleanup(environment.stop)
        client_context = TestClient(app)
        self.client = client_context.__enter__()
        self.addCleanup(lambda: client_context.__exit__(None,None,None))
        for username in ("alice","bob"):
            response = self.client.post("/users",json={"username":username,"password":"secure-passphrase"})
            self.assertEqual(response.status_code,201)

    def test_crud_and_missing_resource(self):
        auth=("alice","secure-passphrase")
        created=self.client.post("/tasks",json={"title":"Interview prep","priority":"high"},auth=auth)
        self.assertEqual(created.status_code,201)
        task_id=created.json()["id"]
        self.assertEqual(len(self.client.get("/tasks",auth=auth).json()),1)
        updated=self.client.put(f"/tasks/{task_id}",json={"title":"Complete portfolio"},auth=auth)
        self.assertEqual(updated.json()["title"],"Complete portfolio")
        self.assertEqual(self.client.delete(f"/tasks/{task_id}",auth=auth).status_code,204)
        self.assertEqual(self.client.get(f"/tasks/{task_id}",auth=auth).status_code,404)

    def test_authentication_and_authorisation(self):
        task_id=self.client.post("/tasks",json={"title":"Private"},auth=("alice","secure-passphrase")).json()["id"]
        self.assertEqual(self.client.get("/tasks").status_code,401)
        self.assertEqual(self.client.get("/tasks",auth=("alice","wrong")).status_code,401)
        self.assertEqual(self.client.get(f"/tasks/{task_id}",auth=("bob","secure-passphrase")).status_code,404)
        self.assertEqual(self.client.delete(f"/tasks/{task_id}",auth=("bob","secure-passphrase")).status_code,404)

    def test_invalid_data(self):
        auth=("alice","secure-passphrase")
        self.assertEqual(self.client.post("/tasks",json={"title":""},auth=auth).status_code,422)
        self.assertEqual(self.client.post("/tasks",json={"title":"OK","priority":"urgent"},auth=auth).status_code,422)
        self.assertEqual(self.client.post("/users",json={"username":"alice","password":"secure-passphrase"}).status_code,409)
