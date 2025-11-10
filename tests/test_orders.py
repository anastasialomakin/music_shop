from app import db
from app.models import User

def test_checkout_creates_order(client, app, user):
    client.post('/login', data={'email': user.email, 'password': '1234'})
    with client.session_transaction() as s:
        s['cart'] = {'1': {'name': 'Test Record', 'price': 100, 'quantity': 1}}

    r = client.post('/checkout', data={
        'address': 'Test street 5',
        'payment_method': 'card'
    }, follow_redirects=True)

    text = r.data.decode('utf-8')
    assert r.status_code == 200
    assert 'Заказ' in text or 'Order' in text
