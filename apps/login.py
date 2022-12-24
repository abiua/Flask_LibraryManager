import os
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, BooleanField, DateField, HiddenField, PasswordField, \
    FileField, RadioField, SelectField
from wtforms.validators import DataRequired
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from debugpy._vendored.pydevd.pydevd_attach_to_process.winappdbg.win32.defines import TRUE
from flask_login import current_user, login_required, UserMixin, login_user


from app import db

from flask import Blueprint

bp = Blueprint("login", __name__, url_prefix="/login")


class LoginForm(FlaskForm):
    """登录表单类"""
    id = StringField('工号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class GenerateForm(FlaskForm):
    """登录表单类"""
    id = StringField('工号', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class UsPa(db.Model):
    __tablename__ = 'uspa'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    permissions = db.Column(db.String(64), default=0)

    def __repr__(self):
        return '<Role %r>' % self.name


def vertify_user(id, password):
    """根据用户名获得用户记录"""
    user = UsPa.query.filter_by(id=int(id)).first()
    if user is not None:
        if user.password == password:
            return user
    return None


# @bp.route('/loginwin')  # 首页
# @login_required  # 需要登录才能访问
# def index():
#     return render_template('index.html', username=current_user.username)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ""
    if form.validate_on_submit():
        id = form.id.data
        password = form.password.data
        user = UsPa.query.filter_by(id=id).first()
        if user is None:
            error = "工号或密码有误"
        else:
            if str(user.password) == password:
                # session['user'] = user_name
                session["role"] = "普通用户"
                session["user_id"] = user.id
                return redirect(url_for('book.book_view'))
            error = "工号或密码有误"
    return render_template('login.html', form=form, error=error)


@bp.route('/login/generate', methods=['GET', 'POST'])
def login_generate():
    form = GenerateForm()
    error = ""
    if form.validate_on_submit():
        a = UsPa(id=form.id.data, name=form.name.data, password=form.password.data, permissions=2)
        db.session.add(a)
        db.session.commit()

    return render_template('login.html', form=form, error=error)

        # user_name = form.username.data
        # password = form.password.data
        # user_info = get_user(user_name)  # 从用户数据中查找用户记录
        # if user_info is None:
        #     emsg = "用户名或密码密码有误"
        # else:
        #     user = User(user_info)  # 创建用户实体
        #     if user.verify_password(password):  # 校验密码
        #         # login_user(user)  # 创建用户 Session
        #         return render_template('index.html', username=user_name)
        #     else:
        #         emsg = "用户名或密码密码有误"
from flask import redirect, url_for
from flask_login import logout_user

# ...
# @app.route('/logout')  # 登出
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))





