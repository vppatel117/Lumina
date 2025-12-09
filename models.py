from datetime import datetime, timedelta

from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256

from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    password_hash = db.Column(db.String(255), nullable=False)

    loans = db.relationship("Loan", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)

    @property
    def is_librarian(self) -> bool:
        return self.role == "librarian"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)

    loans = db.relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    @property
    def borrowed_count(self) -> int:
        return sum(1 for loan in self.loans if not loan.returned_date)

    @property
    def available_copies(self) -> int:
        return max(self.total_copies - self.borrowed_count, 0)


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_date = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="loans")
    book = db.relationship("Book", back_populates="loans")

    @staticmethod
    def create(user, book, duration_days: int = 14):
        due = datetime.utcnow() + timedelta(days=duration_days)
        return Loan(user=user, book=book, due_date=due)

    @property
    def is_overdue(self) -> bool:
        return not self.returned_date and datetime.utcnow() > self.due_date
