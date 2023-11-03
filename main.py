import sqlite3
from pprint import pprint

import sqlalchemy
from flask import Flask, render_template, request, redirect, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

bootstrap = Bootstrap5(app)
app.config['BOOTSTRAP_BTN_STYLE'] = "dark"

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"
db.init_app(app)


class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, unique=False, nullable=False)
	author = db.Column(db.String, unique=False, nullable=False)
	abstract = db.Column(db.String, unique=False, nullable=False)
	rating = db.Column(db.String, unique=False, nullable=True)
	__table_args__ = (UniqueConstraint('title', 'author', name='edition_doesnt_matters'),)


with app.app_context():
	db.create_all()


class BookForm(FlaskForm):
	book_title = StringField('Book Title', validators=[DataRequired(message='Please enter the book title here.')])
	author = StringField('Author', validators=[DataRequired(message='Please enter the book\'s author here.')])
	abstract = TextAreaField('Abstract', validators=[DataRequired(message='Please enter the book\'s abstract here.')])
	book_rating = SelectField('Book Rating',
							  choices=['Rate the Book', '📙️', '📙️📙', '📙📙📙️', '📙️📙📙📙', '📙️📙📙📙📙'],
							  validators=[DataRequired(message="Please rate the book 1-5")])
	submit = SubmitField('Submit')


class EditRatingForm(FlaskForm):
	book_rating = SelectField('Book Rating',
							  choices=[ '📙️', '📙️📙', '📙📙📙️', '📙️📙📙📙', '📙️📙📙📙📙'],
							  validators=[DataRequired(message="Please rate the book 1-5")])
	submit = SubmitField('Submit')


@app.route('/')
def home():
	with app.app_context():
		result = db.session.execute(db.select(Book).order_by(Book.id))
		books = result.scalars()
		all_books = []
		for book in books:
			all_books.append(book)
			pprint(book.title)
	return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
	form = BookForm()
	if request.method == 'GET':
		return render_template('add.html', form=form)
	elif request.method == 'POST' and form.validate_on_submit():
		book = {
			"title": form.book_title.data,
			"author": form.author.data,
			"abstract": form.abstract.data,
			"rating": form.book_rating.data,
		}
		stored_book = Book(
			title=book['title'],
			author=book['author'],
			abstract=book['abstract'],
			rating=book['rating']
		)
		try:
			with app.app_context():
				db.session.add(stored_book)
				db.session.commit()
		except sqlalchemy.exc.IntegrityError:
			flash('This Book is already exists.')
			return render_template('add.html', form=form)
		pprint(book)
		# all_books.append(book)
		# pprint(all_books)
		return redirect('.')
	else:
		return render_template('add.html', form=form)


@app.route("/edit/<book_id>", methods=['GET', 'POST'])
def edit(book_id):
	form = EditRatingForm()
	book_id = book_id
	if request.method == 'GET':
		with app.app_context():
			book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
		return render_template('edit.html', form=form, book=book)
	elif request.method == 'POST' and form.validate_on_submit():
		rating = form.book_rating.data
		with app.app_context():
			book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
			book_to_update.rating = rating
			db.session.commit()
		return redirect('../')
	else:
		return redirect('../')


@app.route("/del/<book_id>", methods=['GET', 'POST'])
def delete(book_id):
	book_id = book_id
	with app.app_context():
		book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
		db.session.delete(book)
		db.session.commit()
	return redirect('../')


if __name__ == "__main__":
	app.run(debug=True)
