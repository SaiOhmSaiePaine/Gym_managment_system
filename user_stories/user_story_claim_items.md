# User story title: Claim Lost Items

## Priority: High / 2

This functionality allows users to request ownership of found items by submitting claim requests with verification details.

## Estimation: 3 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 3
* Linn Thant Soe Wai: 3
* Hlyan Wint Aung: 3

## Assumptions:

* Users must be authenticated to submit claim requests.
* Claim requests require detailed descriptions for verification.
* Item finders will receive notifications about claim requests.
* Claims can be approved or rejected by the item finder or admin.
* Multiple users can claim the same item, but only one claim can be approved.

## Description:

As a registered campus member who has lost an item, I want to be able to submit a claim request for items I believe belong to me. I should provide detailed information about the item to verify my ownership, and the person who found the item should be able to review and approve my claim.

## Tasks:

1. **Backend:** Create API endpoint for submitting claim requests.
2. **Backend:** Implement claim status tracking (pending, approved, rejected).
3. **Backend:** Create notification system for claim events.
4. **Backend:** Design database schema for claims with relationships to items and users.
5. **Frontend:** Design claim request form with validation.
6. **Frontend:** Create claim status dashboard for users.
7. **Frontend:** Implement notification display for claim updates.
8. **Integration:** Connect claim system with item status updates.
9. **Security:** Ensure users can only claim items and view their own claims.

## UI Design:

### Claim Request Form:
* Item Reference (Auto-filled from selected item)
* Detailed Description (Text Area - "Describe your lost item in detail")
* Additional Verification Info (Text Area - "Any unique features, purchase location, etc.")
* Contact Preference (Radio buttons: Email, Phone, In-person meeting)
* Submit Claim Button
* Cancel Button

### Claim Status Display:
* List of submitted claims with status indicators
* Claim submission date and time
* Item details and thumbnail
* Current status (Pending, Under Review, Approved, Rejected)
* Contact information for approved claims
* Option to withdraw pending claims

### Notification System:
* Real-time notifications for claim status changes
* Email notifications for important updates
* In-app notification badge and list
* Mark as read functionality

### For Item Finders:
* List of claims received for their posted items
* Claim details with user verification information
* Approve/Reject buttons with reason field
* Contact information reveal upon approval
