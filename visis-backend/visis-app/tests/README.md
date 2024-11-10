README.md

 file that explains all the endpoints in your codebase, including the purpose of each endpoint and how to use them.

---

# Project Name

## Overview

This project is a backend service built with FastAPI and SQLAlchemy. It provides endpoints for user authentication, managing bookmarks, and user preferences. The service interacts with a PostgreSQL database to store user data, bookmarks, and preferences.

## Table of Contents

- Installation
- Configuration
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - Authentication
  - Bookmarks
  - Preferences
- Models
- Schemas
- Contributing
- License

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**

   Ensure you have PostgreSQL installed and running. Create a database for the project.

   ```bash
   createdb yourdatabase
   ```

5. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

## Configuration

Create a 

.env

 file in the project root with the following environment variables:

```env
DATABASE_URL=postgresql://username:password@localhost/yourdatabase
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

1. **Start the FastAPI server:**

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation:**

   Open your browser and navigate to `http://127.0.0.1:8000/docs` to view the interactive API documentation.

## API Endpoints

### Authentication

#### `POST /token`

Authenticate a user and obtain an access token.

- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- **Response:**
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### Bookmarks

#### `POST /bookmarks/`

Create a new bookmark for the current user.

- **Request Body:**
  ```json
  {
    "document_id": 1,
    "audiobook_id": null,
    "position": "string"
  }
  ```

- **Response:**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "document_id": 1,
    "audiobook_id": null,
    "position": "string",
    "date_created": "2023-01-01T00:00:00"
  }
  ```

#### `GET /bookmarks/`

Retrieve all bookmarks for the current user.

- **Response:**
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "document_id": 1,
      "audiobook_id": null,
      "position": "string",
      "date_created": "2023-01-01T00:00:00"
    }
  ]
  ```

#### `DELETE /bookmarks/{bookmark_id}`

Delete a bookmark by ID for the current user.

- **Response:**
  ```json
  {
    "detail": "Bookmark deleted successfully"
  }
  ```

### Preferences

#### `GET /preferences/`

Retrieve the current user's preferences.

- **Response:**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "text_to_speech_voice": "string",
    "playback_speed": "string",
    "preferred_language": "string"
  }
  ```

#### `POST /preferences/`

Create preferences for the current user.

- **Request Body:**
  ```json
  {
    "text_to_speech_voice": "string",
    "playback_speed": "string",
    "preferred_language": "string"
  }
  ```

- **Response:**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "text_to_speech_voice": "string",
    "playback_speed": "string",
    "preferred_language": "string"
  }
  ```

#### `PUT /preferences/`

Update the current user's preferences.

- **Request Body:**
  ```json
  {
    "text_to_speech_voice": "string",
    "playback_speed": "string",
    "preferred_language": "string"
  }
  ```

- **Response:**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "text_to_speech_voice": "string",
    "playback_speed": "string",
    "preferred_language": "string"
  }
  ```

#### `DELETE /preferences/`

Delete the current user's preferences.

- **Response:**
  ```json
  {
    "detail": "Preferences deleted successfully"
  }
  ```

## Models

### User

- **Fields:**
  - 

id

: Integer, primary key
  - `username`: String, unique
  - `email`: String, unique
  - `hashed_password`: String
  - `bookmarks`: Relationship to 

UserBookmark


  - `preferences`: Relationship to `UserPreference`

### UserBookmark

- **Fields:**
  - 

id

: Integer, primary key
  - 

user_id

: Foreign key to `User`
  - 

document_id

: Foreign key to `Document`, nullable
  - 

audiobook_id

: Foreign key to `Audiobook`, nullable
  - 

position

: String
  - 

date_created

: DateTime, default to current timestamp

### UserPreference

- **Fields:**
  - 

id

: Integer, primary key
  - 

user_id

: Foreign key to `User`, unique
  - `text_to_speech_voice`: String
  - `playback_speed`: String
  - `preferred_language`: String

## Schemas

### UserBookmark

- **UserBookmarkBase**
  - 

document_id

: Optional Integer
  - 

audiobook_id

: Optional Integer
  - 

position

: String

- **UserBookmarkCreate**
  - Inherits from `UserBookmarkBase`

- **UserBookmarkResponse**
  - Inherits from `UserBookmarkBase`
  - 

id

: Integer
  - 

user_id

: Integer
  - 

date_created

: DateTime

### UserPreference

- **UserPreferenceBase**
  - `text_to_speech_voice`: Optional String
  - `playback_speed`: Optional String
  - `preferred_language`: Optional String

- **UserPreferenceCreate**
  - Inherits from `UserPreferenceBase`
  - All fields required

- **UserPreferenceUpdate**
  - Inherits from `UserPreferenceBase`

- **UserPreferenceResponse**
  - Inherits from `UserPreferenceBase`
  - 

id

: Integer
  - 

user_id

: Integer

## Contributing

1. **Fork the repository**
2. **Create a new branch**
3. **Make your changes**
4. **Submit a pull request**

## License

This project is licensed under the MIT License.

---

Let me know if you need any further adjustments or additional information!

Ad163: explain the document endpoint in details I need their readme

GitHub Copilot: Sure! Below is a detailed explanation of the document endpoints, including their purpose, request and response formats, and usage examples. This can be included in your 

README.md

 file.

---

## Document Endpoints

The document endpoints allow users to upload, list, update, delete, and retrieve statistics about their documents. These endpoints interact with the document processing service, which includes OCR (Optical Character Recognition) and TTS (Text-to-Speech) functionalities.

### **Upload Document**

#### `POST /documents/`

Upload a new document for the current user.

- **Request:**
  - **Headers:**
    - `Authorization: Bearer <token>`
  - **Body:**
    - 

file

: The document file to upload (multipart/form-data).
    - 

is_public

: Optional boolean indicating if the document should be public (default: `false`).

- **Response:**
  - **Status Code:** `201 Created`
  - **Body:**
    ```json
    {
      "id": 1,
      "title": "document.pdf",
      "author": "username",
      "file_type": "application/pdf",
      "file_key": "folder/1/document.pdf",
      "url": "https://s3.amazonaws.com/bucket/folder/1/document.pdf",
      "is_public": false,
      "upload_date": "2023-01-01T00:00:00",
      "processing_status": "pending",
      "processing_error": null,
      "audio_url": null,
      "audio_key": null,
      "detected_language": null,
      "tags": []
    }
    ```

- **Example:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/documents/" \
       -H "Authorization: Bearer <token>" \
       -F "file=@/path/to/document.pdf" \
       -F "is_public=false"
  ```

### **List Documents**

#### `GET /documents/`

Retrieve a list of documents belonging to the current user.

- **Request:**
  - **Headers:**
    - `Authorization: Bearer <token>`
  - **Query Parameters:**
    - 

skip

: Optional integer to skip a number of documents (default: `0`).
    - 

limit

: Optional integer to limit the number of documents returned (default: `10`).
    - 

search

: Optional string to search for documents by title.
    - 

status

: Optional string to filter documents by processing status.
    - 

file_type

: Optional string to filter documents by file type.
    - 

start_date

: Optional datetime to filter documents uploaded after this date.
    - 

end_date

: Optional datetime to filter documents uploaded before this date.

- **Response:**
  - **Status Code:** `200 OK`
  - **Body:**
    ```json
    [
      {
        "id": 1,
        "title": "document.pdf",
        "author": "username",
        "file_type": "application/pdf",
        "file_key": "folder/1/document.pdf",
        "url": "https://s3.amazonaws.com/bucket/folder/1/document.pdf",
        "is_public": false,
        "upload_date": "2023-01-01T00:00:00",
        "processing_status": "completed",
        "processing_error": null,
        "audio_url": "https://s3.amazonaws.com/bucket/folder/1/document.mp3",
        "audio_key": "folder/1/document.mp3",
        "detected_language": "en",
        "tags": []
      }
    ]
    ```

- **Example:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/documents/?limit=5" \
       -H "Authorization: Bearer <token>"
  ```

### **Update Document**

#### `PUT /documents/{document_id}`

Update an existing document's metadata.

- **Request:**
  - **Headers:**
    - `Authorization: Bearer <token>`
  - **Body:**
    ```json
    {
      "title": "new_title.pdf",
      "author": "new_author",
      "is_public": true,
      "description": "Updated description",
      "tags": ["tag1", "tag2"]
    }
    ```

- **Response:**
  - **Status Code:** `200 OK`
  - **Body:**
    ```json
    {
      "id": 1,
      "title": "new_title.pdf",
      "author": "new_author",
      "file_type": "application/pdf",
      "file_key": "folder/1/document.pdf",
      "url": "https://s3.amazonaws.com/bucket/folder/1/document.pdf",
      "is_public": true,
      "upload_date": "2023-01-01T00:00:00",
      "processing_status": "completed",
      "processing_error": null,
      "audio_url": "https://s3.amazonaws.com/bucket/folder/1/document.mp3",
      "audio_key": "folder/1/document.mp3",
      "detected_language": "en",
      "tags": ["tag1", "tag2"]
    }
    ```

- **Example:**
  ```bash
  curl -X PUT "http://127.0.0.1:8000/documents/1" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{
             "title": "new_title.pdf",
             "author": "new_author",
             "is_public": true,
             "description": "Updated description",
             "tags": ["tag1", "tag2"]
           }'
  ```

### **Delete Document**

#### `DELETE /documents/{document_id}`

Delete a document by its ID.

- **Request:**
  - **Headers:**
    - `Authorization: Bearer <token>`

- **Response:**
  - **Status Code:** `200 OK`
  - **Body:**
    ```json
    {
      "detail": "Document deleted successfully"
    }
    ```

- **Example:**
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/documents/1" \
       -H "Authorization: Bearer <token>"
  ```

### **Get Document Statistics**

#### `GET /documents/stats`

Get statistics about the documents of the current user.

- **Request:**
  - **Headers:**
    - `Authorization: Bearer <token>`

- **Response:**
  - **Status Code:** `200 OK`
  - **Body:**
    ```json
    {
      "total_documents": 10,
      "processed_documents": 8,
      "failed_documents": 2,
      "total_storage_used": 50.5  # in MB
    }
    ```

- **Example:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/documents/stats" \
       -H "Authorization: Bearer <token>"
  ```

---

### **Summary**

- **Upload Document (`POST /documents/`)**: Allows users to upload a new document. The document is stored in S3, and a record is created in the database.
- **List Documents (`GET /documents/`)**: Retrieves a list of documents belonging to the current user, with optional filtering and pagination.
- **Update Document (`PUT /documents/{document_id}`)**: Updates the metadata of an existing document.
- **Delete Document (`DELETE /documents/{document_id}`)**: Deletes a document by its ID.
- **Get Document Statistics (`GET /documents/stats`)**: Provides statistics about the user's documents, including total documents, processed documents, failed documents, and total storage used.

These endpoints provide comprehensive functionality for managing documents, including uploading, listing, updating, deleting, and retrieving statistics. The integration with OCR and TTS services allows for advanced document processing capabilities.

---

Let me know if you need any further details or adjustments!