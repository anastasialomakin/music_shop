from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, EqualTo, Optional, ValidationError
from app.models import User, Band
from flask_login import current_user

class BandForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired()])
    bio = TextAreaField('Описание/Биография')
    submit = SubmitField('Сохранить')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    shipping_address = TextAreaField('Адрес доставки')
    password = PasswordField('Новый пароль', validators=[Optional()])
    password2 = PasswordField(
        'Повторите новый пароль', validators=[EqualTo('password', message='Пароли должны совпадать.')])
    submit = SubmitField('Сохранить изменения')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')

class RecordForm(FlaskForm):
    title = StringField('Название альбома', validators=[DataRequired()])
    band = SelectField('Группа', coerce=int, validators=[DataRequired()])
    release_year = IntegerField('Год выпуска', validators=[Optional()])
    price = DecimalField('Цена', validators=[DataRequired()])
    stock_quantity = IntegerField('Количество на складе', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Сохранить')

class AdminEditUserForm(EditProfileForm):
    role = SelectField('Роль', choices=[('user', 'Покупатель'), ('manufacturer', 'Производитель'), ('admin', 'Администратор')])
    submit = SubmitField('Сохранить')