import os
import main
main.DB_PATH = "test_todos.db"
if os.path.exists(main.DB_PATH):
    os.remove(main.DB_PATH)
main.init_db()

from fastapi.testclient import TestClient
client = TestClient(main.app)


def test_crud_flow():
    r = client.post("/todos", json={"title": "Belajar FastAPI"})
    assert r.status_code == 201
    todo = r.json()
    assert todo["done"] is False
    tid = todo["id"]

    assert client.get(f"/todos/{tid}").json()["title"] == "Belajar FastAPI"

    r = client.patch(f"/todos/{tid}", json={"done": True})
    assert r.json()["done"] is True

    assert len(client.get("/todos?done=true").json()) == 1
    assert len(client.get("/todos?done=false").json()) == 0

    assert client.delete(f"/todos/{tid}").status_code == 204
    assert client.get(f"/todos/{tid}").status_code == 404


def test_validation():
    assert client.post("/todos", json={"title": ""}).status_code == 422
    assert client.patch("/todos/999", json={"done": True}).status_code == 404
    assert client.patch("/todos/1", json={}).status_code == 400
