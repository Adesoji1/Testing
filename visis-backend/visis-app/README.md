markdown```
File Structure
visis-app/
├── .venv/                      # Virtual environment
├── app/
│   ├── __init__.py             # Initialize the app module
│   ├── main.py                 # Main application entry point
│   ├── api/                    # API endpoints
│   │   ├── endpoints/
│   │   │   ├── admin/          # Admin-specific endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── settings.py
│   │   │   ├── user/           # User-specific endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── audiobooks.py
│   │   │   │   ├── bookmarks.py
│   │   │   │   ├── preferences.py
│   │   │   │   ├── scanning.py
│   │   │   │   ├── accessibility.py
│   │   │   │   ├── languages.py
│   │   │   │   ├── activities.py
│   │   │   │   ├── feedback.py
│   │   │   ├── middleware/      # Middleware
│   │   │   │   ├── ip_whitelist.py
│   ├── core/                   # Core functionalities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security-related functionalities
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── audiofile.py
│   │   ├── user_preference.py
│   │   ├── user_bookmark.py
│   │   ├── scanning_history.py
│   │   ├── accessibility.py
│   │   ├── language.py
│   │   ├── document_language.py
│   │   ├── audiobook_language.py
│   │   ├── user_activity.py
│   │   ├── feedback.py
│   │   └── app_setting.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── audiofile.py
│   │   ├── user_preference.py
│   │   ├── user_bookmark.py
│   │   ├── scanning_history.py
│   │   ├── accessibility.py
│   │   ├── language.py
│   │   ├── document_language.py
│   │   ├── audiobook_language.py
│   │   ├── user_activity.py
│   │   ├── feedback.py
│   │   └── app_setting.py
│   ├── services/               # Business logic and services
│   │   ├── __init__.py
│   │   └── document_service.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── send_reset_password_email.py
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_main.py
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
markdown```

## Setup Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/visis-backend.git
    cd visis-backend/visis-app
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory and add the necessary environment variables:
    ```properties
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    SQLALCHEMY_DATABASE_URL=your_database_url
    ```

5. **Run the application**:
    ```sh
    uvicorn app.main:app --reload --port 8081
    ```

6. **Run tests**:
    ```sh
    pytest
    ```

## Project Overview

This project is a backend service built with FastAPI, SQLAlchemy, and Pydantic. It includes user authentication, CRUD operations for users and documents, and unit tests.

## License

This project is licensed under the MIT License.
