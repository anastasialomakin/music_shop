from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, IntegerField, DecimalField, SelectField, FileField, SelectMultipleField, TimeField
from wtforms.validators import DataRequired, EqualTo, Optional, ValidationError, NumberRange
from app.models import User, Release, UserMixin
from flask_login import current_user
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    # только для покупателей
    shipping_address = TextAreaField('Адрес доставки')
    # Поля для смены пароля
    password = PasswordField('Новый пароль', validators=[Optional()])
    password2 = PasswordField(
        'Повторите новый пароль', 
        validators=[EqualTo('password', message='Пароли должны совпадать.')]
    )
    submit = SubmitField('Сохранить изменения')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')
            

class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Адрес доставки', validators=[DataRequired()])
    payment_method = SelectField('Способ оплаты', choices=[('Card', 'Картой онлайн'), ('Cash', 'Наличными при получении')], validators=[DataRequired()])
    comment = TextAreaField('Комментарий к заказу')
    submit = SubmitField('Подтвердить заказ')

class ManufacturerProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    company_name = StringField('Название компании', validators=[DataRequired()])
    company_address = TextAreaField('Адрес компании')
    password = PasswordField('Новый пароль', validators=[Optional()])
    password2 = PasswordField(
        'Повторите новый пароль', 
        validators=[EqualTo('password', message='Пароли должны совпадать.')]
    )
    submit = SubmitField('Сохранить изменения')

class RecordForm(FlaskForm):
    title = StringField('Название издания', validators=[DataRequired()])
    release = SelectField('Релиз', coerce=int, validators=[DataRequired()])
    manufacturer_profile = SelectField('Производитель', coerce=int, validators=[DataRequired()])
    release_year = IntegerField('Год этого издания', validators=[Optional()])
    price = DecimalField('Цена (в рублях)', validators=[DataRequired()])
    stock_quantity = IntegerField('Количество на складе', validators=[DataRequired()])
    record_type = StringField('Тип записи (LP, EP, 7" и т.д.)')
    description = TextAreaField('Описание издания')
    cover_image = FileField('Обложка (изображение)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    submit = SubmitField('Сохранить пластинку')


class AdminEditUserForm(EditProfileForm):
    role = SelectField('Роль', choices=[
        ('user', 'Покупатель'), 
        ('manufacturer', 'Производитель'), 
        ('admin', 'Администратор')
    ])
    submit = SubmitField('Сохранить изменения')

class GenreForm(FlaskForm):
    name = StringField('Название жанра', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class ArtistForm(FlaskForm):
    name = StringField('Имя артиста/музыканта', validators=[DataRequired()])
    bio = TextAreaField('Биография')
    submit = SubmitField('Сохранить')

class BandForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired()])
    bio = TextAreaField('Биография')
    genre = SelectField('Жанр', coerce=int, validators=[Optional()])
    members = SelectMultipleField('Участники', coerce=int)
    cover_image = FileField('Картинка', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    submit = SubmitField('Сохранить')

class CompositionForm(FlaskForm):
    title = StringField('Название композиции', validators=[DataRequired()])
    author_band = SelectField('Группа (автор)', coerce=int, validators=[DataRequired()])
    duration = IntegerField('Длительность (в секундах)', validators=[Optional()])
    submit = SubmitField('Сохранить')


class ReleaseForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    release_year = IntegerField('Год выпуска', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    band = SelectField('Группа', coerce=int, validators=[DataRequired()])
    compositions = SelectMultipleField('Композиции', coerce=int, validators=[Optional()])
    cover_image = FileField('Обложка', validators=[Optional()])
    submit = SubmitField('Сохранить')

class AdminOrderForm(FlaskForm):
    status = SelectField('Статус', choices=[
        ('pending', 'В ожидании'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён')
    ], validators=[DataRequired()])
    shipping_address = TextAreaField('Адрес доставки', validators=[DataRequired()])
    payment_method = SelectField('Способ оплаты', choices=[('Card', 'Картой онлайн'), ('Cash', 'Наличными при получении')], validators=[DataRequired()])
    comment = TextAreaField('Комментарий к заказу')
    submit = SubmitField('Сохранить')