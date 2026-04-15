Project overview
================

The News Application is a Django project that supports three main user roles:
readers, journalists, and editors.

Key features
------------

* Readers can browse approved articles and newsletters.
* Readers can subscribe to publishers and journalists.
* Journalists can create articles and newsletters.
* Editors can approve articles and manage publishers.
* The project exposes REST API endpoints secured with JWT authentication.
* Approved article notifications are sent by email and logged to an internal API.

Main application flow
---------------------

#. A journalist creates an article.
#. An editor reviews and approves the article.
#. The application sends subscriber notifications.
#. Approved content becomes visible on the site and API.
