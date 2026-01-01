import uuid


def test_invite_accept_flow(client):
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_username = f"owner_{uuid.uuid4().hex[:6]}"

    client.post("/auth/register",json={"email":owner_email, "username":owner_username, "password":"password"},)

    owner_token = client.post(
        "/auth/login", json={"identifier": owner_email, "password": "password"}
    ).json()["access_token"]

    org = client.post(
        "/orgs", json={"name": "InviteOrg"}, headers={"Authorization": f"Bearer {owner_token}"}
    ).json()

    invite_email = f"invite_{uuid.uuid4().hex[:8]}@example.com"

    res = client.post(
        f"/orgs/{org['id']}/invites",
        json={"email": invite_email, "role": "member"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert res.status_code == 201
    invite_id =res.json()["id"]

    client.post(
        "/auth/register",
        json={"email":invite_email, "username":"invitee", "password":"password"},
    )

    invitee_token = client.post(
        "/auth/login", json={"identifier": invite_email, "password": "password"}
    ).json()["access_token"]

    # accept invite
    res = client.post(
        f"/orgs/{org['id']}/invites/{invite_id}/accept",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )
    assert res.status_code == 200