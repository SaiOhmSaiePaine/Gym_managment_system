# Iteration 1 Retrospective – Project Plan

**Project Title**: Lost and Found Campus System  
**Iteration**: 1 (Week 3 – Week 6)  
**Date Range**: 10 June 2025 – 1 July 2025  
**Team Members**: Min Khant, Khun Pyae Heinn, Naing Phone Pyae, Nang Kaung Shan Kham  
**Velocity Assumption**: 7 days per developer  
**Total Estimate**: 10 task-days  
**Actual Velocity**: 10 task-days

---

## What Went Well

- **On-time Delivery**: All user stories were completed within the estimated time.
- **Strong Task Division**: Tasks were clearly divided by frontend/backend responsibilities.
- **Effective Git Usage**: Team consistently committed code and tracked changes using GitHub.
- **Cloud Integration**: Successful AWS S3 integration for image uploads during this sprint.
- **UI/UX Design**: Smooth implementation of posting, viewing, and filtering UI with responsive layout.
- **Collaboration**: Weekly progress check-ins helped align the team and resolve blockers early.

---

## What Could Be Improved

- **API Modularity**: Some backend endpoints could have been better modularized for future scalability.
- **Testing Coverage**: While functional testing was done, more structured test cases could improve reliability.
- **Task Estimates**: Some tasks (e.g., S3 upload handling) were slightly underestimated in complexity.
- **Frontend-Backend Sync**: Minor delays occurred when API changes weren’t promptly reflected in frontend.

---

## Lessons Learned

- Importance of aligning frontend and backend through shared API documentation.
- Building reusable components early reduces repetitive code in later stages.
- AWS S3 integration requires careful handling of file types and size restrictions.
- Burn-down chart tracking helps visualize actual progress and velocity.

---

## Action Plan for Iteration 2

- Implement **JWT authentication** early to enable secure user flows from the start.
- Refactor backend for **clearer module separation** and documentation.
- Adopt a **test plan** checklist for every feature delivered.
- Use **mock data** during early UI development to decouple from backend dependencies.
- Improve **code review process** with structured pull requests and checklists.

---

## Completed User Stories

1. ✅ **Post a Found Item** – 4 days  
   *UI Form, API, S3 Upload*

2. ✅ **View and Search Found Items** – 4 days  
   *Listing UI, Search API, Integration*

3. ✅ **Filter Found Items by Status** – 2 days  
   *Dropdown UI, Query Filter*

---

## Burn-down Summary

| Week     | Estimated Work Left |
|----------|---------------------|
| Week 1   | 10 days             |
| Week 2   | 6 days              |
| Week 3   | 4 days              |
| Week 4   | 2 days              |
| Final    | 0 days ✅            |

---

*Prepared by: CP3407 Group – Practical B*  
*Retrospective Date: 1 July 2025*
