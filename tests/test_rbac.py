

def test_non_owner_delete_org(client):
    import uuid
    from tests.conftest import register_login

    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_username = f"owner_{uuid.uuid4().hex[:6]}"


    owner_token = register_login(client,owner_email,owner_username,"pwd123")
    
    org= client.post("/orgs",json={
        "name":"RBACorg"},headers={"Authorization":f"Bearer {owner_token}"}).json()
    
    
    member_email = f"member_{uuid.uuid4().hex[:8]}@example.com"
    member_token=register_login(client,member_email,"member","password")
    
    res=client.delete(f"/orgs/{org['id']}",headers={"Authorization":f"Bearer {member_token}"})
    
    
    assert res.status_code ==403