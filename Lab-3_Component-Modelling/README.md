# Lab 3 – Component Modelling & Architectural Pattern Selection

**Course:** Software Engineering  
**Lab:** Lab 3 – Component Modelling & Architectural Pattern Selection  
**SRN:** PES1UG24CS316  
**NAME:** PARAS AGARWAL
**Problem Statement:** 11 – Telemedicine Slot Booking & Prescription Portal

## Objective

To evaluate suitable architectural styles for the assigned system, select an appropriate architecture, and model the system using a UML Component Diagram showing its major components, interfaces, and dependencies.

## Selected Architecture

**Layered Architecture**

The Telemedicine Slot Booking & Prescription Portal is organized into separate layers to provide clear separation of concerns:

- **Presentation Layer** – Handles interactions with patients and physicians.
- **Business Layer** – Handles booking, scheduling, video consultations, and prescription management.
- **Data Layer** – Handles persistent storage of booking, prescription, and related system data.
- **External System** – Provides notification services.

## Components

The component model consists of:

- Patient & Physician Portal UI
- Booking & Scheduling Manager
- Video Consultation Manager
- Prescription Manager
- Database
- Notification Service

## Interfaces

The component diagram models the interactions between components using provided and required interfaces, including:

- `IBookingService`
- `IVideoSession`
- `IPrescriptionService`
- `IRoomLinkGeneration`
- `IBookingData`
- `IPrescriptionData`
- `INotify`

## Architectural Justification

Layered Architecture was selected because the system naturally separates into user-interface, business-logic, and data-storage responsibilities.

This structure provides clear separation of concerns and keeps the application simpler to implement, test, and maintain than a distributed microservices architecture for this scenario.

The architecture also provides clear boundaries for applying security controls to sensitive healthcare and booking data while avoiding unnecessary distributed service-to-service communication overhead.

## Deliverables

- `PES1UG24CS316_Telemedicine_Component_Diagram.pdf` – UML Component Diagram
- `PES1UG24CS316_Written_Justification.pdf` – Architectural selection and justification

## Tools / Concepts Used

- UML Component Modelling
- Layered Architecture
- Provided and Required Interfaces
- Component Dependencies
- Architectural Pattern Analysis