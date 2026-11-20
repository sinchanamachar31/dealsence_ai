
# 📸 FastAPI Instagram Clone API

A backend API built with **FastAPI** that mimics Instagram’s core features such as authentication, posting images, liking, and commenting.

---

## 🚀 Features

* User authentication & authorization (JWT-based)
* Create, update, and delete posts
* Add Post title, description, caption, Images
* Like & comment on posts
* PostgreSQL database configured through `DATABASE_URL`
* Organized project structure (auth, database, routes, schema)
* Automatic API docs with **Swagger** & **ReDoc**

---

## 📂 Project Structure

```bash
Instagram_Clone/
│── Instagram/
│   ├── auth/             # Authentication logic
│   ├── database/         # Database connection/config
│   ├── images/           # Uploaded images
│   ├── routes/           # API routes (users, posts, comments, etc.)
│   ├── schema/           # Pydantic schemas
│   ├── instagram_api.db  # SQLite database
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Dependencies for this app
│
├── instagram_env/        # Virtual environment (ignored in git)
├── react_app/            # Frontend (React project)
├── .gitignore
└── requirements.txt      # Root dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/fastapi-instagram-clone.git
cd FastAPI/Instagram_Clone
```

### 2️⃣ Create & activate virtual environment

```bash
# Create virtual environment
python -m venv instagram_env

# Activate venv (Windows)
instagram_env\Scripts\activate

# Activate venv (Mac/Linux)
source instagram_env/bin/activate
```

### 3️⃣ Configure local services

Create a PostgreSQL database (for example, `instagram_db`). If `.env` does not
exist, copy `.env.example` to `.env` at the repository root. If it already
exists, keep it and update `DATABASE_URL` to your PostgreSQL username, password,
host, port, and database name.

Generate a private JWT key locally:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put the generated value in `SECRET_KEY` in `.env`. Do not commit `.env` or paste
database credentials or the JWT key into chat.

For local development, copy `frontend/.env.example` to
`frontend/.env.local`. The React app defaults to the API at
`http://localhost:8000` even if you do not create this optional file.

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
cd frontend
npm install
```

### 5️⃣ Run the applications

Start the backend from the repository root:

```bash
uvicorn Instagram.main:app --reload
```

Server will start at 👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

In another terminal, start the frontend:

```bash
cd frontend
npm start
```

Restart React after changing `frontend/.env.local`. For hosted deployments, set
`REACT_APP_API_URL` on the frontend host and `DATABASE_URL` and `SECRET_KEY` on
the backend host.

---

## 📑 API Documentation

* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🎯 Future Enhancements

* Add image storage in AWS S3 / Cloudinary
* Implement notifications & stories
* Dockerize the application

---

✅ Now you can run your **Instagram Clone API** locally with just a few commands.
