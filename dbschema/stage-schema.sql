CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE artists (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	bio TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE genres (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(12) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE TABLE bands (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	bio TEXT, 
	genre_id INTEGER, cover_image_url VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(genre_id) REFERENCES genres (id)
);
CREATE TABLE customer_profiles (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	shipping_address TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (user_id)
);
CREATE TABLE manufacturer_profiles (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	company_name VARCHAR(150) NOT NULL, 
	company_address VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (user_id)
);
CREATE TABLE orders (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	order_date DATETIME, 
	total_amount NUMERIC(10, 2) NOT NULL, 
	status VARCHAR(50) NOT NULL, 
	payment_method VARCHAR(50), shipping_address TEXT, comment TEXT, delivery_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE band_members (
	band_id INTEGER NOT NULL, 
	artist_id INTEGER NOT NULL, 
	PRIMARY KEY (band_id, artist_id), 
	FOREIGN KEY(artist_id) REFERENCES artists (id), 
	FOREIGN KEY(band_id) REFERENCES bands (id)
);
CREATE TABLE releases (
	id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	release_year INTEGER, 
	band_id INTEGER NOT NULL, cover_image_url VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(band_id) REFERENCES bands (id)
);
CREATE TABLE records (
	id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	release_year INTEGER, 
	price NUMERIC(10, 2) NOT NULL, 
	stock_quantity INTEGER NOT NULL, 
	description TEXT, 
	cover_image_url VARCHAR(255), 
	record_type VARCHAR(45), 
	release_id INTEGER NOT NULL, 
	manufacturer_profile_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(manufacturer_profile_id) REFERENCES manufacturer_profiles (id), 
	FOREIGN KEY(release_id) REFERENCES releases (id)
);
CREATE TABLE release_compositions (
	release_id INTEGER NOT NULL, 
	composition_id INTEGER NOT NULL, 
	PRIMARY KEY (release_id, composition_id), 
	FOREIGN KEY(composition_id) REFERENCES compositions (id), 
	FOREIGN KEY(release_id) REFERENCES releases (id)
);
CREATE TABLE order_items (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	record_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	price_at_purchase NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(record_id) REFERENCES records (id)
);
CREATE TABLE IF NOT EXISTS "compositions" (
	id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	duration INTEGER, 
	author_band_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_band_id) REFERENCES bands (id)
);
