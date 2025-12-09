from datetime import datetime

from dotenv import load_dotenv
from flask import (Flask, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

from database import db, init_db
from config import get_config
from models import Book, Loan, User
from services import search_books

load_dotenv()
ConfigClass = get_config()

app = Flask(__name__)
app.config.from_object(ConfigClass)

init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_nav():
    return {
        "current_user": current_user,
    }


@app.route("/")
def index():
    if current_user.is_authenticated:
        dashboard = "dashboard_librarian" if current_user.is_librarian else "dashboard_user"
        return redirect(url_for(dashboard))
    return redirect(url_for("catalog"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Signed out", "info")
    return redirect(url_for("login"))


@app.route("/catalog")
def catalog():
    query = request.args.get("q", "").strip()
    results = search_books(query)
    return render_template(
        "catalog.html",
        books=results["local"],
        external_books=results["external"],
        query=query,
    )


@app.route("/books/<int:book_id>/checkout", methods=["POST"])
@login_required
def checkout_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.available_copies <= 0:
        flash("All copies are currently checked out.", "warning")
        return redirect(url_for("catalog"))
    loan = Loan.create(current_user, book, current_app.config["DEFAULT_LOAN_DURATION_DAYS"])
    db.session.add(loan)
    db.session.commit()
    flash(f"You now have '{book.title}' until {loan.due_date.date().isoformat()}.", "success")
    return redirect(url_for("dashboard_user"))


@app.route("/loans/<int:loan_id>/return", methods=["POST"])
@login_required
def return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.user != current_user and not current_user.is_librarian:
        abort(403)
    if loan.returned_date:
        flash("Loan already closed.", "info")
    else:
        loan.returned_date = datetime.utcnow()
        db.session.commit()
        flash("Book returned. Thank you!", "success")
    redirect_target = request.referrer or url_for("dashboard_user")
    return redirect(redirect_target)


@app.route("/dashboard/librarian", methods=["GET", "POST"])
@login_required
def dashboard_librarian():
    if not current_user.is_librarian:
        abort(403)

    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "add_book":
            _add_book_from_form()
        elif form_type == "manual_checkout":
            _manual_checkout_from_form()
        return redirect(url_for("dashboard_librarian"))

    stats = _inventory_stats()
    active_loans = (Loan.query
                    .filter(Loan.returned_date.is_(None))
                    .order_by(Loan.due_date)
                    .all())
    users = User.query.order_by(User.name).all()
    books = Book.query.order_by(Book.title).all()

    return render_template(
        "dashboard_librarian.html",
        stats=stats,
        active_loans=active_loans,
        users=users,
        books=books,
    )


@app.route("/dashboard/user")
@login_required
def dashboard_user():
    loans = (Loan.query
             .filter_by(user_id=current_user.id)
             .order_by(Loan.due_date)
             .all())
    return render_template("dashboard_user.html", loans=loans)


def _add_book_from_form():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    copies = int(request.form.get("copies", 1))
    if not title or not author:
        flash("Title and author are required", "warning")
        return
    book = Book(title=title, author=author, total_copies=max(copies, 1))
    db.session.add(book)
    db.session.commit()
    flash(f"Added '{title}'.", "success")


def _manual_checkout_from_form():
    email = request.form.get("user_email", "").lower().strip()
    book_id = request.form.get("book_id")
    try:
        book_id = int(book_id)
    except (TypeError, ValueError):
        book_id = None
    user = User.query.filter_by(email=email).first()
    book = Book.query.get(book_id) if book_id else None
    if not user or not book:
        flash("User or book not found", "danger")
        return
    if book.available_copies <= 0:
        flash("No copies available", "warning")
        return
    loan = Loan.create(user, book, current_app.config["DEFAULT_LOAN_DURATION_DAYS"])
    db.session.add(loan)
    db.session.commit()
    flash(f"{user.name} now has '{book.title}'.", "success")


def _inventory_stats():
    total_books = Book.query.count()
    total_copies = db.session.query(db.func.sum(Book.total_copies)).scalar() or 0
    active_loans = Loan.query.filter(Loan.returned_date.is_(None)).all()
    overdue = sum(1 for loan in active_loans if loan.is_overdue)
    available = total_copies - len(active_loans)
    return {
        "titles": total_books,
        "copies": total_copies,
        "borrowed": len(active_loans),
        "available": max(available, 0),
        "overdue": overdue,
    }


def seed_demo_data():
    if User.query.count() > 0:
        return
    librarian = User(name="Priya Librarian", email="librarian@lumina.local", role="librarian")
    librarian.set_password("password")
    user = User(name="Arjun Reader", email="user@lumina.local", role="user")
    user.set_password("password")

    books = [
        Book(title="Clean Architecture", author="Robert C. Martin", total_copies=3),
        Book(title="Atomic Habits", author="James Clear", total_copies=4),
        Book(title="The Pragmatic Programmer", author="Andrew Hunt", total_copies=2),
        Book(title="Designing Data-Intensive Applications", author="Martin Kleppmann", total_copies=5),
    ]

    db.session.add_all([librarian, user] + books)
    db.session.commit()


with app.app_context():
    seed_demo_data()


if __name__ == "__main__":
    app.run(debug=True)
