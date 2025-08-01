# User story title: User Profile Management

## Priority: High / 3

This functionality provides users with a personal dashboard to manage their account information, view their activity history, and track their posted items and claims.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 3
* Linn Thant Soe Wai: 3
* Hlyan Wint Aung: 3

## Assumptions:

* Users must be authenticated to access their profile.
* Profile information can be updated except for email (which requires verification).
* Users can view all items they have posted and their current status.
* Users can see the history of their claim requests and outcomes.
* Profile includes activity statistics and summary information.

## Description:

As a registered user of the Lost & Found system, I want to have a personal profile page where I can view and update my account information, see all the items I have posted, track my claim requests, and monitor my overall activity on the platform. This helps me manage my account and stay updated on my Lost & Found activities.

## Tasks:

1. **Backend:** Create API endpoint for retrieving user profile information.
2. **Backend:** Implement API for updating user profile data.
3. **Backend:** Create endpoints for user's posted items with pagination.
4. **Backend:** Implement endpoints for user's claim history.
5. **Frontend:** Design profile overview page with user statistics.
6. **Frontend:** Create profile editing form with validation.
7. **Frontend:** Implement posted items management interface.
8. **Frontend:** Design claim history display with status tracking.
9. **Frontend:** Add profile navigation and settings menu.
10. **Security:** Ensure users can only access and modify their own profile data.

## UI Design:

### Profile Overview:
* User avatar/photo (uploadable)
* Name and email display
* Registration date and member status
* Activity statistics (items posted, claims made, successful matches)
* Quick action buttons (Post New Item, View Claims)

### Profile Editor:
* Full Name (Text Input)
* Contact Phone (Text Input, optional)
* Campus Department/Faculty (Dropdown)
* Preferred Contact Method (Radio buttons)
* Bio/Description (Text Area, optional)
* Save Changes Button
* Cancel Button

### Posted Items Section:
* Grid/list view of all posted items
* Item thumbnail, title, and status
* Date posted and last updated
* Status indicators (Available, Claimed, Returned)
* Quick actions (Edit, Mark as Returned, Delete)
* Pagination for large lists
* Filter by status options

### Claims History Section:
* List of all submitted claims
* Item details and claim date
* Status progression (Submitted → Under Review → Approved/Rejected)
* Outcome details and contact information
* Ability to withdraw pending claims
* Success rate statistics

### Account Settings:
* Change password option
* Email preferences for notifications
* Privacy settings
* Account deletion option
* Export data option
