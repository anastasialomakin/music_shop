from app import app
from flask import render_template

FAKE_RECORDS = [
    {
        'id': 1,
        'title': 'The Dark Side of the Moon',
        'artist': 'Pink Floyd',
        'price': 25.99,
        'stock_quantity': 10,
        'cover_image_url': 'https://upload.wikimedia.org/wikipedia/en/3/3b/Dark_Side_of_the_Moon.png'
    },
    {
        'id': 2,
        'title': 'Abbey Road',
        'artist': 'The Beatles',
        'price': 22.50,
        'stock_quantity': 5,
        'cover_image_url': 'https://upload.wikimedia.org/wikipedia/en/4/42/Beatles_-_Abbey_Road.jpg'
    },
    {
        'id': 3,
        'title': 'Kind of Blue',
        'artist': 'Miles Davis',
        'price': 28.00,
        'stock_quantity': 0, 
        'cover_image_url': 'https://upload.wikimedia.org/wikipedia/en/9/9c/MilesDavisKindofBlue.jpg'
    },
]


@app.route('/')
@app.route('/index')
def index():
    """
    Главная страница (каталог товаров).
    """
    records_from_db = FAKE_RECORDS
    return render_template('index.html', title='Каталог', records=records_from_db)