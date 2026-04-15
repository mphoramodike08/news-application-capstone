# Database Design Summary

## Main Entities
- **CustomUser**: stores authentication information and the application role.
- **Publisher**: stores publisher details and relationships to editors, journalists, and subscribers.
- **Article**: stores article content, approval status, author, and publisher.
- **Newsletter**: stores curated content collections and linked articles.

## Normalisation Notes
- Repeating data is reduced by keeping publishers, users, articles, and newsletters in separate tables.
- Many-to-many relationships are used for publisher subscribers, publisher staff, newsletter articles, and journalist subscriptions.
- Articles link to a single author and publisher using foreign keys.
- Newsletters link to a single creator and publisher, while supporting multiple related articles.
