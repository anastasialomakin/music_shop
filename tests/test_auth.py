def test_register_login_logout(client):
    # Регистрация
    r = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': '1234',
        'confirm_password': '1234'
    }, follow_redirects=True)
    assert r.status_code == 200

    # Вход
    r = client.post('/login', data={
        'email': 'new@example.com',
        'password': '1234'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'logout' in r.data.lower()

    # Выход
    r = client.get('/logout', follow_redirects=True)
    assert r.status_code == 200
