Doctor Appointment Booking API

A RESTful API for facilitating online doctor appointment bookings. This backend-only solution allows patients to book appointments, doctors to manage their schedules, and includes payment integration, cancellation policies, waitlist notifications, and more.
Table of Contents

    Overview
    Features
    Technology Stack
    Project Architecture
    Installation & Setup
    API Endpoints
    Testing
    Contributing
    License

## Overview

The Doctor Appointment Booking API is designed to streamline the process of scheduling appointments between patients and doctors. The system supports:

Doctor Registration: A portal for doctors to register and provide details such as specialty and experience.
Appointment Booking: Patients can book appointments with doctors based on availability, subject to a 15-day window.
Payment Processing: Integrated payment functionality for confirming appointments.
Cancellation & Rescheduling: Patients can cancel (if more than 3 days remain) or reschedule their appointments. Doctors can also cancel or reschedule appointments and notify affected patients.
Waitlist Notifications: If a doctor’s appointment slots are full, patients can be placed on a waitlist and will be notified if a slot becomes available.
Appointment Limit: Each doctor is limited to 30 appointments.

## Features

## Doctor Registration Portal
    Doctors register and provide details including specialty, experience, and contact information.

## Patient Appointment Booking
    Patients book appointments within a 15-day window.
    The system ensures that each doctor can only accept up to 30 appointments.

## Payment Integration
    Payment processing is integrated using a payment gateway (e.g., PayPal).

## Cancellation & Rescheduling
    Patients can cancel appointments if there are more than 3 days remaining before the scheduled time.
    Doctors can cancel or reschedule appointments and notify patients accordingly.

## Waitlist & Notifications
    If a booking is not possible due to slot limitations, patients can join a waitlist.
    In case of cancellation, waitlisted patients are notified about available appointment slots.

## Technology Stack

    Backend: Python, Django, Django REST Framework
    Database: PostgreSQL
    Asynchronous Tasks: Celery with Redis
    Payment Integration: PayPal SDK
    Version Control: Git (hosted on GitHub)

## Project Architecture

## Modular Code Structure:
The project is divided into modular Django apps (e.g., accounts, appointments, payments) to enhance maintainability and testability.

## Custom User & Role-Based Profiles:
A custom user model (CustomUser) differentiates between doctors and patients, with role-specific data stored in dedicated profile models.

## RESTful API Endpoints:
All functionalities are exposed as REST API endpoints, which can be consumed by any client (e.g., Postman, mobile apps).

## Asynchronous Processing:
Celery and Redis are used for background tasks like sending email notifications.

## Secure and Testable:
The code is designed to be safe, portable, and easily testable across environments.

## Installation & Setup
## Prerequisites

    Python 3.10+
    Redis (for Celery)
    A relational database (SQLite is used by default; configure PostgreSQL if needed)
    Git

## Backend Setup

## Clone the Repository:

    git clone https://github.com/Towet-Tum/Doctor-Visit-App.git

## Create a Virtual Environment and Install Dependencies:

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt

## Configure Environment Variables:

Create a .env file (or configure environment variables) with values such as:

    DJANGO_SECRET_KEY=your-secret-key
    DEBUG=True
    DATABASE_URL=sqlite:///db.sqlite3  # Or your MySQL configuration
    PAYPAL_CLIENT_ID=your-paypal-client-id
    PAYPAL_CLIENT_SECRET=your-paypal-client-secret
    PAYPAL_MODE=sandbox  # Change to "live" in production
    REDIS_URL=redis://localhost:6379/0
    EMAIL_HOST=smtp.your-email-provider.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your-email@example.com
    EMAIL_HOST_PASSWORD=your-email-password
    DEFAULT_FROM_EMAIL=your-email@example.com

## Apply Migrations:

    python manage.py makemigrations
    python manage.py migrate

## Create a Superuser:

    python manage.py createsuperuser

## Run the Development Server:

    python manage.py runserver

## Start Celery Worker (in a separate terminal):

    celery -A your_project_name worker --loglevel=info

## API Endpoints

All endpoints are prefixed by /api/. Below is a summary of the main endpoints:
Accounts

    Register a User:
    POST /api/accounts/register/
    Payload Example:

    {
      "username": "johndoe",
      "email": "johndoe@example.com",
      "password": "securepassword123",
      "role": "doctor"
    }

    Get/Update Current User Details:
    GET/PUT /api/accounts/me/

Appointments

    List/Create Appointments:
    GET/POST /api/appointments/appointments/
    Create Payload Example:

{
  "doctor": 1,
  "patient": 2,
  "appointment_date": "2025-03-10T10:00:00Z"
}

    Cancel Appointment (Patient):
    POST /api/appointments/appointments/<appointment_id>/cancel/

    Reschedule Appointment (Patient):
    POST /api/appointments/appointments/<appointment_id>/reschedule/
    Payload Example:

    {
    "appointment_date": "2025-03-15T14:00:00Z"
    }

    Doctor Cancel Appointment:
    POST /api/appointments/appointments/<appointment_id>/doctor_cancel/

    Doctor Reschedule Appointment:
    POST /api/appointments/appointments/<appointment_id>/doctor_reschedule/

    Doctor Bulk Cancel:
    POST /api/appointments/appointments/doctor_bulk_cancel/
    Optional Payload Example:

        {
        "patient_id": 3,
        "cancel_date": "2025-03-10"
        }

        Waitlist Entry (if applicable):
        POST /api/appointments/waitlist/

Payments

    Create a Payment:
    POST /api/payments/create/
    Payload Example:

{
  "appointment_id": 2,
  "amount": "100.00",
  "currency": "USD"
}

    Execute a Payment:
    POST /api/payments/execute/
    Payload Example:

        {
        "paymentId": "PAYID-XXXXXXXXXX",
        "PayerID": "XXXXXXXXXX"
        }

    Note: Always include a trailing slash at the end of the URL (e.g., /api/appointments/appointments/).
Testing

    Unit Testing:
    Run tests using:

    python manage.py test

    API Testing:
    Use Postman or curl to test each endpoint. Ensure you include the necessary authentication headers JWT tokens when required.

    Continuous Integration:
    The repository includes configuration for automated testing (e.g., GitHub Actions) to maintain code stability.

Contributing

Contributions are welcome! Follow these steps to contribute:

    Fork the repository.
    Create a feature branch (git checkout -b feature/your-feature).
    Commit your changes (git commit -m 'Add new feature').
    Push to the branch (git push origin feature/your-feature).
    Open a pull request.

Please ensure that your code is modular, well-tested, and adheres to our coding guidelines.
License

This project is licensed under the MIT License. See the LICENSE file for more details.
Workflow & Execution

    Code Organization:
    The project is structured into modular Django apps (accounts, appointments, payments, etc.) to ensure maintainability and portability.

    Version Control:
    The project is maintained on GitHub as a public repository.

    Development Process:
        Set up your environment and install dependencies.
        Develop features following the modular approach.
        Write tests to ensure code safety and functionality.
        Use CI/CD pipelines for automated testing and deployment.

    Execution:
        Run the Django development server.
        Start Celery for asynchronous tasks.
        Use API testing tools to interact with the API endpoints.
