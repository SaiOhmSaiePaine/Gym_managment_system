# User story title: View and Search Found Items

## Priority: High / 2

This is the primary way for users who have lost items to find them.

## Estimation: 4 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 5
* Linn Thant Soe Wai: 3
* Hlyan Wint Aung: 4

## Assumptions:

* All users (registered or anonymous) can view the list of found items.
* The list will display key information: item name, image (if available), location found, status, and date posted.
* Basic search functionality by item name/keywords will be available.
* Filtering by item status will be available.

## Description:

As a campus member, I want to be able to view a list of all recently found items and search/filter this list so that I can try to find an item I have lost.

## Tasks:

1.  **Backend:** Create API endpoint to fetch a list of all found items, with pagination.
2.  **Backend:** Implement search functionality (e.g., by item name, description keywords).
3.  **Backend:** Implement filtering functionality (e.g., by status, location - advanced).
4.  **Frontend:** Design and implement a page to display found items in a clear, browseable format (e.g., cards or list view).
5.  **Frontend:** Implement UI elements for searching and filtering.
6.  **Frontend:** Display item details including image, name, location, status, and date.
7.  **Frontend:** Implement a "Contact Finder" button/mechanism for items "kept personally".

## UI Design:

* A main page displaying a grid or list of item cards.
* Each card showing a thumbnail image, item name, brief location, and status.
* A search bar at the top.
* Filter options (e.g., dropdowns or buttons for item status).
* Clicking an item could show more details (or the card itself has all necessary info).
