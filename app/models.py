from app import db, login_manager
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# связи многие-ко-многим

# группа <-> музыкант
band_members = db.Table('band_members',
    db.Column('band_id', db.Integer, db.ForeignKey('bands.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True)
)

# релиз <-> композиция
release_compositions = db.Table('release_compositions',
    db.Column('release_id', db.Integer, db.ForeignKey('releases.id'), primary_key=True),
    db.Column('composition_id', db.Integer, db.ForeignKey('compositions.id'), primary_key=True)
)

# основное

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'manufacturer', 'admin'), nullable=False)

    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    manufacturer_profile = db.relationship('ManufacturerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    shipping_address = db.Column(db.Text, nullable=True)

class ManufacturerProfile(db.Model):
    __tablename__ = 'manufacturer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    company_address = db.Column(db.String(255))
    records = db.relationship('Record', backref='manufacturer', lazy='dynamic')

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    bands = db.relationship('Band', backref='genre', lazy='dynamic')

class Band(db.Model):
    __tablename__ = 'bands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    
    members = db.relationship('Artist', secondary=band_members, back_populates='bands')
    compositions = db.relationship('Composition', backref='author_band', lazy='dynamic')
    releases = db.relationship('Release', backref='band', lazy='dynamic')

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    bands = db.relationship('Band', secondary=band_members, back_populates='members')

class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)
    author_band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=False)
    releases = db.relationship('Release', secondary=release_compositions, back_populates='compositions')

class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    cover_image_url = db.Column(db.String(255))
    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=False)
    records = db.relationship('Record', backref='release', lazy='dynamic')
    compositions = db.relationship('Composition', secondary=release_compositions, back_populates='releases')

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(255))
    record_type = db.Column(db.String(45))
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    manufacturer_profile_id = db.Column(db.Integer, db.ForeignKey('manufacturer_profiles.id'), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50))
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)
    record = db.relationship('Record')