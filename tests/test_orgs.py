from tests.conftest import register_login

def test_create_list_org(client):
    import uuid
    email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    username = f"owner_{uuid.uuid4().hex[:6]}"
    token = register_login(client, email, username, "pwd123")

    res =client.post("/orgs", json={"name": "Acme"}, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 201

    res =client.get("/orgs",headers={"Authorization":f"Bearer {token}"})

    assert len(res.json()) ==1
    assert res.json()[0]["role"] == "owner"
    
    