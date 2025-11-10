from app import db

def test_add_record_by_manufacturer(client, app, user):
    user.role = 'manufacturer'
    db.session.commit()

    client.post('/login', data={'email': user.email, 'password': '1234'})
    r = client.post('/my-records/add', data={
        'title': 'Test Record',
        'price': 200,
        'stock_quantity': 10,
        'band_id': 1,
        'genre_id': 1
    }, follow_redirects=True)
    assert r.status_code == 200
