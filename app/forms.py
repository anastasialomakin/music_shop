from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class EnsembleForm(FlaskForm):
    name = StringField('Название ансамбля', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Сохранить')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')