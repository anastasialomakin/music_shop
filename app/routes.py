from app import app
from flask import render_template, flash, redirect, url_for, session, request
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Record, Ensemble, Customer, Composition, Order
from app.forms import EnsembleForm, LoginForm, ProfileForm

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
    record = Record.query.get_or_404(id)
    return render_template('record_detail.html', title=record.title, record=record)

@app.route('/ensemble/<int:id>')
def ensemble_detail(id):
    ensemble = Ensemble.query.get_or_404(id)
    records = Record.query.join(Record.compositions).filter(Composition.ensemble_id == ensemble.id).all()
    return render_template('ensemble_detail.html', title=ensemble.name, ensemble=ensemble, records=records)

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')

@app.route('/ensembles')
def ensembles_list():
    # TODO: Заменить на реальный запрос к БД с пагинацией
    fake_ensembles = Ensemble.query.all() # Пока просто возьмем всех из БД
    return render_template('ensembles_list.html', title='Все ансамбли', ensembles=fake_ensembles)

@app.route('/add_to_cart/<int:record_id>', methods=['POST'])
@login_required
def add_to_cart(record_id):
    cart = session.get('cart', {})
    
    cart_item = str(record_id)
    cart[cart_item] = cart.get(cart_item, 0) + 1
    
    session['cart'] = cart
    flash('Товар добавлен в корзину!')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    if not cart_items:
        return render_template('cart.html', title='Корзина', items_with_details=[], total=0)
    record_ids = [int(id) for id in cart_items.keys()]
    records_in_cart = Record.query.filter(Record.id.in_(record_ids)).all()
    
    items_with_details = []
    total_price = 0
    for record in records_in_cart:
        quantity = cart_items.get(str(record.id), 0)
        subtotal = record.retail_price * quantity
        total_price += subtotal
        items_with_details.append({
            'record': record,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render_template('cart.html', title='Корзина', items_with_details=items_with_details, total=total_price)

@app.route('/remove_from_cart/<int:record_id>', methods=['POST'])
@login_required
def remove_from_cart(record_id):
    cart = session.get('cart', {})
    if str(record_id) in cart:
        del cart[str(record_id)]
        session['cart'] = cart
        flash('Товар удален из корзины.')
    return redirect(url_for('cart'))

# --- РАЗДЕЛ ПОЛЬЗОВАТЕЛЯ ---

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.shipping_address = form.shipping_address.data
        db.session.commit()
        flash('Ваш профиль был обновлен.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.shipping_address.data = current_user.shipping_address
    return render_template('profile.html', title='Мой профиль', form=form)

@app.route('/orders')
@login_required
def orders_list():
    # ЗАГЛУШКА: в будущем здесь будет запрос к реальным заказам
    # orders = Order.query.filter_by(customer_id=current_user.id).all()
    fake_orders = [
        {'id': 1, 'date': '2025-09-10', 'total': 49.98, 'status': 'Доставлен'},
        {'id': 2, 'date': '2025-09-14', 'total': 29.99, 'status': 'В обработке'},
    ]
    return render_template('orders.html', title='Мои заказы', orders=fake_orders)

@app.route('/checkout')
@login_required
def checkout():
    # ЗАГЛУШКА: здесь будет логика оформления заказа
    return render_template('checkout.html', title='Оформление заказа')