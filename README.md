# HW_Web_13 (First part - FastAPI) User's email verification + Redis cash
In this homework, we continue to refine the REST API application from homework 12.

# Implemented required tasks:
- Implemented a mechanism for verifying the registered user's e-mail; 
      (The email verification process includes the following steps:

          - The user provides an email address during registration or account creation.
          - The system generates a unique verification token and sends it to the specified email address.
          - The user clicks on the verification link in the email, which takes them to a confirmation page on the website.
          - The site verifies that the validation token specified in the URL is valid and matches the email address.
          - If the verification token is valid, the site marks the email address as verified and the user is granted full access to the site's features.
          - If the verification token is invalid, the user is prompted to try again or request another verification email.)

- Limit the number of requests to your contact routes. Be sure to limit the speed of creating contacts for the user; 
- implemented  CORS Middleware for connecting to Client by API
- Implemented the ability to update the user's avatar. Use the Cloudinary service;

# general requirements:
- All environment variables stored in an .env file.
- Docker Compose is used to run all services and databases in the application;

# Implemented additional task:
- Implemented a caching mechanism using a Redis database. Cache the current user during authorization;

# Not implemented a password reset mechanism for the REST API application
      (password recovery process:

         - The user requests a password reset by entering their email address in the password reset form.
         - FastAPI generates a unique password reset token and sends an email with a password reset link to the user's email address. The link enables the password reset token as a parameter.
         - When the user clicks on the reset password link, FastAPI checks the password reset token and a form appears to enter a new password.
         - The user enters a new password and submits the form.
         - FastAPI updates the user's password and notifies the user.)


# HW_Web_12_JWT for RestAPI
In this homework, we continue to refine our REST API application from homework 11.

# Implemented required tasks:
- implemented an authentication mechanism in the application;
- Implemented an authorization mechanism using JWT tokens 
so that all operations with contacts are performed only by registered users;
- The user has access only to his transactions with contacts;

# Implemented additional tasks:
- for allowed operation  by privileges added next roles: user, moderator, admin;
- implemented  CORS Middleware for connecting to Client by API;


# general requirements
- When registering, if a user already exists with such an email, the server will return an HTTP 409 Conflict error;
- The server hashes the password and does not store it openly in the database;
- In case of successful user registration, the server should return the HTTP response status 201 Created and the new user's data;
- For all POST operations to create a new resource, the server returns a status of 201 Created;
- During the POST operation - user authentication, 
the server accepts a request with user data (email, password) in the body of the request;
- If the user does not exist or the password does not match, an HTTP 401 Unauthorized error is returned;
- the authorization mechanism using JWT tokens is implemented by 
a pair of tokens: the access token access_token and the update token refresh_token;



# HW_Web_11_RestAPI
The REST API for storing and managing contacts. 
The API build using the FastAPI infrastructure and use SQLAlchemy for database management.

# Contacts stored in the database and contain the following information:
-First Name
-Last Name
-E-mail address
-Phone number
-Birthday
-Favorite flag
-Additional data (optional)


# The API able to do the following:
-Create a new contact
-Get a list of all contacts
-Get one contact per ID
-Update an existing contact
-Patch favorite flag
-Delete contact

# In addition to the basic CRUD functionality, the API also have the following features:
-Contacts can be searchable by name, surname, phone or email address.
-The API able to retrieve a list of contacts with birthdays for the next {shift} days.
-The API has middlewares for: performance measuring, errors_handling
-The API has events for change favorite flag before insert or change contact, related with first name
-The APi has a template for visualisation of API (only model without implementation)


# general requirements:
-Used the FastAPI framework to create API
-Used ORM SQLAlchemy to work with the database
-PostgreSQL used as a database.
-Provide API documentation
-Used the Pydantic data validation module

# Start
- upload docker -> postgres
- uvicorn main:app --host localhost --port 8000 --reload  -> start application 
- http://127.0.0.1:8000/docs -> Swagger documentation
- http://127.0.0.1:8000/redoc -> Redoc documentation
- http://127.0.0.1:8000/ -> template
- alembic revision --autogenerate -m "name" -> generation of migration
- alembic upgrade head -> implementation to DB 
- docker-compose up -> up REdis+Postgress
- docker-compose down -> shut REdis+Postgress
