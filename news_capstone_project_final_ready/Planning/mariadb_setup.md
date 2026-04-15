# MariaDB Setup Note

This project supports MariaDB for final assessment.

## Required environment variables
- USE_SQLITE=False
- DB_NAME=news_db
- DB_USER=root
- DB_PASSWORD=your_password
- DB_HOST=localhost
- DB_PORT=3306

## Steps
1. Create an empty MariaDB database named `news_db` or update `DB_NAME`.
2. Install requirements from `requirements.txt`.
3. Run `python manage.py migrate` from the `news_project` folder.
4. Run `python manage.py test`.
5. Run `python manage.py runserver`.

The project also supports SQLite as a local fallback for quick development checks, but MariaDB is the target database for final assessment.
