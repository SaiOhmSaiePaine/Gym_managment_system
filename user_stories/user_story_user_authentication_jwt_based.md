# User story title: User Authentication (JWT-based)

## Priority: High / 1

This is essential for secure and personalized access to the system.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 3
* Linn Thant Soe Wai: 2
* Hlyan Wint Aung: 2

## Assumptions:

* Users need to securely register, log in, and maintain session state.
* The system uses JWT (JSON Web Tokens) for authentication.
* User passwords are securely hashed and stored in the database.
* A login token is required to access user-protected endpoints.

## Description:

As a campus user, I want to securely register and log in to the system so that I can post lost/found items and access protected features.

## Tasks:

1. **Backend:** Implement secure user registration with password hashing.
2. **Backend:** Set up JWT generation and validation for login sessions.
3. **Frontend:** Create login and registration UI forms and store the token for authenticated sessions.

## UI Design:

* A login page and a registration page with input fields for email, password, and confirm password.
* Feedback for incorrect login or registration attempts.
* On success, users are redirected to the main interface with session info stored (e.g., in localStorage or context).
* Optional "Remember Me" checkbox for persistent login.

