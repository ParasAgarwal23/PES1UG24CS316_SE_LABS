# Lab 1 — Requirements Engineering & UML Use-Case Modelling

**SRN:** PES1UG24CS316

**NAME:** Paras Aagrwal

**Problem Statement #11 — Healthcare & Telemedicine**

**System:** Telemedicine Slot Booking & Prescription Portal

## Overview
A secure healthcare consultation portal allowing remote patients to view doctor specialties,
book video consultation slots, receive encrypted tele-consultation room links, and download
digitally signed prescriptions.

**Actors:** Patient, Attending Physician, Notification Service

## Contents

| Deliverable | File |
|---|---|
| Requirements Table (5 FR + 2 NFR) | `Requirements/Requirements_Table.xlsx` |
| UML Use-Case Diagram (editable) | `UML/Telemedicine_Use_Case_Diagram.drawio` |
| UML Use-Case Diagram (export) | `UML/Telemedicine_Use_Case_Diagram.pdf` |
| Use-Case Flow Specification | `Use-Case-Flow/Book_Consultation_Flow.docx` and `.pdf` |

## Diagram summary
- 6 use cases (UC-01 to UC-06) covering slot browsing, booking, room-link generation,
  conducting the video consultation itself, prescription authoring/signing, and prescription
  history.
- **«include»**: *Book Video Consultation Slot* always includes *Generate Encrypted Room Link*.
- **«extend»**: *Author & Digitally Sign Prescription* optionally extends *Conduct Video
  Consultation* — a physician may issue a prescription during or after a call, but not every
  consultation ends in one.

## Use-Case Flow
The flow specification details **Book Video Consultation Slot**, including preconditions,
postconditions, the main success scenario, and one alternate flow (slot no longer available).
