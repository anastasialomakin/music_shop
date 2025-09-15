from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, EqualTo, Optional, ValidationError
from app.models import Customer, Ensemble
from flask_login import current_user

class EnsembleForm(FlaskForm):
    name = StringField('Название ансамбля', validators=[DataRequired()])
    description = TextAreaField('Описание')
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
        # Проверяем, что если имя пользователя изменилось, то новое имя не занято
        if username.data != current_user.username:
            user = Customer.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')
            
class RecordForm(FlaskForm):
    title = StringField('Название альбома', validators=[DataRequired()])
    ensemble = SelectField('Ансамбль', coerce=int, validators=[DataRequired()])
    release_year = IntegerField('Год выпуска', validators=[Optional()])
    retail_price = DecimalField('Розничная цена', validators=[DataRequired()])
    stock_quantity = IntegerField('Количество на складе', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Сохранить')