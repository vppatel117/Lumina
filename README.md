# Lumina - Library Management System

A Flask-based library management system built with Python.

## Features
- User authentication and login system
- Book catalog management
- Loan tracking and management
- User and Librarian dashboards
- SQLAlchemy ORM for database operations

## Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Lumina
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
FLASK_ENV=development
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

5. Run the application:
```bash
python main.py
```

6. run this application in terminal using:

flask --app main run


The application will be available at `http://localhost:5000`

## Project Structure
```
Lumina/
├── main.py              # Flask application entry point
├── config.py            # Configuration settings
├── database.py          # Database initialization
├── models.py            # SQLAlchemy models
├── requirements.txt     # Python dependencies
├── integrations/        # External integrations
│   └── catalog_client.py
├── services/            # Business logic
│   └── catalog_service.py
├── static/              # Static files (CSS, JS, images)
│   └── style.css
└── templates/           # HTML templates
    ├── base.html
    ├── catalog.html
    ├── dashboard_librarian.html
    ├── dashboard_user.html
    └── login.html
```

## Technologies Used
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- PostgreSQL / SQLite

## License
[Your License Here]

## Author
[Your Name]
