# User story title: Mark a Posted Item as Reclaimed

## Priority: Medium / 5

This feature is important for maintaining an accurate and up-to-date list of found items, preventing users from inquiring about items that have already been returned to their owners.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 3
* Linn Thant Soe Wai: 2
* Hlyan Wint Aung: 3

## Assumptions:

* Only the user who originally posted the found item can mark it as "Reclaimed".
* Once an item is marked as "Reclaimed", it should ideally be visually distinct in lists or perhaps moved to an archive/history section (though for an initial version, simply changing its status might suffice).
* The system needs a way to identify and manage the "Reclaimed" status.

## Description:

As a registered campus member who has previously posted a found item, I want to be able to update the status of that item to "Reclaimed" once the rightful owner has collected it. This will help keep the list of actively lost items accurate and reduce unnecessary inquiries.

## Tasks:

1.  **Backend:** Add a new status option (e.g., "Reclaimed") to the `ItemStatus` enum or create a separate boolean field (e.g., `is_reclaimed`).
2.  **Backend:** Create an API endpoint (e.g., `PATCH /items/{item_id}/reclaim`) that allows the original finder to update the item's status to "Reclaimed".
3.  **Backend:** Ensure that only the user who posted the item can call this endpoint for their item.
4.  **Frontend:** On a page displaying the user's own posted items (or on the item detail page if they are the finder), provide a button or action to "Mark as Reclaimed".
5.  **Frontend:** Implement the API call to update the item's status.
6.  **Frontend:** Update the UI to reflect the "Reclaimed" status (e.g., disable further actions, change visual style, or filter it out from the main "active" list).
7.  **Database:** Ensure the `Item` model and schema can accommodate the "Reclaimed" status.

## UI Design:

* **My Posted Items Page (New or Enhanced):** A logged-in user should be able to see a list of items they have personally posted.
* For each item in their list, there should be a clear button/option like "Mark as Reclaimed".
* Once an item is marked as reclaimed:
    * The button might change to "Reclaimed" (disabled) or disappear.
    * The item's card/listing might visually change (e.g., greyed out, a "Reclaimed" badge).
    * The item might no longer appear in the main public search results for "active" lost items, or be clearly marked.