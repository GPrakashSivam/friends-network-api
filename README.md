
# Friends Social Network Management API

## Overview

This is a Django-based RESTful API for managing user registration/login, friend requests, friendships, blocking/unblocking users, and logging user activity. The project uses JWT for authentication and includes rate-limiting to prevent abuse. Redis has been integrated for caching, and PostgreSQL is used as the database.

## Features
- User registration and authentication (JWT)
- Role-based access control (RBAC)
- Friend request management (send/accept/reject requests)
- Friendships listing with caching for optimized performance
- Blocking and unblocking users
- Rate-limiting to prevent request spam
- User activity logging
- Admin panel access for managing users and requests
- Detailed API documentation using drf-spectacular

## Project Structure

```
friends_network_api/
├── friends/                    # Friends Network app
│   ├── migrations/             # Migration files for the app
│   ├── admin.py                # Admin registration for models
│   ├── apps.py                 # App configuration
│   ├── models.py               # Database models (User, FriendRequest, etc.)
│   ├── serializers.py          # Serializers for data validation
│   ├── urls.py                 # API endpoint routing
│   ├── views.py                # API view logic
│   └── tests.py                # Unit tests for the API
├── friends_network/            # Main Django project configuration
│   ├── settings.py             # Main Django project Settings
│   ├── urls.py                 # Main project URL routing    
│   └── wsgi.py                 # Webserver Config settings  
├── manage.py                   # Django project management script
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis
- Git

### Step-by-Step Guide

1. **Clone the repository**:
    ```bash
    git clone https://github.com/GPrakashSivam/friends-network-api.git
    cd friends-network-api
    ```

2. **Set up virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # For Windows, use venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following:
    ```env
    SECRET_KEY=<your_secret_key>
    DEBUG=True
    DATABASE_URL=postgres://dev_user:password@localhost:5432/projects_db
    REDIS_URL=redis://localhost:6379/1
    ```

5. **Set up the PostgreSQL database**:
    - Create the database:
      ```bash
      sudo -u postgres psql
      CREATE DATABASE projects_db;
      CREATE USER dev_user WITH PASSWORD 'password';
      ALTER ROLE dev_user SET client_encoding TO 'utf8';
      ALTER ROLE dev_user SET default_transaction_isolation TO 'read committed';
      ALTER ROLE dev_user SET timezone TO 'IST';
      GRANT ALL PRIVILEGES ON DATABASE projects_db TO dev_user;
      ```

6. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

7. **Create a superuser**:
    ```bash
    python manage.py createsuperuser
    ```

8. **Start the Redis server** (if not already running):
    ```bash
    redis-server
    ```

9. **Run the Django development server**:
    ```bash
    python manage.py runserver
    ```

10. **Access the admin panel**:
    - Visit `http://localhost:8000/admin` and log in with the superuser credentials.

### Docker Deployment

To containerize and run the application using Docker, follow these steps: (Ensure Docker is installed on your system)

Run Docker Compose: In the project root directory (where the docker-compose.yml file is located), run the following command to build and start the services:

docker-compose up --build

Access the API: Once the containers are running, the Django app will be accessible at http://localhost:8000, PostgreSQL at port 5432, and Redis at port 6379.

### Postman Collection

To simplify testing the API, a public Postman collection has been created. You can use the following link to import the collection directly into your Postman workspace:

Postman Collection URL: [https://www.postman.com/gnanaprakashsiv/postman-friends-network-api/collection/n4u25ug/friends-network-api]

This collection includes all the API endpoints, with predefined requests for sending friend requests, user login, search, and more. Simply import the collection and use the generated JWT tokens in the authorization headers to test the API.

## API Documentation

The API is documented using `drf-spectacular`. You can access the documentation via the following routes:
- **Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- **Swagger UI**: [http://localhost:8000/api/docs/swagger/](http://localhost:8000/api/docs/swagger/)
- **Redoc**: [http://localhost:8000/api/docs/redoc/](http://localhost:8000/api/docs/redoc/)

### Endpoints

#### Authentication

- **Sign Up**: `POST /api/signup/`
- **Log In**: `POST /api/login/`
- **Token Refresh**: `POST /api/token/refresh/`

#### Friend Requests

- **Send Friend Request**: `POST /api/friend-request/send/`
- **Accept Friend Request**: `POST /api/friend-request/accept/`
- **Reject Friend Request**: `POST /api/friend-request/reject/`
- **Pending Friend Requests**: `GET /api/friend-requests/pending/`
- **Friends List**: `GET /api/friends/`

#### Blocking

- **Block User**: `POST /api/block/`
- **Unblock User**: `POST /api/unblock/`

#### User Activity

- **User Activity List**: `GET /api/activities/`

## Design Choices

### JWT Authentication
- **Why**: Stateless authentication, better suited for distributed systems.
- **How**: JWT tokens are stored securely via HttpOnly cookies. On login, an access token and refresh token are generated.

### Rate Limiting
- **Why**: To prevent brute force and spam attacks.
- **How**: Rate-limiting is implemented for sensitive endpoints like login and sending friend requests.

### Caching with Redis
- **Why**: To optimize performance by caching frequently accessed data like user friends lists and user activity.
- **How**: Redis is used for caching and session management, reducing load on the database.

### Atomic Transactions
- **Why**: To prevent race conditions in critical operations like accepting or rejecting friend requests.
- **How**: Django’s `atomic` decorator is used to ensure the database operations are atomic.

### Modularization
- **Why**: To keep code maintainable and organized. User-related models, serializers, and views are separated from friendship-related logic.

## Testing

Run unit tests using Django's test framework:
```bash
python manage.py test
```

## Future Improvements

- **Add WebSockets**: Real-time updates for friend requests and user activities.
- **Improve Caching**: Implement more granular cache invalidation for specific users.
- **API Throttling**: Apply more specific throttling rules based on user roles.

## Contributing

Feel free to open issues or pull requests if you find any bugs or want to suggest new features.

---

*Created with ❤️ by Gnanaprakash*
