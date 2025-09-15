from app import app
from flask import render_template, flash, redirect, url_for
from app import db
from flask_login import current_user, login_user, logout_user
from app.models import Record, Ensemble, Customer
from app.forms import EnsembleForm, LoginForm

@app.route('/')
@app.route('/index')
def index():
    """
    Главная страница (каталог товаров).
    """
    records_from_db = Record.query.all()
    return render_template('index.html', title='Каталог', records=records_from_db)

@app.route('/admin/ensemble/add', methods=['GET', 'POST'])
def add_ensemble():
    form = EnsembleForm()
    if form.validate_on_submit():
        new_ensemble = Ensemble(name=form.name.data, description=form.description.data)
        db.session.add(new_ensemble)
        db.session.commit()
        flash('Ансамбль успешно добавлен!') 
        return redirect(url_for('index')) 
    return render_template('add_ensemble.html', title='Добавить ансамбль', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароль')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        flash(f'Добро пожаловать, {user.username}!')
        return redirect(url_for('index'))
        
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/record/<int:id>')
def record_detail(id):
    # TODO: Заменить на реальный запрос к БД по id
    fake_record = {
        'id': id,
        'title': 'Пример пластинки',
        'ensemble_name': 'Тестовая группа',
        'release_year': 2025,
        'format': 'LP',
        'manufacturer_name': 'Super Label',
        'retail_price': 99.99,
        'description': 'Это очень подробное и интересное описание пластинки, которое рассказывает о ее создании и музыкальном значении.',
        'cover_image_url': 'https://via.placeholder.com/400'
    }
    return render_template('record_detail.html', title=fake_record['title'], record=fake_record)

@app.route('/ensemble/<int:id>')
def ensemble_detail(id):
    # TODO: Заменить на реальные запросы к БД
    fake_ensemble = {'id': id, 'name': 'Название ансамбля', 'description': 'Это описание очень известного и популярного ансамбля.'}
    fake_records_list = [
        {'id': 1, 'title': 'Первый альбом', 'retail_price': 19.99, 'cover_image_url': 'https://via.placeholder.com/200'},
        {'id': 2, 'title': 'Второй альбом', 'retail_price': 24.99, 'cover_image_url': 'https://via.placeholder.com/200'}
    ]
    return render_template('ensemble_detail.html', title=fake_ensemble['name'], ensemble=fake_ensemble, records=fake_records_list)

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')

@app.route('/ensembles')
def ensembles_list():
    # TODO: Заменить на реальный запрос к БД с пагинацией
    fake_ensembles = Ensemble.query.all() # Пока просто возьмем всех из БД
    return render_template('ensembles_list.html', title='Все ансамбли', ensembles=fake_ensembles)