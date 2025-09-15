# заглушка бд пока что

from app import db
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 

# пластинка <-> композиция
record_compositions = db.Table('record_compositions',
    db.Column('record_id', db.Integer, db.ForeignKey('records.id'), primary_key=True),
    db.Column('composition_id', db.Integer, db.ForeignKey('compositions.id'), primary_key=True)
)

# ансамбль <-> музыкант
ensemble_members = db.Table('ensemble_members',
    db.Column('ensemble_id', db.Integer, db.ForeignKey('ensembles.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True)
)

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    format = db.Column(db.String(50))
    retail_price = db.Column(db.Numeric(10, 2), nullable=False)
    wholesale_price = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(255))
    
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'))

    compositions = db.relationship('Composition', secondary=record_compositions, back_populates='records')
    order_items = db.relationship('OrderItem', back_populates='record')
    manufacturer = db.relationship('Manufacturer', back_populates='records')

    def __repr__(self):
        return f'<Record {self.title}>'

class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration_seconds = db.Column(db.Integer)
    creation_year = db.Column(db.Integer)

    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'))

    records = db.relationship('Record', secondary=record_compositions, back_populates='compositions')

    ensemble = db.relationship('Ensemble', back_populates='compositions')

    def __repr__(self):
        return f'<Composition {self.title}>'

class Ensemble(db.Model):
    __tablename__ = 'ensembles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    compositions = db.relationship('Composition', back_populates='ensemble')
    members = db.relationship('Artist', secondary=ensemble_members, back_populates='ensembles')

    def __repr__(self):
        return f'<Ensemble {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)

    ensembles = db.relationship('Ensemble', secondary=ensemble_members, back_populates='members')

    def __repr__(self):
        return f'<Artist {self.name}>'

class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    user = db.relationship('Customer', backref=db.backref('manufacturer', uselist=False))

    records = db.relationship('Record', back_populates='manufacturer')
    
    def __repr__(self):
        return f'<Manufacturer {self.name}>'

class Customer(UserMixin, db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    shipping_address = db.Column(db.Text)

    role = db.Column(db.String(20), nullable=False, default='user')

    orders = db.relationship('Order', back_populates='customer')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Customer {self.username}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50), default='Processing')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    customer = db.relationship('Customer', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Numeric(10, 2), nullable=False)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'))

    order = db.relationship('Order', back_populates='items')
    record = db.relationship('Record', back_populates='order_items')