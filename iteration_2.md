# Iteration-2 board

**Start Date:** 02/07/2025  
**End Date:** 23/07/2025  

---

### Checklist:
1. GitHub entry timestamps: ✔️ Confirmed  
2. User stories are correct: ✔️ Reviewed and prioritized  

---

- **Assumed Velocity:** 7 days per developer (70% of 10 working days)  
- **Number of developers:** 3  
- **Total estimated amount of work:** 10 task-days  

---

### User Stories and Tasks:

1. **[User Authentication (JWT-based)](./user_stories/user_story_user_authentication.md)** *Priority:* High (1), *Estimate:* 3 days  
2. **[Admin Login and Dashboard](./user_stories/user_story_admin_login_dashboard.md)** *Priority:* High (2), *Estimate:* 2 days
3. **[Connect and Store Data on DigitalOcean PostgreSQL](./user_stories/user_story_digitalocean_storage.md)** *Priority:* High (3), *Estimate:* 3 days 
4. **[Mark Item as Returned](./user_stories/user_story_mark_item_returned.md)** *Priority:* Medium (4), *Estimate:* 2 days  
5. **[Upload Item Image to AWS S3](./user_stories/user_story_aws_s3_upload.md)** *Priority:* Medium (5), *Estimate:* 2 days  

---

### In Progress:

---

### Completed:

1. **[User Authentication (JWT-based)](./user_stories/user_story_user_authentication.md)**  
   *Priority:* High (1), *Estimate:* 3 days  
   **Tasks:**
   - Task 1.1 – Design and implement user registration & login form
   - Task 1.2 – Set up backend JWT authentication and secure endpoints
   - Task 1.3 – Store and validate tokens on frontend with session state

2. **[Admin Login and Dashboard](./user_stories/user_story_admin_login_dashboard.md)**  
   *Priority:* High (2), *Estimate:* 2 days  
   **Tasks:**
   - Task 2.1 – Create secure admin login page with Material-UI
   - Task 2.2 – Build admin dashboard layout with real-time statistics
   - Task 2.3 – Integrate dashboard API and authenticate with admin role
  
3. **[Connect and Store Data on DigitalOcean PostgreSQL](./user_stories/user_story_digitalocean_storage.md)**  
   *Priority:* High (3), *Estimate:* 3 days  
   **Tasks:**
   - Task 3.1 – Provision managed PostgreSQL instance on DigitalOcean
   - Task 3.2 – Configure backend to connect using secured credentials
   - Task 3.3 – Migrate existing schema and test database operations

4. **[Mark Item as Returned](./user_stories/user_story_mark_item_returned.md)**  
   *Priority:* Medium (4), *Estimate:* 2 days  
   **Tasks:**
   - Task 4.1 – Add “Mark as Returned” button to admin item view
   - Task 4.2 – Update item status in database on click
   - Task 4.3 – Hide returned items from public user list

5. **[Upload Item Image to AWS S3](./user_stories/user_story_aws_s3_upload.md)**  
   *Priority:* Medium (5), *Estimate:* 2 days  
   **Tasks:**
   - Task 5.1 – Configure AWS S3 bucket and credentials
   - Task 5.2 – Implement frontend image picker and progress bar
   - Task 5.3 – Connect frontend to backend S3 upload API
  
---

### Burn Down for iteration-2:
- 3 weeks left: 10 days of estimated work remaining  
- 2 weeks left: 6 days of estimated work remaining  
- 1 week left: 3 days of estimated work remaining  
- 0 weeks left: 0 days of estimated work remaining  
- **Actual Velocity:** 10

