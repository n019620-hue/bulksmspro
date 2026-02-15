# PR Tech Connect – Bulk Messaging Panel

A complete production-ready SaaS web application for bulk WhatsApp and SMS messaging.

## Features
- **Authentication System**: Role-based access (Admin/Client).
- **Admin Panel**: Manage users, add credits, and monitor activity.
- **Client Dashboard**: Upload CSV, compose messages, and send bulk WhatsApp/SMS.
- **WhatsApp Integration**: Meta WhatsApp Cloud API support.
- **SMS Integration**: Configurable URL-based SMS API.
- **Credit System**: Automatic deduction and balance management.
- **Responsive UI**: Built with Bootstrap 5.

## Tech Stack
- **Backend**: Python Flask
- **Database**: SQLite (SQLAlchemy)
- **Frontend**: Bootstrap 5, FontAwesome
- **Security**: Flask-Login, Werkzeug Password Hashing

## Installation
1. Extract the project files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your API credentials in `.env` or `config.py`.
4. Run the application:
   ```bash
   python app.py
   ```

## Default Credentials
- **Admin Username**: `admin`
- **Admin Password**: `admin123`

## File Structure
```text
pr_tech_connect/
├── app.py              # Main application logic
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Dependencies
├── .env                # Environment variables
├── instance/           # SQLite database storage
├── uploads/            # Temporary CSV storage
├── static/             # CSS/JS assets
└── templates/          # HTML templates
    ├── base.html
    ├── login.html
    ├── admin/
    │   └── dashboard.html
    └── client/
        └── dashboard.html
```
