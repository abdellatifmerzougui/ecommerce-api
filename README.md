# E-Commerce REST API

A production-ready E-Commerce REST API built with Django REST Framework, PostgreSQL, Docker, and JWT authentication.

## Features

### Authentication

* User registration
* JWT authentication
* Access and refresh tokens
* User-specific permissions

### Products

* Product and category management
* Product images
* Search
* Filtering
* Ordering
* Pagination
* Staff-only product management

### Shopping Cart

* User-specific shopping cart
* Add products to cart
* Increase quantity for existing products
* Update cart items
* Delete cart items
* Stock validation
* Active product validation
* Automatic subtotal calculation
* Automatic cart total calculation

### Orders and Checkout

* Checkout API
* Order creation
* Order items
* Purchase-price snapshot
* Automatic stock reduction
* Cart clearing after checkout
* Transactional checkout using database transactions
* Row locking for stock and cart operations
* Order history
* Order detail
* Order status workflow

### Order Status

```text
PENDING
   |
   v
CONFIRMED
   |
   v
SHIPPED
   |
   v
DELIVERED
```

Cancellation is supported from the `PENDING` state.

Only staff users can change order status.

## Tech Stack

* Python
* Django 6.1.1
* Django REST Framework 3.18.1
* PostgreSQL 18
* Simple JWT
* django-filter
* drf-spectacular
* Gunicorn
* WhiteNoise
* Docker
* Docker Compose

## API Documentation

Swagger / OpenAPI documentation:

```text
http://127.0.0.1:8000/api/docs/
```

## Run with Docker

Clone the repository:

```bash
git clone <your-repository-url>
cd ecommerce-api
```

Create your environment file:

```bash
cp .env.example .env
```

Start the application:

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Swagger documentation:

```text
http://127.0.0.1:8000/api/docs/
```

## Run Tests

Run the complete test suite:

```bash
docker compose exec web python manage.py test
```

The project currently contains 17 automated tests covering:

* Authentication
* Products
* Permissions
* Cart
* Stock validation
* Checkout
* Orders
* Order ownership
* Order status transitions

## Project Structure

```text
ecommerce-api/
|
├── config/
|   ├── settings.py
|   ├── urls.py
|   ├── wsgi.py
|   └── ...
|
├── users/
|   ├── models.py
|   ├── serializers.py
|   ├── views.py
|   ├── permissions.py
|   └── tests.py
|
├── products/
|   ├── models.py
|   ├── serializers.py
|   ├── views.py
|   └── tests.py
|
├── orders/
|   ├── models.py
|   ├── serializers.py
|   ├── views.py
|   ├── permissions.py
|   └── tests.py
|
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py
```

## Environment Variables

Create a `.env` file containing values similar to:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=543
```
