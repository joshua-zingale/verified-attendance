def test_form_ok_response(client):
    assert client.get("/").status_code == 200

def test_admin_ok_response(client):
    assert client.get("/admin", follow_redirects=True).status_code == 200


def test_sign_in_and_access_portal(client, app):

    with client.session_transaction() as sess:
        assert sess.get('logged_in') is not True

    response = client.get("/admin", follow_redirects=True)

    assert "password" in str(response.data).lower()
    assert response.status_code == 200
    
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is not True

    login_response = client.post("/admin_login", data={
        "password": app.config['ADMIN_PASSWORD']
    }, follow_redirects=True)


    assert login_response.status_code == 200
    assert "admin panel" in str(login_response.data).lower()

    with client.session_transaction() as sess:
        assert sess.get('logged_in')


def test_bad_password(client):
    client.post("/admin_login", data={
        "password": "bad_password_that_is_not_used"
    }, follow_redirects=True)

    assert client.get("/admin").status_code == 302