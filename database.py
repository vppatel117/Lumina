from flask_sqlalchemy import SQLAlchemy

# Shared database instance used across the application.
db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app and create tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
