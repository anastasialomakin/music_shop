from app import app
from flask import render_template, flash, redirect, url_for, session, request, abort
from app import db
from functools import wraps
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Record, Ensemble, Customer, Composition, Order
from app.forms import EnsembleForm, LoginForm, EditProfileForm, RecordForm, AdminEditUserForm

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

# покупатель

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
  
        if current_user.role == 'user':
            current_user.shipping_address = form.shipping_address.data

        if form.password.data:
            current_user.set_password(form.password.data)
            
        db.session.commit()
        flash('Ваш профиль был обновлен.')
        return redirect(url_for('profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        if current_user.role == 'user':
            form.shipping_address.data = current_user.shipping_address
            
    return render_template('profile.html', title='Личный кабинет', form=form)

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

def manufacturer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'manufacturer':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

# лейбл

@app.route('/my-records')
@login_required
@manufacturer_required
def my_records():
    records = Record.query.filter_by(manufacturer_id=current_user.manufacturer.id).all()
    return render_template('my_records.html', title='Мои пластинки', records=records)

@app.route('/my-records/add', methods=['GET', 'POST'])
@login_required
@manufacturer_required
def add_record():
    form = RecordForm()
    form.ensemble.choices = [(e.id, e.name) for e in Ensemble.query.order_by('name').all()]

    if form.validate_on_submit():
        ensemble = Ensemble.query.get(form.ensemble.data)
        new_composition = Composition(title=form.title.data, ensemble=ensemble)
        
        new_record = Record(
            title=form.title.data,
            release_year=form.release_year.data,
            retail_price=form.retail_price.data,
            stock_quantity=form.stock_quantity.data,
            description=form.description.data,
            manufacturer_id=current_user.manufacturer.id
        )
        new_record.compositions.append(new_composition)
        db.session.add(new_record)
        db.session.commit()
        flash('Пластинка успешно добавлена!')
        return redirect(url_for('my_records'))
        
    return render_template('record_form.html', title='Добавить пластинку', form=form)

@app.route('/my-records/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@manufacturer_required
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)
    if record.manufacturer_id != current_user.manufacturer.id:
        abort(403)
        
    form = RecordForm(obj=record)
    form.ensemble.choices = [(e.id, e.name) for e in Ensemble.query.order_by('name').all()]
    
    if form.validate_on_submit():
        record.title = form.title.data
        record.release_year = form.release_year.data
        record.retail_price = form.retail_price.data
        record.stock_quantity = form.stock_quantity.data
        record.description = form.description.data
        ensemble = Ensemble.query.get(form.ensemble.data)
        if record.compositions:
            record.compositions[0].ensemble = ensemble
        else: 
            new_composition = Composition(title=record.title, ensemble=ensemble)
            record.compositions.append(new_composition)

        db.session.commit()
        flash('Данные о пластинке обновлены.')
        return redirect(url_for('my_records'))
        
    elif request.method == 'GET':
        if record.compositions:
            form.ensemble.data = record.compositions[0].ensemble_id

    return render_template('record_form.html', title='Редактировать пластинку', form=form)

@app.route('/sales-report')
@login_required
@manufacturer_required
def sales_report():
    return render_template('sales_report.html', title='Отчет о продажах')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

# админ
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Админ-панель')

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = Customer.query.all()
    return render_template('admin_users.html', title='Управление пользователями', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = Customer.query.get_or_404(user_id)
    form = AdminEditUserForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Пользователь обновлен.')
        return redirect(url_for('admin_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.role.data = user.role
    return render_template('admin_edit_user.html', title='Редактировать пользователя', form=form, user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash('Вы не можете удалить свой собственный аккаунт.')
        return redirect(url_for('admin_users'))
    user = Customer.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален.')
    return redirect(url_for('admin_users'))

@app.route('/admin/records')
@login_required
@admin_required
def admin_records():
    records = Record.query.all()
    return render_template('admin_records.html', title='Управление пластинками', records=records)

@app.route('/admin/ensembles')
@login_required
@admin_required
def admin_ensembles():
    ensembles = Ensemble.query.all()
    return render_template('admin_ensembles.html', title='Управление ансамблями', ensembles=ensembles)