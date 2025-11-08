import pytest
from backend.app import create_app, db
from backend.models import User, Article, Summary
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def register_user(client, username="testuser", email="test@example.com", password="testpass"):
    return client.post('/signup', json={
        "username": username, "email": email, "password": password
    })

def login_user(client, username="testuser", password="testpass"):
    return client.post('/login', json={
        "username": username, "password": password
    })

def test_signup_and_login(client):
    res = register_user(client)
    assert res.status_code == 201 or res.status_code == 400  # Already present is okay

    res = login_user(client)
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    return data["access_token"]

def test_summary_crud(client):
    token = test_signup_and_login(client)
    # Create article (needed for summary)
    res = client.post('/articles', json={"title": "A", "content": "B"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    article_id = res.get_json()["id"]

    # Create summary
    res = client.post('/summaries', json={"text": "Summary!", "article_id": article_id},
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    summary_id = res.get_json()["id"]

    # Get summaries
    res = client.get('/summaries', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert any(s["id"] == summary_id for s in res.get_json())

    # Update summary
    res = client.patch(f'/summaries/{summary_id}', json={"text": "Updated"},
                       headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["text"] == "Updated"

    # Delete summary
    res = client.delete(f'/summaries/{summary_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    # Confirm deletion
    res = client.get('/summaries', headers={"Authorization": f"Bearer {token}"})
    assert summary_id not in [s["id"] for s in res.get_json()]

