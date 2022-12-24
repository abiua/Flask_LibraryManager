import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField

import sqlite3
# 5000 1234
# 4000 789
# 1 123456
app = Flask(__name__)
bootstrap = Bootstrap(app)

'''配置数据库'''
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123456'
db = SQLAlchemy(app)
# db.metadata.clear()

from apps.login import bp as login_bp
from apps.root import bp as root_bp

app.register_blueprint(login_bp)
app.register_blueprint(root_bp)

from apps.book import bp as book_bp
app.register_blueprint(book_bp)

# #数据库创建表
# def init():
#     from apps.book import Book
#     db.create_all(Book)




class iForm(FlaskForm):
    selectfield = SelectField('登录身份')
    submit = SubmitField('确定')


@app.route('/', methods=['GET', 'POST'])
def hello():
    form = iForm()
    l = ["", "root", "book", "user"]
    form.selectfield.choices = [i for i in l]
    if form.validate_on_submit():
        if form.selectfield.data == "user":
            return redirect(url_for('login.login'))
        if form.selectfield.data == "book":
            return redirect(url_for('book.book_login'))
        else:
            return redirect(url_for('root.root_login'))
    return render_template("start.html", form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
