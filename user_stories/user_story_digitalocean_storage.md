# User story title: Connect and Store Data on DigitalOcean PostgreSQL

## Priority: High / 3

Cloud-hosted database improves scalability and reliability for real-world deployment.

## Estimation: 2 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 1
* Linn Thant Soe Wai: 2
* Hlyan Wint Aung: 1

## Assumptions:

* A managed PostgreSQL instance will be provisioned on DigitalOcean.
* Secure credentials and connection strings will be stored in environment variables.
* Existing data schemas will be migrated and tested.

## Description:

As a developer, I want to store and retrieve application data from a managed PostgreSQL instance on DigitalOcean so that I can ensure reliable, cloud-based data access for our app.

## Tasks:

1. **DevOps:** Provision a managed PostgreSQL instance on DigitalOcean.
2. **Backend:** Update database config to connect using DigitalOcean credentials.
3. **Backend:** Migrate schema and test CRUD operations on the cloud database.

## UI Design:

* No frontend UI required.
* Developers should test connection via backend logging and success messages.
* Include fallback to local PostgreSQL if cloud connection fails (for development mode).

