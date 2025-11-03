from flask import Flask,jsonify
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
api=Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre
        }

with app.app_context():
    db.create_all()


book_parser = reqparse.RequestParser()
book_parser.add_argument('title', type=str, required=True, help="title is required")
book_parser.add_argument('author', type=str, required=True, help="author is required")
book_parser.add_argument('genre', type=str, required=True, help="genre is required")

class BookListResource(Resource):
    def get(self):
        books = BookModel.query.all()
        return jsonify([b.to_dict() for b in books])

    def post(self):
        args = book_parser.parse_args()
        new_book = BookModel(title=args['title'], author=args['author'], genre=args['genre'])
        db.session.add(new_book)
        db.session.commit()
        return new_book.to_dict(), 201

class BookResource(Resource):
    def get(self, book_id):
        book = BookModel.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        return book.to_dict(), 200

    def put(self, book_id):
        args = book_parser.parse_args()
        book = BookModel.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        book.title = args['title']
        book.author = args['author']
        book.genre = args['genre']
        db.session.commit()
        return book.to_dict(), 200

    def delete(self, book_id):
        book = BookModel.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200

api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<int:book_id>')

if __name__=='__main__':
    app.run(debug=True)