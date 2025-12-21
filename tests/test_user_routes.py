def _register_user(client, email="user@example.com", username="user", password="secret"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "username": username,
            "public_name": "User",
        },
    )


def test_register_login_and_profile(client, db_session):
    response = _register_user(client)
    assert response.status_code == 200

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get("/profile/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_user_search_and_lookup(client, db_session):
    _register_user(client, email="ana@example.com", username="ana", password="pass")

    response = client.get("/users/search", params={"q": "an"})
    assert response.status_code == 200
    assert response.json()[0]["username"] == "ana"

    response = client.get("/users/by-username/ana")
    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"
