# User story title: Post a Found Item

## Priority: High / 1

This is a core functionality allowing users to report items they've found, making them visible to others.

## Estimation: 4 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 4
* Linn Thant Soe Wai: 4
* Hlyan Wint Aung: 5

## Assumptions:

* Users must be registered and logged in to post a found item.
* The system will allow image uploads for the found item.
* Location details (block, level) are mandatory.
* Item status (kept personally, sent to One Stop, left at location) is mandatory.
* Contact information will be derived from the logged-in user's profile if the item is "kept personally".

## Description:

As a registered campus member (student or staff), I want to be able to easily post details of an item I have found on campus, including its name, a description, a picture, where I found it (block and level), and how I am currently keeping the item. This will help others who have lost items to find them.

## Tasks:

1.  **Backend:** Create API endpoint to receive and store found item details (name, description, location, status, image URL, finder's username).
2.  **Backend:** Implement image upload functionality to AWS S3 and store the image URL.
3.  **Frontend:** Design and implement a user-friendly form for submitting found item details.
4.  **Frontend:** Integrate image upload functionality in the form.
5.  **Frontend:** Ensure form validation for required fields.
6.  **Database:** Update schema to store found item information, linking to the user who posted it.
7.  **Security:** Ensure only authenticated users can post items.

## UI Design:

* A clear form with fields for:
    * Item Name/Title (Text Input)
    * Description (Text Area)
    * Image Upload (File Input)
    * Location - Block (Text Input / Dropdown)
    * Location - Level (Text Input / Dropdown)
    * Status (Dropdown: "Kept personally by me", "Sent to One Stop Center", "Found and left at location")
* Submit Button.
* Success/Error messages upon submission.
