# Campus Lost & Found - CP3407 Project 2025

## Project Overview

This project is a web application designed to help students and staff manage lost and found items on the JCU campus efficiently. It serves two primary user groups:

* **Finders:**
    * Easily post details and photos of items they have found.
    * Specify where and how the item is being kept.
* **Seekers:**
    * Quickly browse or filter through listed found items.
    * Get information on how to potentially reclaim their lost belongings.

Our main goals are to build a secure, user-friendly, and reliable system utilizing cloud storage for item images and a robust database for item information.

## Project Goal
* Our goal is to build a simple Lost and Found website for our school. When someone finds a lost item, they bring it to the Lost and Found Center. The staff will take a photo of the item and upload it to the website.This way, students who lose something can easily check the website to see if their item has been found.

## Team Members (Practical B Group 6)

* Sai Ohm Saie Paine
* Linn Thant Soe Wai
* Hlyan Wint Aung

## Project Planning (BEFORE Iteration-1)

### Checklist / TODOs

* ✅ Update the following during each weekly prac session
* ✅ GitHub's entry timestamp is BEFORE the iteration-1
* ✅ Review and confirm all user stories for the Lost & Found system are correct.
* ✅ Add more user stories than can fit in Iterations 1 and 2 to practice prioritization (e.g., user notifications, advanced search, direct messaging between finder/seeker, item expiry/disposal tracking).

## What We Focus On

* **Simple and Clear Interface:** For easy navigation when posting found items or searching for lost ones.
* **Secure User Authentication:** To protect user information for those posting items.
* **Cloud Storage (AWS S3):** For reliable and efficient handling of item images.
* **Effective Item Management:** Tools for users to post items with location, status, and contact information.
* **Filtering Capabilities:** To help users quickly narrow down searches based on item status or location.

## Who Does What

* **Frontend:** Sai Ohm Saie Paine, Hlyan Wint Aung
* **Backend:** Linn Thant Soe Wai

## Tech Stack

* **Frontend:** React
* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL
* **File Storage:** AWS S3 (for item images)
* **Authentication:** JWT-based
* **Deployment:** Docker, AWS Elastic Beanstalk

### Iteration 1 [3-4 Weeks] (Start: DD/MM/YYYY - End: DD/MM/YYYY)
**Goals:** Implement core functionalities for users to post found items, and for anyone to browse, search, and filter these items. This will establish the basic public-facing features of the system.

**User Stories for Iteration 1:**

- **Post a Found Item** | Priority: High / 1 | Estimate: 4 days
  - *Description*: As a registered campus member (student or staff), I want to be able to easily post details of an item I have found on campus, including its name, a description, a picture, where I found it (block and level), and how I am currently keeping the item. This will help others who have lost items to find them. *(Note: This story implies user registration/login might be needed, or it's posted by an 'anonymous' or pre-defined admin if user auth is in Iteration 2)*

- **View and Search Found Items** | Priority: High / 2 | Estimate: 4 days
  - *Description*: As a campus member, I want to be able to view a list of all recently found items and search/filter this list so that I can try to find an item I have lost.

- **Filter Found Items by Status** | Priority: Medium / 4 | Estimate: 2 days
  - *Description*: As a campus member looking for a lost item, I want to be able to filter the list of found items based on how the item is being kept (e.g., "Sent to One Stop Center") so I can more efficiently search in relevant places or for items I can directly inquire about.

**Total estimated effort for Iteration 1:** 10 days (assuming 1 day = 5 production hours)

---