from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



records_has_releases = db.Table('records_has_releases',
    db.Column('records_idrecords', db.Integer, db.ForeignKey('records.idrecords'), primary_key=True),
    db.Column('releases_idreleases', db.Integer, db.ForeignKey('releases.idreleases'), primary_key=True)
)



class Manufacturer(db.Model):
    __tablename__ = 'manufacturer'
    id = db.Column('idmanufacturer', db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    user_id = db.Column('users_idusers', db.Integer, db.ForeignKey('users.idusers'), unique=True)

    records = db.relationship('Record', back_populates='manufacturer')
    
    def __repr__(self):
        return f'<Manufacturer {self.name}>'

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column('idrecords', db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    in_stock = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    type = db.Column(db.String(45), nullable=False)

    manufacturer_id = db.Column('manufacturer_idmanufacturer', db.Integer, db.ForeignKey('manufacturer.idmanufacturer'), nullable=False)

    manufacturer = db.relationship('Manufacturer', back_populates='records')
    
    releases = db.relationship('Release', secondary=records_has_releases, back_populates='records')

    def __repr__(self):
        return f'<Record {self.title}>'

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column('idgenres', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    bands = db.relationship('Band', back_populates='genre')
    releases = db.relationship('Release', back_populates='genre')

    def __repr__(self):
        return f'<Genre {self.name}>'

class Band(db.Model):
    __tablename__ = 'bands'
    id = db.Column('idbands', db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    bio = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    
    genre_id = db.Column('genres_idgenres', db.Integer, db.ForeignKey('genres.idgenres'), nullable=False)

    genre = db.relationship('Genre', back_populates='bands')

    artists = db.relationship('Artist', back_populates='band')
    compositions = db.relationship('Composition', back_populates='band')
    releases = db.relationship('Release', back_populates='band')

    def __repr__(self):
        return f'<Band {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column('idartists', db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    bio = db.Column(db.Text)
    role = db.Column(db.String(45), nullable=False)
    
    band_id = db.Column('bands_idbands', db.Integer, db.ForeignKey('bands.idbands'), nullable=False)

    band = db.relationship('Band', back_populates='artists')

    def __repr__(self):
        return f'<Artist {self.name}>'

class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column('idcompositions', db.Integer, primary_key=True)
    title = db.Column(db.String(45), nullable=False)
    duration = db.Column(db.Time, nullable=False)
    
    band_id = db.Column('bands_idbands', db.Integer, db.ForeignKey('bands.idbands'), nullable=False)

    band = db.relationship('Band', back_populates='compositions')

    def __repr__(self):
        return f'<Composition {self.title}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column('idcustomers', db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    shipping_address = db.Column(db.Text)
    role = db.Column(db.String(45), nullable=False)

    manufacturer = db.relationship('Manufacturer', backref='user', uselist=False)
    
    orders = db.relationship('Order', back_populates='customer')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Customer {self.username}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column('idorders', db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    customer_id = db.Column('customers_idcustomers', db.Integer, db.ForeignKey('customers.idcustomers'), nullable=False)
    record_id = db.Column('records_idrecords', db.Integer, db.ForeignKey('records.idrecords'), nullable=False)

    customer = db.relationship('Customer', back_populates='orders')
    record = db.relationship('Record')

    def __repr__(self):
        return f'<Order {self.id}>'

class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column('idreleases', db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)

    composition_id = db.Column('compositions_idcompositions', db.Integer, db.ForeignKey('compositions.idcompositions'), nullable=False)
    genre_id = db.Column('genres_idgenres', db.Integer, db.ForeignKey('genres.idgenres'), nullable=False)
    band_id = db.Column('bands_idbands', db.Integer, db.ForeignKey('bands.idbands'), nullable=False)

    composition = db.relationship('Composition')
    genre = db.relationship('Genre', back_populates='releases')
    band = db.relationship('Band', back_populates='releases')

    records = db.relationship('Record', secondary=records_has_releases, back_populates='releases')

    def __repr__(self):
        return f'<Release {self.name}>'