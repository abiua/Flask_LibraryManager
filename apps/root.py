from flask import Flask, render_template, session, redirect, url_for, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, BooleanField, DateField, HiddenField, PasswordField, \
    FileField, RadioField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
# from flask_moment import Moment
# from flask_bootstrap import Bootstrap
# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
# # from debugpy._vendored.pydevd.pydevd_attach_to_process.winappdbg.win32.defines import TRUE
# from flask_login import current_user, login_required, UserMixin, login_user

from app import db

bp = Blueprint("root", __name__, url_prefix="/login/root")

'''借阅用户信息'''
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    sex = db.Column(db.String(64))
    year = db.Column(db.String(64))

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '<Role %r>' % self.name


class LoginForm(FlaskForm):
    id = StringField('工号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class OperateForm(FlaskForm):
    radioField = RadioField('操作', choices=["创建借阅用户", "删除借阅用户", "修改借阅用户", "查询借阅用户"])
    submitField = SubmitField("确定")


class CreateForm(FlaskForm):
    id = StringField(u'工号', validators=[DataRequired()])
    name = StringField(u'姓名', validators=[DataRequired()])
    sex = RadioField(u'性别', validators=[DataRequired()], choices=[("男", 'Male'), ("女", 'Female')])
    year = IntegerField(u'入职年份', validators=[NumberRange(min=1949, max=2090)])
    password = StringField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'创建')


class DeleteForm(FlaskForm):
    id = StringField(u'工号', validators=[DataRequired()])
    submit = SubmitField(u'删除')


class DeForm(FlaskForm):
    id = StringField(u'工号', validators=[DataRequired()])
    name = StringField(u'姓名', validators=[DataRequired()])
    submit = SubmitField(u'删除')


class AlterForm(FlaskForm):
    id = StringField(u'工号', validators=[DataRequired()])
    name = StringField(u'姓名')
    sex = RadioField(u'性别', choices=[("男", 'Male'), ("女", 'Female')])
    year = IntegerField(u'入职年份')
    submit = SubmitField(u'确定')


class SearchForm(FlaskForm):
    selectfield = SelectField('请选择检索方式', choices=["工号", "姓名", "性别", "入职年份"])
    value = StringField(validators=[DataRequired()])
    submit = SubmitField(u'查找')


'''用来判断用户是否登录成功'''
from functools import wraps
def is_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('user', None) == 'root':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('root.root_login'))

    return wrapper


from apps.login import UsPa
@bp.route("/", methods=['GET', 'POST'])
def root_login():
    error = ""
    permission = "系统管理员"
    form = LoginForm()
    if form.validate_on_submit():
        user = UsPa.query.filter_by(id=form.id.data).first()
        if user is not None:
            if str(user.password) == form.password.data:
                print("1")
                if user.permissions == 1:
                    session['user'] = "root"
                    return redirect(url_for('root.operate'))
                else:
                    error = "该用户权限不足"
                    return render_template('login.html', form=form, error=error)
        error = "工号或密码错误"

    return render_template('login.html', form=form, error=error, permission=permission)


'''操作'''
@bp.route("/operate", methods=['GET', 'POST'])
@is_admin
def operate():
    form = OperateForm()
    if form.validate_on_submit():
        if form.radioField.data == "创建借阅用户":
            return redirect(url_for('root.create'))
        elif form.radioField.data == "删除借阅用户":
            return redirect(url_for('root.delete'))
        elif form.radioField.data == "修改借阅用户":
            return redirect(url_for('root.alter'))
        else:
            return redirect(url_for('root.search'))
    return render_template("root.html", form=form)


'''创建'''
@bp.route("/create", methods=['GET', 'POST'])
def create():
    emsg = ""
    info = "创建借阅用户"
    create_form = CreateForm()
    users = Role.query.all()
    if create_form.validate_on_submit():
        user = Role.query.filter_by(id=create_form.id.data).first()
        if user is None:
            user = Role(id=create_form.id.data, name=create_form.name.data, sex=create_form.sex.data,
                        year=create_form.year.data)
            db.session.add(user)
            permission = UsPa(id=create_form.id.data, name=create_form.name.data, password=create_form.password.data)
            db.session.add(permission)
            db.session.commit()
        else:
            emsg = "该工号已存在"
        users = Role.query.all()
    return render_template("user_create.html", form=create_form, emsg=emsg, users=users, info=info)


'''删除'''
@bp.route("/delete", methods=['GET', 'POST'])
def delete():
    emsg = ""
    info = "删除借阅用户"
    delete_form = DeForm()
    users = Role.query.all()
    if delete_form.validate_on_submit():
        # id = delete_form.id.data
        user = Role.query.filter_by(id=delete_form.id.data).first()
        if user is not None:
            db.session.delete(user)
            db.session.commit()
            emsg = "删除成功"
        else:
            emsg = "删除失败 无该工号的用户"
        users = Role.query.all()
    return render_template("user_create.html", form=delete_form, emsg=emsg, users=users, info=info)


'''修改'''
@bp.route("/alter", methods=['GET', 'POST'])
def alter():
    emsg = ""
    info = "修改借阅用户"
    alter_form = AlterForm()
    users = Role.query.all()
    if alter_form.validate_on_submit():
        id = alter_form.id.data
        user = Role.query.filter_by(id=alter_form.id.data).first()
        if user is not None:
            user.name = alter_form.name.data
            user.sex = alter_form.sex.data
            user.year = alter_form.year.data
            db.session.add(user)
            db.session.commit()
            emsg = "修改成功"
        else:
            emsg = "修改失败 无该工号的用户"
        users = Role.query.all()
    return render_template("user_create.html", form=alter_form, emsg=emsg, users=users, info=info)


'''查找'''
@bp.route("/search", methods=['GET', 'POST'])
def search():
    flag = False
    error = ""
    info = "查找借阅用户"
    search_form = SearchForm()
    if search_form.validate_on_submit():
        if search_form.selectfield.data in ["工号", "姓名", "性别"]:
            if search_form.selectfield.data == "工号":
                user = Role.query.filter_by(id=search_form.value.data).first()
            elif search_form.selectfield.data == "姓名":
                user = Role.query.filter_by(name=search_form.value.data).all()
            else:
                user = Role.query.filter_by(sex=search_form.value.data).all()
        else:
            user = Role.query.filter_by(year=search_form.value.data).all()
        if user is not None:
            if user:
                if search_form.selectfield.data == "工号":
                    return render_template("user_search.html", form=search_form, item=user, flag=True, info=info)
                elif search_form.selectfield.data in ["姓名", "性别", "入职年份"]:
                    return render_template("user_search.html", form=search_form, users=user, flag=True, info=info)
        error = "查找失败 无该信息的用户"
        return render_template("user_search.html", form=search_form, flag=False, error=error, info=info)

    return render_template("user_search.html", form=search_form, flag=False, info=info)


'''登出'''
@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('root.root_login'))
