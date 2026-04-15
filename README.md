# News Application Capstone Project - Consolidation

## Overview
This repository contains the consolidated version of the News Application capstone. It extends the earlier Django capstone by adding:

- version-control-ready project structure
- Sphinx documentation in the `docs/` folder
- a working `Dockerfile` for containerised execution
- a `requirements.txt` file for dependency installation
- a README that explains how to run the project with both `venv` and Docker

The application is a Django-based news platform where readers can browse approved content, journalists can create articles and newsletters, and editors can manage publishers and approve articles.

## Features
- Custom user model with Reader, Journalist, and Editor roles
- Role-aware registration and dashboard behaviour
- Article creation, editing, deletion, and editor approval workflow
- Newsletter creation with article selection
- Publisher management for editors
- Reader subscriptions to publishers and journalists
- REST API endpoints for articles, newsletters, publishers, and JWT authentication
- Approval notification workflow using email and an internal callback endpoint
- Automated Django tests
- Sphinx documentation with generated HTML output
- Docker support for simple deployment

## Project structure
```text
news_capstone_project_final_ready/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── capstone.txt
├── requirements.txt
├── manage.py
├── docs/
│   ├── Makefile
│   ├── source/
│   └── build/html/
├── news_project/
├── newsapp/
└── Planning/
```

## Requirements
- Python 3.12 or newer recommended
- pip
- Docker Desktop if you want to run the container version
- MariaDB if you want to use the database configuration from the original project brief

## Running the project with a virtual environment

### 1. Create and activate the environment
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file
Copy the example file and adjust the values.

Windows:
```bash
copy .env.example .env
```

Example values:
```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
USE_SQLITE=True
DB_NAME=news_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DEFAULT_FROM_EMAIL=no-reply@example.com
APPROVED_ARTICLE_CALLBACK_URL=http://127.0.0.1:8000/api/approved/
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser
```bash
python manage.py createsuperuser
```

### 6. Start the server
```bash
python manage.py runserver
```

The application will be available at:
- `http://127.0.0.1:8000/`
- `http://localhost:8000/`

## Running the project with Docker

### 1. Build the image
```bash
docker build -t news-capstone .
```

### 2. Run the container
```bash
docker run -p 8000:8000 news-capstone
```

### 3. Open the app
Visit:
- `http://127.0.0.1:8000/`

## Building the Sphinx documentation
From the project root:

```bash
cd docs
make html
```

The generated documentation entry point is:

```text
docs/build/html/index.html
```

## API endpoints
### Authentication
- `POST /api/token/`
- `POST /api/token/refresh/`

### Articles
- `GET /api/articles/`
- `POST /api/articles/`
- `GET /api/articles/<id>/`
- `PUT /api/articles/<id>/`
- `DELETE /api/articles/<id>/`
- `GET /api/articles/subscribed/`

### Newsletters
- `GET /api/newsletters/`
- `POST /api/newsletters/`

### Publishers
- `GET /api/publishers/`
- `POST /api/publishers/`

### Internal callback
- `POST /api/approved/`

## Tests
Run the test suite from the project root:

```bash
python manage.py test
```

## Notes on secrets
Do not commit secrets such as real passwords, tokens, or production keys to a public repository.
Use the `.env.example` file as a template and create your own local `.env` file.

## Submission checklist
- [x] `.gitignore` included
- [x] `requirements.txt` included
- [x] Sphinx documentation included in `docs/`
- [x] Dockerfile included
- [x] README included with `venv` and Docker instructions
- [x] Project source code included
- [x] Planning files included
- [x] Automated tests passing locally
- [x] `capstone.txt` included for GitHub repo link submission
