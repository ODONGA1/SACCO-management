# SACCO Management System

## Overview
The SACCO Management System is a Django-based web application designed to streamline and manage SACCO operations, including user authentication, transactions, and account management.

## Features
- User registration and authentication (Login, Logout, Registration)
- ShortUUIDField for unique user IDs
- Role-based access control
- Transaction management
- Data persistence with PostgreSQL

## Requirements
Before running the project, ensure you have the following installed:
- Python 3.12+
- Django 5.1.6
- PostgreSQL (or SQLite for local testing)
- Virtual environment (venv)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/SACCO-management.git
cd SACCO-management
```

### 2. Create and Activate a Virtual Environment
#### On Windows (cmd):
```bash
python -m venv venv
venv\Scripts\activate
```
#### On Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the Database
Update the `settings.py` file with your database credentials. If using PostgreSQL, ensure you have a database set up.

For SQLite (default):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

For PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up an admin user.

### 7. Start the Development Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`

## Troubleshooting
- If you encounter a **ModuleNotFoundError**, install missing dependencies:
  ```bash
  pip install shortuuid
  ```
- If permission errors occur on Windows, run your terminal as Administrator.

## License
This project is licensed under the MIT License.

## Contributors
- [Your Name]
- [Other Contributors]
