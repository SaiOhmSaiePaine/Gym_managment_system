# User story title: Filter Found Items by Status

## Priority: Medium / 4

Enhances the user experience by allowing seekers to narrow down their search.

## Estimation: 2 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 2
* Linn Thant Soe Wai: 1
* Hlyan Wint Aung: 2

## Assumptions:

* The primary filter needed initially is by the item's "status" (Kept personally, Sent to One Stop Center, Found and left at location).
* The backend API for fetching items can accept a status filter parameter.
* The frontend will provide clear UI elements to apply these filters.

## Description:

As a campus member looking for a lost item, I want to be able to filter the list of found items based on how the item is being kept (e.g., "Sent to One Stop Center") so I can more efficiently search in relevant places or for items I can directly inquire about.

## Tasks:

1.  **Backend:** Modify the API endpoint for fetching items (`/items/`) to accept an optional `status` query parameter.
2.  **Backend:** Update the database query in `crud_item.py` to filter by status if the parameter is provided.
3.  **Frontend:** Add UI elements (e.g., buttons, dropdown) to the item listing page to allow users to select a status filter.
4.  **Frontend:** When a filter is applied, re-fetch the item list from the backend with the appropriate status parameter.
5.  **Frontend:** Clearly indicate which filter is currently active.

## UI Design:

* A set of filter buttons or a dropdown menu on the "View Found Items" page.
* Options: "All", "Kept Personally", "Sent to One Stop Center", "Left at Location".
* The item list should dynamically update when a filter is selected.
