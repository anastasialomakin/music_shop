from app.models import User, db

def test_admin_dashboard_access_denied_for_user(client, user):
    client.post('/login', data={'email': user.email, 'password': '1234'})
    r = client.get('/admin/dashboard', follow_redirects=True)
    assert r.status_code == 403 or 'Доступ запрещен' in r.data.decode('utf-8')

def test_admin_dashboard_access_granted(client, app):
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('1234')
    db.session.add(admin)
    db.session.commit()

    client.post('/login', data={'email': admin.email, 'password': '1234'})
    r = client.get('/admin/dashboard')
    assert r.status_code == 200
