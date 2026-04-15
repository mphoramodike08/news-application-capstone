Setup and run guide
===================

Run with a virtual environment
------------------------------

1. Create a virtual environment::

      python -m venv venv

2. Activate it.

   Windows::

      venv\Scripts\activate

3. Install dependencies::

      pip install -r requirements.txt

4. Copy the environment template::

      copy .env.example .env

5. Run migrations::

      python manage.py migrate

6. Start the server::

      python manage.py runserver

Run with Docker
---------------

1. Build the image::

      docker build -t news-capstone .

2. Run the container::

      docker run -p 8000:8000 news-capstone

3. Open the application at ``http://127.0.0.1:8000/``.
