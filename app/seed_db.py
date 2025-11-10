from app import db
from app.models import Genre, Band, Artist, Composition, Release, Record, User, ManufacturerProfile
from werkzeug.security import generate_password_hash
import random
import faker

fake = faker.Faker()

def seed_database():
    if User.query.filter_by(role='admin').first():
        print("База уже содержит администратора. Seed пропущен.")
        return
    # ------------------
    # Админ и обычный пользователь
    # ------------------
    if not User.query.filter_by(role='admin').first():
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        print("✅ Администратор создан: admin / admin123")

    if not User.query.filter_by(username='user1').first():
        user = User(
            username='user1',
            password_hash=generate_password_hash('password'),
            role='user'
        )
        db.session.add(user)
        print("✅ Обычный пользователь создан: user1 / password")

    db.session.commit()

    # ------------------
    # Жанры
    # ------------------
    genre_names = ['Rock', 'Jazz', 'Pop', 'Hip-Hop', 'Electronic']
    genres = [Genre(name=name) for name in genre_names]
    db.session.add_all(genres)
    db.session.commit()

    # ------------------
    # Производители
    # ------------------
    manufacturers = []
    for i in range(3):
        username = f'manufacturer{i+1}'
        user = User(
            username=username,
            password_hash=generate_password_hash('password'),
            role='manufacturer'
        )
        db.session.add(user)
        db.session.commit()

        profile = ManufacturerProfile(
            user_id=user.id,
            company_name=f'{fake.company()}',
            company_address=fake.address()
        )
        db.session.add(profile)
        db.session.commit()
        manufacturers.append(profile)

    # ------------------
    # Артисты
    # ------------------
    artists = []
    for i in range(20):
        artist = Artist(
            name=fake.first_name() + " " + fake.last_name(),
            bio=fake.text(max_nb_chars=150)
        )
        db.session.add(artist)
        artists.append(artist)
    db.session.commit()

    # ------------------
    # Группы
    # ------------------
    bands = []
    for i in range(10):
        band = Band(
            name=fake.word().capitalize() + " Band",
            bio=fake.text(max_nb_chars=200),
            genre=random.choice(genres),
            cover_image_url=f"band_{i+1}.jpg",
            # placeholder для картинки band_n.jpg
        )
        # Добавляем артистов в группу (1–4 случайных)
        num_members = random.randint(1, 4)
        band.members = random.sample(artists, num_members)
        db.session.add(band)
        bands.append(band)
    db.session.commit()

    # ------------------
    # Релизы
    # ------------------
    releases = []
    for i in range(25):
        release_year = random.randint(1990, 2025)
        release = Release(
            title=fake.word().capitalize() + f" Release {i+1}",
            release_year=release_year,
            cover_image_url=f"release_{i+1}.jpg",
            band=random.choice(bands)
        )
        db.session.add(release)
        releases.append(release)
    db.session.commit()

    # ------------------
    # Композиции
    # ------------------
    compositions = []
    for release in releases:
        num_tracks = random.randint(3, 8)
        for j in range(num_tracks):
            comp = Composition(
                title=fake.word().capitalize() + f" Track {j+1}",
                duration=random.randint(120, 300),
                author_band_id=release.band.id
            )
            comp.releases.append(release)
            db.session.add(comp)
            compositions.append(comp)
    db.session.commit()

    # ------------------
    # Пластинки
    # ------------------
    records = []
    total_records = 50
    records_created = 0
    release_pool = releases.copy()
    while records_created < total_records:
        release = random.choice(release_pool)
        # определяем сколько версий будет для этого релиза (1–3)
        remaining = total_records - records_created
        max_versions = min(3, remaining)
        versions = random.randint(1, max_versions)
        for v in range(versions):
            record_year = random.randint(release.release_year, 2025)
            record = Record(
                title=f"{release.title} - Edition {v+1}",
                release_year=record_year,
                price=round(random.uniform(1000, 3000), 2),
                stock_quantity=random.randint(0, 50),
                description=fake.text(max_nb_chars=150),
                cover_image_url=f"record_{records_created+1}.jpg",
                record_type=random.choice(['Studio', 'Live']),
                release_id=release.id,
                manufacturer_profile_id=random.choice(manufacturers).id
            )
            db.session.add(record)
            records.append(record)
            records_created += 1
            if records_created >= total_records:
                break
    db.session.commit()

    print("✅ Seed завершён. Созданы:")
    print(f"- Жанры: {len(genres)}")
    print(f"- Группы: {len(bands)}")
    print(f"- Артисты: {len(artists)}")
    print(f"- Релизы: {len(releases)}")
    print(f"- Композиции: {len(compositions)}")
    print(f"- Пластинки: {len(records)}")
    print(f"- Производители: {len(manufacturers)}")
    print("Админ и обычный пользователь созданы.")

# ------------------
# Если запускаем как скрипт
# ------------------
if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
        seed_database()

# i want to sleep please fix jesus please
