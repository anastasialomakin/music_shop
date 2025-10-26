import os
from app import app, db
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, session, request, abort, send_from_directory, jsonify
from functools import wraps
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Record, Release, Band, User, CustomerProfile, ManufacturerProfile, Order, OrderItem, Genre, Artist, Composition
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CheckoutForm, ManufacturerProfileForm, RecordForm, AdminEditUserForm, GenreForm, ArtistForm, BandForm, CompositionForm, ReleaseForm
from sqlalchemy import or_

# --- ДЕКОРАТОРЫ ДЛЯ РОЛЕЙ ---
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


# --- ПУБЛИЧНЫЕ МАРШРУТЫ ---

@app.route('/search_suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = Release.query.join(Band).filter(
        or_(
            Release.title.ilike(f'{q}%'),
            Band.name.ilike(f'{q}%')
        )
    ).limit(5).all()

    suggestions = [f"{r.title} ({r.band.name})" for r in results]
    return jsonify(suggestions)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    selected_band = request.args.get('band', type=int)
    selected_genre = request.args.get('genre', type=int)
    selected_sort = request.args.get('sort', 'title_asc')
    search_query = request.args.get('q', '').strip()
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)

    # базовый запрос
    query = Release.query.join(Band).join(Genre)

    # фильтры
    if selected_band:
        query = query.filter(Release.band_id == selected_band)
    if selected_genre:
        query = query.filter(Band.genre_id == selected_genre)
    if year_min is not None:
        query = query.filter(Release.release_year >= year_min)
    if year_max is not None:
        query = query.filter(Release.release_year <= year_max)

    # поиск
    if search_query:
        query = query.filter(
            or_(
                Release.title.ilike(f'%{search_query}%'),
                Band.name.ilike(f'%{search_query}%')
            )
        )

    # сортировка
    if selected_sort == 'title_asc':
        query = query.order_by(Release.title.asc())
    elif selected_sort == 'title_desc':
        query = query.order_by(Release.title.desc())
    elif selected_sort == 'year_asc':
        query = query.order_by(Release.release_year.asc())
    elif selected_sort == 'year_desc':
        query = query.order_by(Release.release_year.desc())

    # пагинация
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    releases = pagination.items

    bands = Band.query.all()
    genres = Genre.query.all()

    # автоподсказки для текущего запроса
    autocomplete_options = []
    if search_query:
        autocomplete_options = Release.query.join(Band).filter(
            or_(
                Release.title.ilike(f'{search_query}%'),
                Band.name.ilike(f'{search_query}%')
            )
        ).limit(5).all()

    return render_template(
        'index.html',
        releases=releases,
        bands=bands,
        genres=genres,
        selected_band=selected_band,
        selected_genre=selected_genre,
        selected_sort=selected_sort,
        search_query=search_query,
        autocomplete_options=autocomplete_options,
        pagination=pagination,
        year_min=year_min,
        year_max=year_max
    )

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/bands')
def bands_list():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    selected_sort = request.args.get('sort', 'name_asc')

    # Базовый запрос
    query = Band.query

    # Поиск по названию
    if search_query:
        query = query.filter(Band.name.ilike(f'%{search_query}%'))

    # Сортировка
    if selected_sort == 'name_asc':
        query = query.order_by(Band.name.asc())
    elif selected_sort == 'name_desc':
        query = query.order_by(Band.name.desc())

    # Пагинация: 8 групп на страницу
    pagination = query.paginate(page=page, per_page=8, error_out=False)
    bands = pagination.items

    return render_template(
        'bands_list.html',
        bands=bands,
        search_query=search_query,
        selected_sort=selected_sort,
        pagination=pagination
    )

@app.route('/record/<int:id>')
def record_detail(id):
    record = Record.query.get_or_404(id)
    return render_template('record_detail.html', title=record.title, record=record)

@app.route('/release/<int:id>')
def release_detail(id):
    release = Release.query.get_or_404(id)
    return render_template('release_detail.html', title=release.title, release=release)

@app.route('/band/<int:id>')
def band_detail(id):
    band = Band.query.get_or_404(id)
    return render_template('band_detail.html', title=band.name, band=band)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Это имя пользователя уже занято. Пожалуйста, выберите другое.')
            return redirect(url_for('register'))
        new_user = User(username=form.username.data, role='user')
        new_user.set_password(form.password.data)
        new_customer_profile = CustomerProfile(user=new_user)
        db.session.add(new_user)
        db.session.add(new_customer_profile)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- ЛИЧНЫЙ КАБИНЕТ ---
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Личный кабинет')

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role == 'user':
        form = EditProfileForm()
    elif current_user.role == 'manufacturer':
        form = ManufacturerProfileForm()
    else:
        form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.password.data:
            current_user.set_password(form.password.data)
        if current_user.role == 'user':
            if not current_user.customer_profile:
                current_user.customer_profile = CustomerProfile()
            current_user.customer_profile.shipping_address = form.shipping_address.data
        elif current_user.role == 'manufacturer':
            if not current_user.manufacturer_profile:
                current_user.manufacturer_profile = ManufacturerProfile()
            current_user.manufacturer_profile.company_name = form.company_name.data
            current_user.manufacturer_profile.company_address = form.company_address.data
        db.session.commit()
        flash('Ваш профиль был успешно обновлен.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        if current_user.role == 'user' and current_user.customer_profile:
            form.shipping_address.data = current_user.customer_profile.shipping_address
        elif current_user.role == 'manufacturer' and current_user.manufacturer_profile:
            form.company_name.data = current_user.manufacturer_profile.company_name
            form.company_address.data = current_user.manufacturer_profile.company_address
    return render_template('edit_profile.html', title='Редактировать профиль', form=form)

# --- ЛОГИКА КОРЗИНЫ И ЗАКАЗОВ ---
@app.route('/add_to_cart/<int:record_id>', methods=['POST'])
@login_required
def add_to_cart(record_id):
    record = Record.query.get_or_404(record_id)
    cart = session.get('cart', {})
    record_id_str = str(record_id)
    qty_to_add = int(request.form.get('quantity', 1))
    
    # текущий кол-во в корзине
    current_qty = cart.get(record_id_str, 0)
    
    # нельзя добавить больше, чем есть на складе
    if current_qty + qty_to_add > record.stock_quantity:
        flash(f'Нельзя добавить больше {record.stock_quantity} шт. в корзину.', 'warning')
        qty_to_add = max(0, record.stock_quantity - current_qty)
    
    if qty_to_add > 0:
        cart[record_id_str] = current_qty + qty_to_add
        session['cart'] = cart
        flash(f'{qty_to_add} шт. добавлено в корзину.', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/decrease_cart_item/<int:record_id>', methods=['POST'])
@login_required
def decrease_cart_item(record_id):
    cart = session.get('cart', {})
    record_id_str = str(record_id)
    if record_id_str in cart:
        cart[record_id_str] -= 1
        if cart[record_id_str] <= 0:
            del cart[record_id_str]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:record_id>', methods=['POST'])
@login_required
def remove_from_cart(record_id):
    cart = session.get('cart', {})
    record_id_str = str(record_id)
    if record_id_str in cart:
        del cart[record_id_str]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    session['cart'] = {}
    return redirect(url_for('cart'))

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

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # --- гарантируем, что у пользователя есть профиль ---
    if not current_user.customer_profile:
        profile = CustomerProfile(user_id=current_user.id, shipping_address="")
        db.session.add(profile)
        db.session.commit()

    form = CheckoutForm()
    cart_items_dict = session.get('cart', {})

    if not cart_items_dict:
        flash('Ваша корзина пуста, невозможно оформить заказ.')
        return redirect(url_for('cart'))

    record_ids = [int(x) for x in cart_items_dict.keys()]
    records = Record.query.filter(Record.id.in_(record_ids)).all()

    total_amount = sum(rec.price * cart_items_dict[str(rec.id)] for rec in records)

    if form.validate_on_submit():
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status='В обработке',
            payment_method=form.payment_method.data
        )
        db.session.add(new_order)

        for rec in records:
            qty = cart_items_dict[str(rec.id)]

            # уменьшаем склад
            rec.stock_quantity -= qty

            # создаём позиции заказа
            db.session.add(OrderItem(
                order=new_order,
                record_id=rec.id,
                quantity=qty,
                price_at_purchase=rec.price
            ))

        # обновляем адрес доставки
        current_user.customer_profile.shipping_address = form.shipping_address.data

        db.session.commit()
        session['cart'] = {}
        flash('Ваш заказ успешно оформлен!')
        return redirect(url_for('orders_list'))

    # подставляем адрес при открытии страницы
    if request.method == 'GET':
        form.shipping_address.data = current_user.customer_profile.shipping_address

    return render_template(
        'checkout.html',
        title='Оформление заказа',
        form=form,
        total=total_amount,
        items=records,
        cart=cart_items_dict
    )


@app.route('/orders')
@login_required
def orders_list():
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', title='Мои заказы', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    return render_template('order_detail.html', title=f'Заказ #{order.id}', order=order)

# --- РАЗДЕЛ ПРОИЗВОДИТЕЛЯ (ЛЕЙБЛА) ---

@app.route('/my-records')
@login_required
@manufacturer_required
def my_records():
    records = current_user.manufacturer_profile.records.all()
    return render_template('my_records.html', title='Мои пластинки', records=records)


@app.route('/my-records/add', methods=['GET', 'POST'])
@login_required
@manufacturer_required
def add_record():
    form = RecordForm()
    form.release.choices = [(r.id, f"{r.band.name} - {r.title} ({r.release_year})") for r in Release.query.order_by(Release.title).all()]

    if form.validate_on_submit():
        filename = None
        if form.cover_image.data:
            f = form.cover_image.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_record = Record(
            title=form.title.data,
            release_id=form.release.data,
            release_year=form.release_year.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            record_type=form.record_type.data,
            description=form.description.data,
            cover_image_url=filename,
            manufacturer_profile_id=current_user.manufacturer_profile.id
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Новая пластинка успешно добавлена!')
        return redirect(url_for('my_records'))
        
    return render_template('record_form.html', title='Добавить пластинку', form=form)


@app.route('/my-records/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@manufacturer_required
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)
    if record.manufacturer_profile_id != current_user.manufacturer_profile.id:
        abort(403)
        
    form = RecordForm(obj=record)
    form.release.choices = [(r.id, f"{r.band.name} - {r.title} ({r.release_year})") for r in Release.query.order_by(Release.title).all()]
    
    if form.validate_on_submit():
        record.title = form.title.data
        record.release_id = form.release.data
        record.release_year = form.release_year.data
        record.price = form.price.data
        record.stock_quantity = form.stock_quantity.data
        record.record_type = form.record_type.data
        record.description = form.description.data
        
        if form.cover_image.data:
            f = form.cover_image.data
            filename = secure_filename(f.filename)
            # TODO: Удалить старый файл обложки, если он есть и отличается
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            record.cover_image_url = filename

        db.session.commit()
        flash('Данные о пластинке обновлены.')
        return redirect(url_for('my_records'))
        
    elif request.method == 'GET':
        form.release.data = record.release_id

    return render_template('record_form.html', title='Редактировать пластинку', form=form)

@app.route('/my-records/delete/<int:record_id>', methods=['POST'])
@login_required
@manufacturer_required
def delete_record(record_id):
    record = Record.query.get_or_404(record_id)
    if record.manufacturer_profile_id != current_user.manufacturer_profile.id:
        abort(403)
    db.session.delete(record)
    db.session.commit()
    flash('Пластинка была удалена.')
    return redirect(url_for('my_records'))

@app.route('/sales-report')
@login_required
@manufacturer_required
def sales_report():
    total_sold = 0
    total_revenue = 0
    for record in current_user.manufacturer_profile.records:
        total_sold += 1
        total_revenue += record.price
    return render_template('sales_report.html', title='Отчет о продажах', total_sold=total_sold, total_revenue=total_revenue)


@app.route('/top_selling')
def top_selling():
    max_stock = 50  # если это фикс
    records = Record.query.all()

    # посчитаем "сколько продано" на лету
    enriched = []
    for r in records:
        sold = max_stock - r.stock_quantity
        revenue = sold * float(r.price)
        enriched.append((r, sold, revenue))

    # сортировка: по sold убыв
    enriched.sort(key=lambda x: x[1], reverse=True)

    # возьмём топ-10
    enriched = enriched[:10]

    return render_template('top_selling.html', records=enriched)


# --- АДМИН-ПАНЕЛЬ ---

def get_admin_paginated(Model, per_page=15):
    page = request.args.get('page', 1, type=int)
    pagination = Model.query.order_by(Model.id).paginate(page=page, per_page=per_page)
    return pagination



@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_records = db.session.query(db.func.sum(Record.stock_quantity)).scalar() or 0
    total_orders = Order.query.count()

    return render_template(
        'admin_dashboard.html',
        title='Админ-панель',
        total_users=total_users,
        total_records=total_records,
        total_orders=total_orders
    )



@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users_list.html', title='Управление пользователями', users=users)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', title=f'Профиль {user.username}', user=user)


@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm()

    if form.validate_on_submit():
        old_role = user.role
        
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)

        # Логика смены профиля при смене роли
        if old_role != user.role:
            # Если стал производителем
            if user.role == 'manufacturer':
                if user.customer_profile: db.session.delete(user.customer_profile)
                if not user.manufacturer_profile:
                    user.manufacturer_profile = ManufacturerProfile(company_name=f"Компания {user.username}")
            # Если стал покупателем
            elif user.role == 'user':
                if user.manufacturer_profile: db.session.delete(user.manufacturer_profile)
                if not user.customer_profile:
                    user.customer_profile = CustomerProfile()

        db.session.commit()
        flash('Данные пользователя обновлены.')
        return redirect(url_for('admin_users'))
        
    elif request.method == 'GET':
        form.username.data = user.username
        form.role.data = user.role

    return render_template('admin/user_edit.html', title='Редактировать пользователя', form=form, user=user)


@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    # Защита от удаления самого себя
    if user_id == current_user.id:
        flash('Вы не можете удалить свой собственный аккаунт.', 'error')
        return redirect(url_for('admin_users'))
        
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Пользователь был успешно удален.')
    return redirect(url_for('admin_users'))

# --- АДМИН: УПРАВЛЕНИЕ ЖАНРАМИ ---

@app.route('/admin/genres')
@login_required
@admin_required
def admin_genres():
    genres = Genre.query.order_by('name').all()
    return render_template('admin/genres_list.html', genres=genres)

@app.route('/admin/genre/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_genre():
    form = GenreForm()
    if form.validate_on_submit():
        new_genre = Genre(name=form.name.data)
        db.session.add(new_genre)
        db.session.commit()
        flash('Жанр успешно добавлен.')
        return redirect(url_for('admin_genres'))
    return render_template('admin/genre_form.html', title='Добавить жанр', form=form)

@app.route('/admin/genre/edit/<int:genre_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    if form.validate_on_submit():
        genre.name = form.name.data
        db.session.commit()
        flash('Жанр успешно обновлен.')
        return redirect(url_for('admin_genres'))
    return render_template('admin/genre_form.html', title='Редактировать жанр', form=form)

@app.route('/admin/genre/delete/<int:genre_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash('Жанр удален.')
    return redirect(url_for('admin_genres'))

# --- АДМИН: УПРАВЛЕНИЕ АРТИСТАМИ ---

@app.route('/admin/artists')
@login_required
@admin_required
def admin_artists():
    artists = Artist.query.order_by('name').all()
    return render_template('admin/artists_list.html', artists=artists)

@app.route('/admin/artist/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_artist():
    form = ArtistForm()
    if form.validate_on_submit():
        new_artist = Artist(name=form.name.data, bio=form.bio.data)
        db.session.add(new_artist)
        db.session.commit()
        flash('Артист успешно добавлен.')
        return redirect(url_for('admin_artists'))
    return render_template('admin/artist_form.html', title='Добавить артиста', form=form)

@app.route('/admin/artist/edit/<int:artist_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    if form.validate_on_submit():
        artist.name = form.name.data
        artist.bio = form.bio.data
        db.session.commit()
        flash('Данные артиста успешно обновлены.')
        return redirect(url_for('admin_artists'))
    return render_template('admin/artist_form.html', title='Редактировать артиста', form=form)

@app.route('/admin/artist/delete/<int:artist_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Артист удален.')
    return redirect(url_for('admin_artists'))


# --- АДМИН: УПРАВЛЕНИЕ ГРУППАМИ ---

@app.route('/admin/bands')
@login_required
@admin_required
def admin_bands():
    bands = Band.query.order_by('name').all()
    return render_template('admin/bands_list.html', bands=bands)

@app.route('/admin/band/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_band():
    form = BandForm()
    # Загружаем списки для полей выбора
    form.genre.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.members.choices = [(a.id, a.name) for a in Artist.query.order_by('name').all()]

    if form.validate_on_submit():
        new_band = Band(name=form.name.data, bio=form.bio.data, genre_id=form.genre.data)
        # Находим объекты артистов по их id и добавляем в группу
        selected_members = Artist.query.filter(Artist.id.in_(form.members.data)).all()
        new_band.members = selected_members
        
        db.session.add(new_band)
        db.session.commit()
        flash('Группа успешно добавлена.')
        return redirect(url_for('admin_bands'))
    return render_template('admin/band_form.html', title='Добавить группу', form=form)

@app.route('/admin/band/edit/<int:band_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_band(band_id):
    band = Band.query.get_or_404(band_id)
    form = BandForm(obj=band)
    form.genre.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.members.choices = [(a.id, a.name) for a in Artist.query.order_by('name').all()]
    
    if form.validate_on_submit():
        band.name = form.name.data
        band.bio = form.bio.data
        band.genre_id = form.genre.data
        selected_members = Artist.query.filter(Artist.id.in_(form.members.data)).all()
        band.members = selected_members
        
        db.session.commit()
        flash('Данные группы успешно обновлены.')
        return redirect(url_for('admin_bands'))

    elif request.method == 'GET':
        form.genre.data = band.genre_id
        form.members.data = [member.id for member in band.members]

    return render_template('admin/band_form.html', title='Редактировать группу', form=form)

@app.route('/admin/band/delete/<int:band_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_band(band_id):
    band = Band.query.get_or_404(band_id)
    db.session.delete(band)
    db.session.commit()
    flash('Группа удалена.')
    return redirect(url_for('admin_bands'))


# --- АДМИН: УПРАВЛЕНИЕ КОМПОЗИЦИЯМИ ---

@app.route('/admin/compositions')
@login_required
@admin_required
def admin_compositions():
    compositions = Composition.query.order_by('title').all()
    return render_template('admin/compositions_list.html', compositions=compositions)

@app.route('/admin/composition/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_composition():
    form = CompositionForm()
    # Загружаем список групп в поле выбора
    form.author_band.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]

    if form.validate_on_submit():
        new_composition = Composition(
            title=form.title.data,
            author_band_id=form.author_band.data,
            duration=form.duration.data
        )
        db.session.add(new_composition)
        db.session.commit()
        flash('Композиция успешно добавлена.')
        return redirect(url_for('admin_compositions'))
    return render_template('admin/composition_form.html', title='Добавить композицию', form=form)

@app.route('/admin/composition/edit/<int:composition_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_composition(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    form = CompositionForm(obj=composition)
    form.author_band.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]
    
    if form.validate_on_submit():
        composition.title = form.title.data
        composition.author_band_id = form.author_band.data
        composition.duration = form.duration.data
        db.session.commit()
        flash('Данные композиции успешно обновлены.')
        return redirect(url_for('admin_compositions'))

    # При GET-запросе предзаполняем поле автора
    elif request.method == 'GET':
        form.author_band.data = composition.author_band_id

    return render_template('admin/composition_form.html', title='Редактировать композицию', form=form)

@app.route('/admin/composition/delete/<int:composition_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_composition(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    db.session.delete(composition)
    db.session.commit()
    flash('Композиция удалена.')
    return redirect(url_for('admin_compositions'))


@app.route('/admin/releases')
@login_required
@admin_required
def admin_releases():
    releases = Release.query.order_by('title').all()
    return render_template('admin/releases_list.html', releases=releases)

@app.route('/admin/release/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_release():
    form = ReleaseForm()
    # Загружаем только список групп. Список композиций будет пуст.
    form.band.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]
    form.compositions.choices = []

    if form.validate_on_submit():
        new_release = Release(
            title=form.title.data,
            release_year=form.release_year.data,
            band_id=form.band.data
        )
        selected_compositions = Composition.query.filter(Composition.id.in_(form.compositions.data)).all()
        new_release.compositions = selected_compositions
        
        db.session.add(new_release)
        db.session.commit()
        flash('Релиз успешно добавлен.')
        return redirect(url_for('admin_releases'))
        
    return render_template('admin/release_form.html', title='Добавить релиз', form=form)

@app.route('/admin/release/edit/<int:release_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_release(release_id):
    release = Release.query.get_or_404(release_id)
    form = ReleaseForm(obj=release)
    form.band.choices = [(b.id, b.name) for b in Band.query.order_by('name').all()]
    # При редактировании сразу загружаем композиции ВЫБРАННОЙ группы
    form.compositions.choices = [(c.id, c.title) for c in release.band.compositions]

    if form.validate_on_submit():
        release.title = form.title.data
        release.release_year = form.release_year.data
        release.band_id = form.band.data
        selected_compositions = Composition.query.filter(Composition.id.in_(form.compositions.data)).all()
        release.compositions = selected_compositions
        
        db.session.commit()
        flash('Данные релиза обновлены.')
        return redirect(url_for('admin_releases'))
        
    elif request.method == 'GET':
        form.band.data = release.band_id
        form.compositions.data = [c.id for c in release.compositions]

    return render_template('admin/release_form.html', title='Редактировать релиз', form=form)

@app.route('/admin/release/delete/<int:release_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_release(release_id):
    release = Release.query.get_or_404(release_id)
    db.session.delete(release)
    db.session.commit()
    flash('Релиз удален.')
    return redirect(url_for('admin_releases'))


# --- API-маршрут для JavaScript ---
@app.route('/api/compositions_by_band/<int:band_id>')
@login_required
@admin_required
def api_compositions_by_band(band_id):
    band = Band.query.get_or_404(band_id)
    compositions_list = [{'id': comp.id, 'title': comp.title} for comp in band.compositions]
    return jsonify(compositions_list)