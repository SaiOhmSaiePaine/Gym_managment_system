# User story title: Upload Item Image to AWS S3

## Priority: Medium / 4

Image uploads improve item recognition and reporting accuracy.

## Estimation: 2 days (1 day = 5 production hours)

* Sai Ohm Saie Paine: 2
* Linn Thant Soe Wai: 1
* Hlyan Wint Aung: 1

## Assumptions:

* Users can upload an image when reporting a lost or found item.
* Images are uploaded directly to AWS S3 with a unique filename.
* Upload progress is shown in the UI, and fallback/local backup is possible.

## Description:

As a user, I want to upload an image of my lost or found item so that others can more easily recognize it in the listings.

## Tasks:

1. **Backend:** Set up AWS S3 integration using boto3 with secure credentials.
2. **Frontend:** Create a UI component for file selection and preview.
3. **Frontend:** Display upload progress bar and handle upload success/failure.

## UI Design:

* Upload button or dropzone in the item submission form.
* File preview shown after selection.
* Progress bar during upload.
* Error message if upload fails.
* Optional thumbnail shown in item list.

