# User story title: Admin Login and Dashboard

## Priority: High / 2

Admins need a secure login and a centralized dashboard to manage all items efficiently.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 2
* Linn Thant Soe Wai: 3
* Hlyan Wint Aung: 2

## Assumptions:

* Only admin users can access the dashboard.
* Admin login uses the same JWT-based auth system.
* Admins can view, update, and manage all items including returned ones.
* Statistics like item counts are calculated using backend aggregations.

## Description:

As an admin, I want to securely log in and access a dashboard so that I can manage posted items, update their status, and monitor activity on the platform.

## Tasks:

1. **Frontend:** Build login UI for admin with role-based access control.
2. **Frontend:** Create dashboard layout with cards for item stats and list view.
3. **Backend:** Implement admin-only routes for item listing, updates, and analytics.

## UI Design:

* Admin login form with input validation.
* Dashboard page with cards showing total items, returned items, etc.
* List view with edit and delete options for each item.
* Mobile-responsive layout using Material-UI grid system.

