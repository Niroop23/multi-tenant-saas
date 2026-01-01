import uuid


def test_register_login(client):
    email = f"{uuid.uuid4().hex[:8]}@test.com"
    username = f"user_{uuid.uuid4().hex[:6]}"

    res=client.post("/auth/register",json={"email":email, "username":username, "password":"password123"},)

    assert res.status_code ==200

    res=client.post("/auth/login",json={"identifier":email, "password":"password123"})
    assert res.status_code ==200
    assert "access_token" in res.json()
    

def test_invalid_login(client):
    res=client.post("/auth/login", json={
        "identifier":"aa@test.com",
        "password":"sddfdfd"
    })
    
    assert res.status_code==401