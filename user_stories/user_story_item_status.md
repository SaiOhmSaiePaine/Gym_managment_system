# User story title: Item Status Management

## Priority: Medium / 5

This functionality allows for comprehensive tracking and updating of item statuses throughout their lifecycle in the Lost & Found system.

## Estimation: 2 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 2
* Linn Thant Soe Wai: 2
* Hlyan Wint Aung: 2

## Assumptions:

* Item statuses include: Found, Available, Claimed, Under Review, Returned, Expired.
* Only item owners and admins can update item statuses.
* Status changes trigger notifications to relevant parties.
* Status history is maintained for audit purposes.
* Automatic status updates occur based on time and claim activities.

## Description:

As a user who has posted a found item, I want to be able to update the status of my item as its situation changes (e.g., when someone claims it, when it's returned to the owner, or when I take it to the One Stop Center). The system should also automatically update statuses based on certain triggers and notify relevant users about status changes.

## Tasks:

1. **Backend:** Create API endpoints for status updates with proper validation.
2. **Backend:** Implement automatic status change triggers (time-based, claim-based).
3. **Backend:** Create status history tracking for audit purposes.
4. **Backend:** Implement notification system for status changes.
5. **Frontend:** Design status update interface for item owners.
6. **Frontend:** Create status indicator components and badges.
7. **Frontend:** Implement status change confirmation dialogs.
8. **Integration:** Connect status changes with notification system.

## UI Design:

### Status Update Interface:
* Current status display with color-coded badge
* Status change dropdown with available options
* Reason field for status changes (optional/required)
* Update Status button
* Confirmation dialog with impact explanation

### Status Indicators:
* Color-coded status badges throughout the application
* Status timeline showing progression
* Last updated timestamp
* Status change history expandable section

### Available Status Options:
* **Found** - Item recently found and posted
* **Available** - Item available for claiming
* **Claimed** - Claim request received, under review
* **Under Review** - Multiple claims being evaluated
* **Returned** - Item successfully returned to owner
* **Sent to One Stop** - Item transferred to campus lost & found office
* **Expired** - Item posting expired (auto-set after time period)

### Notification Integration:
* Real-time notifications for status changes
* Email notifications for important status updates
* In-app notification badges and alerts
* Notification preferences in user settings

### Admin Status Management:
* Bulk status update tools
* Override capabilities for any item status
* Mass expiration tools for old items
* Status change audit logs and reporting
