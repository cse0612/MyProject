from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email
import sys

class UserCreateForm(FlaskForm):
  id = StringField('id', validators=[DataRequired()])
  pw = PasswordField('pw', validators=[DataRequired()])
  #email = EmailField('이메일', validators=[DataRequired(), Email()])
  # print("member_id>>>>"+str(userid), file=sys.stderr)
  # print("member_pw>>>>"+str(password), file=sys.stderr)
    