import os 
from flask import Flask,render_template,session,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField,\
    SubmitField,BooleanField,DateField,HiddenField,PasswordField,\
    FileField,RadioField,SelectField
from wtforms.validators import DataRequired
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy 
# from debugpy._vendored.pydevd.pydevd_attach_to_process.winappdbg.win32.defines import TRUE
from flask_login import current_user, login_required, UserMixin, login_user


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'data.sqlite')
print(basedir)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='123456'


db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    """登录表单类"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    


class Role (db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name
    
    
class User(UserMixin):
    """用户类"""
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
        return None


from werkzeug.security import generate_password_hash, check_password_hash
# ...
USERS = [
    {
        "id": 1,
        "name": 'lily',
        "password": generate_password_hash('123')
    },
    {
        "id": 2,
        "name": 'tom',
        "password": generate_password_hash('123')
    }
]

from werkzeug.security import generate_password_hash
import uuid
# ...
def create_user(user_name, password):
    """创建一个用户"""
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def get_user(user_name):
    """根据用户名获得用户记录"""
    for user in USERS:
        if user.get("name") == user_name:
            return user
    return None

    
@app.route('/')  # 首页
@login_required  # 需要登录才能访问
def index():
    return render_template('index.html', username=current_user.username)

    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_info = get_user(user_name)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                # login_user(user)  # 创建用户 Session
                return render_template('index.html', username=user_name)
            else:
                emsg = "用户名或密码密码有误"
    return render_template('login.html', form=form, emsg=emsg)
        
from flask import redirect, url_for
from flask_login import logout_user
# ...
# @app.route('/logout')  # 登出
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
    