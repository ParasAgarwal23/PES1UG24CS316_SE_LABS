# PES1UG24CS316 - Software Engineering Labs

**Course:** Software Engineering  
**Name:** Paras Agarwal  
**SRN:** PES1UG24CS316  
**Section:** F

This repository holds my Software Engineering lab work. Each lab has its own
folder with a README that describes the assignment, the deliverables and the
results.

## Labs

| Lab | Topic | Folder |
|---|---|---|
| Lab 1 | Requirements Engineering & UML Use-Case Modelling | [`Lab-1_Requirements-Engineering/`](Lab-1_Requirements-Engineering/) |
| Lab 2 | Jira Hands-on: Agile Backlog Creation & Sprint Simulations | [`Lab-2_Jira-Agile-Backlog/`](Lab-2_Jira-Agile-Backlog/) |
| Lab 3 | Component Modelling & Architectural Pattern Selection | [`Lab-3_Component-Modelling/`](Lab-3_Component-Modelling/) |
| Lab 4 | Vibe Coding: Maze Chase | [`Lab-4_Vibe-Coding-Maze-Chase/`](Lab-4_Vibe-Coding-Maze-Chase/) |
| Lab 5 | Static Code Analysis | [`Lab-5_Static_Code_Analysis/`](Lab-5_Static_Code_Analysis/) |
| Lab 6 | Code and Branch Coverage Analysis | [`Lab-6_Code_and_Branch_Coverage/PES1UG24CS316_Lab6_amusement_park_ride_access/`](Lab-6_Code_and_Branch_Coverage/PES1UG24CS316_Lab6_amusement_park_ride_access/) |
| Lab 7 | Fuzzing for Input Validation Bugs | [`Lab-7_Fuzzing_for_Input_Validation_Bugs/`](Lab-7_Fuzzing_for_Input_Validation_Bugs/) |

## Lab 1 — Requirements Engineering & UML Use-Case Modelling

Requirements engineering for the Telemedicine Slot Booking & Prescription
Portal (Problem Statement 11). The deliverables are a requirements table with
five functional and two non-functional requirements, a UML use-case diagram,
and a use-case flow specification for *Book Video Consultation Slot*.

Folder: [`Lab-1_Requirements-Engineering/`](Lab-1_Requirements-Engineering/)

## Lab 2 — Jira Hands-on: Agile Backlog Creation & Sprint Simulations

Agile project management in Jira for the telemedicine portal. The work covers
epics and user stories, story-point estimation, sprint planning, an active
sprint and a burndown chart, documented with screenshots and a submission PDF.

Folder: [`Lab-2_Jira-Agile-Backlog/`](Lab-2_Jira-Agile-Backlog/)

## Lab 3 — Component Modelling & Architectural Pattern Selection

Architecture selection for the telemedicine portal. A Layered Architecture
was chosen and modelled as a UML component diagram with provided and required
interfaces, and a written document justifies the choice.

Folder: [`Lab-3_Component-Modelling/`](Lab-3_Component-Modelling/)

## Lab 4 — Vibe Coding: Maze Chase

LLM-assisted (Claude) development on a Python Maze Chase game. Four features
were added incrementally: multiple enemies, enemy speed progression, a
power-pellet freeze and a survival score. The folder also has before and after
gameplay videos and the chat history.

Folder: [`Lab-4_Vibe-Coding-Maze-Chase/`](Lab-4_Vibe-Coding-Maze-Chase/)

## Lab 5 — Static Code Analysis

A Python static-analysis exercise using **Pylint**, **Bandit** and
**Flake8** on the Student Scholarship Eligibility Screener
(`scholarship_system.py`). The purpose is to find and fix security, correctness
and style problems with these tools, then check the fixes by running the tools
again.

The folder contains:

- baseline reports for the original code;
- an issue table;
- fixes made in three commits (security, code quality, style);
- functional tests;
- before and after reports.

Pylint improved from 4.69/10 to 10.00/10, and Bandit and Flake8 findings went
from 2 and 12 to none.

Folder: [`Lab-5_Static_Code_Analysis/`](Lab-5_Static_Code_Analysis/)

## Lab 6 — Code and Branch Coverage Analysis

Test-coverage analysis of the Amusement Park Ride Access module
(`amusement_park_ride_access.py`), which handles ride admission, ticket
pricing, height and health-warning checks, fast-lane fees and
safety-restraint sensor monitoring. The work uses **pytest** and
**Coverage.py** to measure the **line coverage** and **branch coverage** of
the starter test, and then adds two test suites, one written for line coverage
and one for branch coverage.

Line coverage went from 48.28% (28/58 statements) with the starter test to
100% (58/58) with the code coverage suite, and branch coverage went from
40.00% (16/40 branches) to 100% (40/40) with the branch coverage suite.

Folder: [`Lab-6_Code_and_Branch_Coverage/PES1UG24CS316_Lab6_amusement_park_ride_access/`](Lab-6_Code_and_Branch_Coverage/PES1UG24CS316_Lab6_amusement_park_ride_access/)

## Lab 7 — Fuzzing for Input Validation Bugs

Fuzz testing of the Amusement Park Ride Access processor (`processor.py`) from
the `Lab 7` folder of the assigned repository
[SETAPESU26/L6_L7_11_amusement_park_ride_access](https://github.com/SETAPESU26/L6_L7_11_amusement_park_ride_access).
The script validates rider height and FastPass specs, computes dispatch
throughput and resolves safety-restraint codes. **Hypothesis** property-based
tests run with **pytest** found six input-validation bugs, including crashes
on `None`, empty or unknown values, a division by zero, and an accepted 0 cm
height and negative throughput. All of these were fixed in the script.

The Hypothesis suite went from 6 failed and 3 passed on the original script to
9 passed on the fixed script.

The folder contains:

- `processor.py`, the fixed application;
- `test_processor.py`, the Hypothesis fuzz tests;
- `Lab7_Fuzzing_Report.pdf`, the lab report;
- `screenshots/`, four terminal screenshots of the original run, the failing
  tests, the fixed run and the passing tests.

Folder: [`Lab-7_Fuzzing_for_Input_Validation_Bugs/`](Lab-7_Fuzzing_for_Input_Validation_Bugs/)
