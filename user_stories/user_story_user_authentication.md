# User story title: User Registration and Login

## Priority: High / 3

Essential for identifying users who post items and for secure interactions.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 3
* Linn Thant Soe Wai: 3
* Hlyan Wint Aung: 3

## Assumptions:

* A simple username and password-based registration system is sufficient.
* Passwords will be securely hashed and stored.
* JWT (JSON Web Tokens) will be used for session management after login.
* Basic validation for username (uniqueness) and password strength.

## Description:

As a campus member, I want to be able to register for an account using a username and password, and then log in to the system securely. This will allow me to post found items and potentially manage my posts.

## Tasks:

1.  **Backend:** Create API endpoints for user registration (`/auth/register`).
2.  **Backend:** Implement password hashing upon registration.
3.  **Backend:** Create API endpoint for user login (`/auth/token`) that returns a JWT.
4.  **Backend:** Implement logic to verify credentials and issue JWTs.
5.  **Frontend:** Design and implement registration and login forms.
6.  **Frontend:** Handle API calls for registration and login.
7.  **Frontend:** Store JWT securely (e.g., localStorage) and include it in headers for authenticated requests.
8.  **Frontend:** Implement logout functionality (clearing the token).
9.  **Database:** Update user schema to store username and hashed password.

## UI Design:

* Separate pages/modals for Registration and Login.
* Registration Form: Username, Password, Confirm Password fields.
* Login Form: Username, Password fields.
* Clear error messages for invalid input or failed attempts.
* Links to switch between Registration and Login.
