def test_index_page_loads(client):
    r = client.get('/')
    assert r.status_code == 200
    text = r.data.decode('utf-8')
    assert 'Виниловые' in text or 'Vinyl' in text

def test_search_query(client):
    r = client.get('/index?search=beatles')
    assert r.status_code == 200
