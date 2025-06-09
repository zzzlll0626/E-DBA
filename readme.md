# B03 - Education Data Bay Area (E-DBA)

## Project Overview
E-DBA is a lightweight Flask application designed to provide a secure data sharing platform for educational institutions. The system supports course information sharing, student identity authentication, thesis access, and online payment processing, while implementing different levels of user access control.

## Technology Stack
- **Backend Framework**: Flask 2.3.0
- **Database**: MySQL 8.1.0
- **ORM**: Flask-SQLAlchemy 3.1.0

## Project Structure
```
SDW/
├── .venv/             # Python virtual environment
├── app/               # Main application directory
│   ├── controllers/   # Request handlers and routes
│   ├── models/        # Database models
│   ├── static/        # Static assets
│   ├── templates/     # HTML templates
│   ├── uploads/       # User uploaded files
│   │   ├── config/    # Configuration files storage
│   │   └── temp/      # Temporary files
│   ├── utils/         # Utility functions
│   └── __init__.py    # Application initialization
├── logs/              # Log files
├── uploads/           # Top-level upload directory
│   ├── flask_session/ # Flask session storage
│   ├── policies/      # Policy documents
│   └── proof_documents/ # Proof documents
├── .env               # Environment variables configuration
├── init_db.py         # Database initialization script
├── requirements.txt   # Project dependencies
└── run.py             # Application startup script
```

## Installation Guide

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip

### Setup Steps
1. Clone the repository from GitLab
```bash
git clone https://code.uic.edu.cn/workshop3/2025/b03/-/tree/master/code/code_b03
cd e-dba
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
# .env file already contains basic configuration:
DATABASE_URL=mysql://root:1234@localhost:3310/test1
# Update other settings as needed
```

```bash
    test_email = 'your_qq_email@qq.com' # receive code email

    # QQ mailbox SMTP server configuration
    smtp_server = 'smtp.qq.com'
    smtp_port = 587  # TLS端口

    # Configuration of the dedicated mailbox for the edba system
    SYSTEM_EMAIL = {
        'email': 'your_qq_email@qq.com', # send code email
        'password': 'your_SMTP_code'
    }
```
* Please replace your email in the function of `send_verification_email` in `app/contoller`, the `test_email` is to receving code during login e-dba system, the `system_email` is to send code during login.


4. Initialize the database
```bash
python init_db.py
```

5. Run the application
```bash
python run.py
```

## Environment Configuration
The application uses the following environment variables:

### Required Environment Variables
* `DATABASE_URL`: MySQL connection string (default: 'mysql://username:password@localhost/edba')
* `SECRET_KEY`: Secret key for session encryption

### Optional Environment Variables
* `FLASK_APP`: Entry point to the Flask application (default: run.py)
* `FLASK_ENV`: Environment (development/production)
* `FLASK_DEBUG`: Enable debug mode
* `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email server configuration


### Security Configuration
The application is configured with the following security settings:
* Sessions are HTTPS-only (`SESSION_COOKIE_SECURE = True`)
* JavaScript cannot access session cookies (`SESSION_COOKIE_HTTPONLY = True`)
* Session lifetime is limited to 30 minutes
* Upload directories are created at runtime
* Bank interface configuration must be present at `app/uploads/config/BankInterfaceInfo`

## Features
- **User Role Management**: Including T-Admin, E-Admin, Senior E-Admin, O-Convener, and data providers/consumers
- **Organization Registration**: Secure registration process requiring admin approval
- **Course Information Sharing**: Public access to educational course catalogs
- **Student Authentication**: Identity verification services for enrolled students and graduates
- **Student GPA Record Access**: Access student name, enroll year, graduation year, and GPA
- **Thesis Sharing**: Access control for academic papers (free or paid)
- **Financial Management**: Support for payment methods bank transfers
- **Comprehensive Logging**: Activity tracking for security and auditing
- **Interface Configuration**: Data providers can configure interfaces for students to verify their GPA records and papers


## User Access Levels
1. Public data access (Level 1)
2. Private data consumption (Level 2)
3. Private data provision (Level 3)

## Members
**Leader**: Zhou Le 2230016081
**Member**: Chen Yijing 2230016006
