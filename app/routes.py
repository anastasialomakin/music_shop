from app import app
from flask import render_template, flash, redirect, url_for, session, request, abort
from app import db
from functools import wraps
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Record, Band, User, Composition, Order, Release
from app.forms import BandForm, LoginForm, EditProfileForm, RecordForm, AdminEditUserForm

@app.route('/')
@app.route('/index')
def index():
    """
    Главная страница (каталог товаров).
    шаблон index.html нужно будет обновить
    для использования новых полей модели Record.
    """
    records_from_db = Record.query.all()
    return render_template('index.html', title='Каталог', records=records_from_db)

@app.route('/record/<int:id>')
def record_detail(id):
    """
    Детали пластинки. Шаблон record_detail.html нужно будет обновить.
    """
    record = Record.query.get_or_404(id)
    return render_template('record_detail.html', title=record.title, record=record)

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.shipping_address = form.shipping_address.data

        if form.password.data:
            current_user.set_password(form.password.data)
            
        db.session.commit()
        flash('Ваш профиль был обновлен.')
        return redirect(url_for('profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.shipping_address.data = current_user.shipping_address
            
    return render_template('profile.html', title='Личный кабинет', form=form)


@app.route('/bands')
def bands_list():
    bands = Band.query.all()
    return render_template('bands_list.html', title='Все группы', bands=bands)

@app.route('/band/<int:id>')
def band_detail(id):
    band = Band.query.get_or_404(id)
    records = db.session.query(Record).join(Record.releases).join(Composition, Composition.id == Release.composition_id).filter(Composition.band_id == band.id).distinct().all()
    return render_template('band_detail.html', title=band.name, band=band, records=records)


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
        subtotal = record.price * quantity
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

@app.route('/orders')
@login_required
def orders_list():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.date.desc()).all()
    return render_template('orders.html', title='Мои заказы', orders=orders)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Ваша корзина пуста.')
        return redirect(url_for('cart'))

    record_ids = [int(id) for id in cart_items.keys()]
    records_in_cart = Record.query.filter(Record.id.in_(record_ids)).all()

    for record in records_in_cart:
        quantity = cart_items.get(str(record.id))
        if record.in_stock and quantity > 0:
            new_order_item = Order(
                total=(record.price * quantity),
                status='В обработке',
                quantity=quantity,
                customer_id=current_user.id,
                record_id=record.id
            )
            db.session.add(new_order_item)

    db.session.commit()
    session.pop('cart', None)
    flash('Ваш заказ успешно оформлен!')
    return redirect(url_for('orders_list'))


def manufacturer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'manufacturer':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function


@app.route('/my-records')
@login_required
@manufacturer_required
def my_records():
    if not current_user.manufacturer:
        flash('Ваш аккаунт не связан с профилем производителя.')
        return redirect(url_for('index'))
    records = Record.query.filter_by(manufacturer_id=current_user.manufacturer.id).all()
    return render_template('my_records.html', title='Мои пластинки', records=records)

@app.route('/my-records/add', methods=['GET', 'POST'])
@login_required
@manufacturer_required
def add_record():
    form = RecordForm()
    form.ensemble.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]

    if form.validate_on_submit():
        new_record = Record(
            title=form.title.data,
            release_year=form.release_year.data,
            price=form.retail_price.data,
            in_stock=form.stock_quantity.data > 0,
            description=form.description.data,
            manufacturer_id=current_user.manufacturer.id,
            type='Студийная запись' 
        )
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
    form.ensemble.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]
    
    if form.validate_on_submit():
        record.title = form.title.data
        record.release_year = form.release_year.data
        record.price = form.retail_price.data
        record.in_stock = form.stock_quantity.data > 0
        record.description = form.description.data
        
        
        db.session.commit()
        flash('Данные о пластинке обновлены.')
        return redirect(url_for('my_records'))
        
    elif request.method == 'GET':
        form.retail_price.data = record.price
        form.stock_quantity.data = 1 if record.in_stock else 0

    return render_template('record_form.html', title='Редактировать пластинку', form=form)


@app.route('/sales-report')
@login_required
@manufacturer_required
def sales_report():
    return render_template('sales_report.html', title='Отчет о продажах')


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Админ-панель')

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', title='Управление пользователями', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(obj=user)
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
    user = User.query.get_or_404(user_id)
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

@app.route('/admin/bands')
@login_required
@admin_required
def admin_bands():
    bands = Band.query.all()
    return render_template('admin_bands.html', title='Управление группами', bands=bands)