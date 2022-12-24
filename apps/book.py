from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired
from datetime import datetime
from app import db
from flask import Blueprint
from apps.root import Role
bp = Blueprint('book',__name__,url_prefix='/login/book')

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    press_name = db.Column(db.String(100), nullable=False)
    press_year = db.Column(db.Integer, default=datetime.year, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)


    def __init__(self, name, press_name, press_year, price, count):
        self.name = name
        self.press_name = press_name
        self.press_year = press_year
        self.price = price
        self.count = count

    def __init__(self, id, name, press_name, press_year, price, count):
        self.id = id
        self.name = name
        self.press_name = press_name
        self.press_year = press_year
        self.price = price
        self.count = count

class BookForm(FlaskForm):
    id = StringField(u'编号', validators=[DataRequired()])
    name = StringField(u'书名', validators=[DataRequired()])
    press_name = StringField(u'出版社', validators=[DataRequired()])
    press_year = StringField(u'出版年份', validators=[DataRequired()])
    price = StringField(u'价格', validators=[DataRequired()])
    count = StringField(u'数量', validators=[DataRequired()])
    submit = SubmitField(u'添加')

class SearchForm(FlaskForm):
    name = StringField(u'请输入书名进行查询', validators=[DataRequired()])
    submit = SubmitField(u'搜索')


class LoginForm(FlaskForm):
    """登录表单类"""
    id = StringField('工号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('确认')



from apps.login import UsPa
@bp.route('/', methods=['GET', 'POST'])
def book_login():
    error = ""
    permission = "图书管理员"
    form = LoginForm()
    if form.validate_on_submit():
        user = UsPa.query.filter_by(id=form.id.data).first()
        if user is not None:
            if str(user.password) == form.password.data:
                print("1")
                if user.permissions == 2:
                    session["role"] = "图书管理员"
                    session["user_id"] = user.id
                    return redirect(url_for('book.book_view'))
                else:
                    error = "该用户权限不足"
                    return render_template('login.html', form=form, error=error)
        error = "用户名或密码错误"

    return render_template('login.html', form=form, error=error, permission=permission)



@bp.route('/book_view', methods=['GET', 'POST'])
def book_view():
    form = SearchForm()
    role = session.get("role")
    user_id = session.get("user_id")
    books = Book.query.filter(Book.price >= 0).all()
    if form.validate_on_submit():
        books = Book.query.filter_by(name=form.name.data).all()
    print(books)
    return render_template('book_view.html', form=form, book=books, role=role, user_id=user_id)

@bp.route('/book_add', methods=['GET', 'POST'])
def book_add():
    new_book = BookForm()
    if new_book.validate_on_submit():
        getbook = Book.query.filter_by(id=new_book.id.data).first()
        if getbook is not None:
            print("有")
            getbook.count = int(new_book.count.data) + getbook.count
            addBook = getbook
        else:
            print("没有")
            print(new_book.name.data)
            addBook = Book(id=new_book.id.data, name=str(new_book.name.data), press_name=str(new_book.press_name.data),
                           press_year=int(new_book.press_year.data), price=int(new_book.price.data),
                           count=int(new_book.count.data))
        db.session.add(addBook)
        db.session.commit()
        flash(u'成功添加图书')
        return redirect(url_for('book.book_view'))
    return render_template('book_add.html', form=new_book)

@bp.route('/book_delete/<int:book_id>', methods=['GET', 'POST'])
def book_delete(book_id):
    delete_b = Book.query.filter_by(id=book_id).first()
    if delete_b is not None:
        db.session.delete(delete_b)
        flash(u'成功删除图书')
        db.session.commit()
    else:
        flash(u'找不到该图书')
    return redirect(url_for('book.book_view'))

@bp.route('/book_update/<int:id>', methods=['GET', 'POST'])
def book_update(id):
    content = Book.query.filter_by(id=id).first()
    form = BookForm(id=content.id, name=content.name, press_name=content.press_name, press_year=content.press_year,
                    price=content.price, count=content.count)
    if form.validate_on_submit():
        newBook = Book(id=int(form.id.data), name=str(form.name.data), press_name=str(form.press_name.data),
                       press_year=int(form.press_year.data), price=int(form.price.data), count=int(form.count.data))
        db.session.merge(newBook)
        db.session.commit()
        print("进行更新")
        flash("修改成功")
        return redirect(url_for('book.book_view'))
    return render_template('book_add.html', form=form)




#borrow



# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64))
#     sex = db.Column(db.String(64))
#     year = db.Column(db.String(64))
#
#     __table_args__ = {'extend_existing': True}
#
#     def __repr__(self):
#         return '<Role %r>' % self.name

class Borrow(db.Model):
    __tablename__ = 'borrow'
    borrow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    book_count = db.Column(db.Integer)

class BorrowForm(FlaskForm):
    user_name = StringField(u'用户')
    book_name = StringField(u'书名')
    book_count = IntegerField(u'数量', validators=[DataRequired()])
    submit = SubmitField(u'借阅')

@bp.route('/borrow_book/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(user_id, book_id):
    book_content = Book.query.filter_by(id=book_id).first()
    user_content = Role.query.filter_by(id=user_id).first()

    form = BorrowForm(user_name=user_content.name,book_name=book_content.name)
    if form.validate_on_submit():
        if int(form.book_count.data) in range(0,book_content.count+1):
            # 借书
            borrow = Borrow(user_id=user_id, book_id=book_id, book_count=int(form.book_count.data))
            db.session.add(borrow)
            db.session.commit()

            # 更改在馆该图书数量
            book_content.count = book_content.count - int(form.book_count.data)
            newBook = Book(id=book_content.id, name=book_content.name, press_name=book_content.press_name,
                           press_year=book_content.press_year, price=book_content.price, count=book_content.count)
            db.session.merge(newBook)
            db.session.commit()
            print("进行更新")
            flash("修改成功")

            return redirect(url_for('book.book_view'))
        else:
            print("借阅数量过大，该图书在馆数不足")
            return render_template('borrow_book.html', form=form)
    return render_template('borrow_book.html', form=form)


@bp.route('/return_book/<int:borrow_id>', methods=['GET', 'POST'])
def return_book(borrow_id):
    borrow_content = Borrow.query.filter_by(borrow_id=borrow_id).first()
    return_book_id = borrow_content.book_id

    book_content = Book.query.filter_by(id=return_book_id).first()

    if book_content is None:
        print("找不到该图书信息")
        return redirect(url_for('book.book_view'))
    else:
        book_content.count = book_content.count + borrow_content.book_count
        newBook = Book(id=book_content.id, name=book_content.name, press_name=book_content.press_name,
                       press_year=book_content.press_year, price=book_content.price, count=book_content.count)

    db.session.merge(newBook)
    db.session.commit()

    db.session.delete(borrow_content)
    db.session.commit()

    return redirect(url_for('book.borrow_user'))

@bp.route('/borrow_user', methods=['GET', 'POST'])
def borrow_user():
    user_id = session.get("user_id")
    class borrow_user_look():
        name = str()
        press_name = str()
        press_year = str()
        borrow_count = int()
        borrow_id = int()
        user_id = int()
    borrow_user_looks = []

    borrow_content = Borrow.query.filter_by(user_id=user_id).all()

    for b in borrow_content:
        content = borrow_user_look()
        content.borrow_id = b.borrow_id
        content.borrow_count = b.book_count
        content.user_id = user_id

        book_content = Book.query.filter_by(id=b.book_id).first()
        content.name = book_content.name
        content.press_name = book_content.press_name
        content.press_year = book_content.press_year

        borrow_user_looks.append(content)

    return render_template("borrow_user.html", borrow_user_look=borrow_user_looks)