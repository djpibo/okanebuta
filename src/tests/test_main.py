# test_ 규칙을 지켜줘야 pytest가 인식할 수 있음
from fastapi.testclient import TestClient
from main import app
from orm import ToDo


def test_health_check_handler(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


# Reason for Using MOCK : To prepare insert/update ops in real database.
def test_get_todos(client, mocker):
    mocker.patch("main.get_todos", return_value=[
        ToDo(id=1, contents="string", is_done=True),
        ToDo(id=2, contents="string", is_done=True),
        ToDo(id=3, contents="string", is_done=True)
    ])
    response = client.get("/todos?order=DESC")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 3, "contents": "string", "is_done": True},
            {"id": 2, "contents": "string", "is_done": True},
            {"id": 1, "contents": "string", "is_done": True}
        ]
    }


def test_get_todo(client, mocker):
    # 200
    mocker.patch("main.get_todo_by_todo_id", return_value=ToDo(id=1, contents="string", is_done=True))
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "string", "is_done": True}

    # 404
    mocker.patch(
        "main.get_todo_by_todo_id",
        return_value=None
    )
    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found!"}


def test_create_todo(client, mocker):
    # mocker-spy is testing util for tracking method parameter
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch(
        "main.create_todo",
        return_value=ToDo(id=1, contents="string", is_done=True)
    )

    body = {
        "contents": "test",
        "is_done": False,
    }
    response = client.post("/todos", json=body)

    # using mocker-spy for test method-"create"
    # method-"create" is insert query
    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False

    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "string", "is_done": True}


def test_update_todo(client, mocker):
    # 200
    mocker.patch(
        "main.get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="string", is_done=True)
    )
    undone = mocker.patch.object(ToDo, "undone")
    mocker.patch(
        "main.update_todo",
        return_value=ToDo(id=1, contents="string", is_done=False)
    )
    response = client.patch("/todos/1")
    undone.assert_called_once_with()
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "string", "is_done": False}

    # 404
    mocker.patch("main.get_todo_by_todo_id",return_value=None)
    response = client.get("/todos/1", json={"is_done": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found!"}


def test_delete_todo(client, mocker):
    # 204
    mocker.patch("main.get_todo_by_todo_id", return_value=ToDo(id=1, contents="string", is_done=True))
    mocker.patch("main.delete_todo", return_value=None)
    response = client.delete("/todos/1")
    assert response.status_code == 204
    assert response.json() == {"id": 1, "contents": "string", "is_done": True}

    # 404
    mocker.patch("main.get_todo_by_todo_id",return_value=None)
    response = client.get("/todos/1", json={"is_done": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found!"}
