from app import db
from app.models import Genre, Band, Artist, Composition, Release, Record, User, ManufacturerProfile
from werkzeug.security import generate_password_hash
import random

def seed_database():
    # ------------------
    # Проверяем, есть ли админ
    # ------------------
    admin_exists = User.query.filter_by(role='admin').first()
    if admin_exists:
        print("Администратор найден. Seed пропущен.")
        return

    print("Администратор не найден. Запускаем seed базы...")

    # ------------------
    # Создаём администратора
    # ------------------
    admin_user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin_user)
    db.session.commit()
    print("✅ Администратор создан: admin / admin123")

    # ------------------
    # Жанры
    # ------------------
    genres = ['Rock', 'Jazz', 'Pop', 'Hip-Hop', 'Electronic']
    genre_objs = [Genre(name=g) for g in genres]
    db.session.add_all(genre_objs)
    db.session.commit()

    # ------------------
    # Артисты и группы
    # ------------------
    bands = []
    artists = []
    for i in range(5):
        artist = Artist(name=f'Artist {i+1}', bio='Биография артиста')
        band = Band(name=f'Band {i+1}', bio='Описание группы', genre=genre_objs[i])
        band.members.append(artist)
        db.session.add(artist)
        db.session.add(band)
        bands.append(band)
        artists.append(artist)
    db.session.commit()

    # ------------------
    # Композиции и релизы
    # ------------------
    releases = []
    for i, band in enumerate(bands):
        release = Release(
            title=f'Release {i+1}',
            release_year=2000 + i,
            cover_image_url=f'release_{i+1}.jpg',
            band=band
        )
        db.session.add(release)
        releases.append(release)

        for j in range(5):
            comp = Composition(
                title=f'Song {i+1}.{j+1}',
                duration=random.randint(120, 300),
                author_band_id=band.id
            )
            comp.releases.append(release)
            db.session.add(comp)

    db.session.commit()

    # ------------------
    # Пользователь-производитель
    # ------------------
    manufacturer_user = User(
        username='manufacturer1',
        password_hash=generate_password_hash('password'),
        role='manufacturer'
    )
    db.session.add(manufacturer_user)
    db.session.commit()

    manufacturer_profile = ManufacturerProfile(
        user_id=manufacturer_user.id,
        company_name='Vinyl Factory',
        company_address='123 Music Ave'
    )
    db.session.add(manufacturer_profile)
    db.session.commit()

    # ------------------
    # 25 пластинок
    # ------------------
    for i in range(25):
        release = random.choice(releases)
        record = Record(
            title=f'Пластинка {i+1}',
            release_year=release.release_year,
            price=round(random.uniform(1000, 3000), 2),
            stock_quantity=random.randint(0, 50),
            description='Описание пластинки',
            cover_image_url= f'record_{i+1}.jpg',
            record_type='LP',
            release_id=release.id,
            manufacturer_profile_id=manufacturer_profile.id
        )
        db.session.add(record)

    db.session.commit()
    print('✅ База данных успешно заполнена тестовыми данными.')


# ------------------
# Если запускаем как скрипт
# ------------------
if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
        seed_database()
