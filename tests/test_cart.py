def test_add_to_cart(client):
    with client.session_transaction() as s:
        s['cart'] = {}

    r = client.post('/add_to_cart/1', data={'quantity': 2}, follow_redirects=True)
    assert r.status_code == 200
    with client.session_transaction() as s:
        assert '1' in s['cart']
        assert s['cart']['1']['quantity'] == 2


def test_remove_from_cart(client):
    with client.session_transaction() as s:
        s['cart'] = {'1': {'name': 'Test Record', 'price': 100, 'quantity': 1}}

    r = client.post('/remove_from_cart/1', follow_redirects=True)
    assert r.status_code == 200
    with client.session_transaction() as s:
        assert '1' not in s['cart']
