# User story title: Mark Item as Returned

## Priority: Medium / 3

Returned items should no longer be visible to regular users but remain visible for admin auditing.

## Estimation: 2 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 1
* Linn Thant Soe Wai: 2
* Hlyan Wint Aung: 1

## Assumptions:

* Admins can mark found items as "returned".
* Once returned, items are hidden from the public user view.
* Returned items remain visible in the admin dashboard.

## Description:

As an admin, I want to be able to mark items as returned so that the system stays up to date and only active found items are shown to users.

## Tasks:

1. **Frontend:** Add a "Mark as Returned" button in the admin item view.
2. **Backend:** Create an endpoint to update item status to "returned".
3. **Frontend:** Update UI to hide returned items from public item listings.

## UI Design:

* Admin view includes a button or action menu for status update.
* Returned items show a clear "Returned" label in admin view.
* Public UI should not display returned items at all.
* Optionally add a status badge in the admin list view.

