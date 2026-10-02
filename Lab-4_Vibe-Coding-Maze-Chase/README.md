# Lab 4 – Vibe Coding: Maze Chase

**Course:** Software Engineering  
**Lab:** Lab 4 – Vibe Coding  
**SRN:** PES1UG24CS316  
**Name:** PARAS AGARWAL  

## Objective

To use an **LLM-assisted Vibe Coding workflow** to understand, modify, test, and extend an existing Maze Chase game by implementing the assigned gameplay features and documenting the development process.

## Project Overview

The starter project is a Maze Chase game developed in Python.

For this lab, **Claude was used as the Vibe Coding assistant** to review the existing codebase and assist in implementing the required modifications.

The following four gameplay features were implemented:

1. Multiple enemies
2. Progressive enemy speed
3. Power pellet freeze
4. Survival score

Each feature was implemented and tested incrementally.

## Features Implemented

### Task 1 – Multiple Enemies

The game was extended to support multiple enemies instead of a single enemy.

This increases the difficulty of the game by requiring the player to avoid several enemies moving through the maze.

### Task 2 – Enemy Speed Progression

Enemy speed increases as the player survives longer.

- Enemy speed increases every **15 seconds**
- The current speed progression is reflected during gameplay
- The game therefore becomes progressively more difficult over time

### Task 3 – Power Pellet Freeze

A power pellet mechanic was added to temporarily freeze enemies.

When the player activates the power pellet:

- Enemies enter a frozen state
- Frozen enemies temporarily stop moving
- The freeze effect lasts for approximately **5 seconds**
- A visual indication is provided while enemies are frozen

### Task 4 – Survival Score

A survival-based scoring system was added.

The game tracks the player's survival progress and displays the score during gameplay. The final score is also displayed when the game ends.

## Code Modified

The primary source files modified during the lab were:

### `game/game_engine.py`

Contains the main gameplay changes required to integrate the four tasks, including:

- Multiple-enemy handling
- Enemy speed progression
- Power pellet and freeze timing
- Survival score tracking
- Gameplay/HUD updates

### `game/entities.py`

Modified to support enemy freeze behaviour, including:

- Enemy frozen state
- Preventing enemy movement while frozen
- Visual representation of the frozen state

## Vibe Coding with Claude

**Claude was used as the LLM assistant for the Vibe Coding process in this lab.**

The development workflow consisted of:

1. Reviewing the existing Maze Chase codebase
2. Providing the relevant source code and task requirements to Claude
3. Using Claude to understand the existing implementation and generate suggested code modifications
4. Applying the suggested changes to the project
5. Running and testing the game locally
6. Refining the implementation where required
7. Committing the completed features incrementally using Git

This approach allowed each required feature to be implemented and tested separately while maintaining a clear development history.

### Claude Chat

The Claude conversation used during the Vibe Coding process can be viewed here:

**[View Claude Vibe Coding Chat](https://claude.ai/share/debc628c-9301-491f-9c93-5f42ba15689e)**

The exported conversation is also included in the repository as:

`Chat_History_Claude.pdf`

## Deliverables

The Lab 4 submission includes:

- Updated Maze Chase source code
- Before-modification gameplay video
- After-modification gameplay video
- Claude Vibe Coding chat history PDF
- Claude conversation link
- README documentation

### Submission Files

```text
Lab-4_Vibe-Coding-Maze-Chase/
├── game/
├── main.py
├── requirements.txt
├── README.md
├── PES1UG24CS316_before_video.mp4
├── PES1UG24CS316_after_video.mp4
├── Chat_History_Claude.pdf
└── Chat_Link_Claude.md
```

## Implementation History

The project was developed incrementally, with separate Git commits for the major tasks:

- Task 1 – Multiple enemies
- Task 2 – Enemy speed progression
- Task 3 – Power pellet freeze
- Task 4 – Survival score
- Final submission deliverables

## Tools / Concepts Used

- Python
- Git and GitHub
- Vibe Coding
- LLM-Assisted Development
- Claude
- Incremental Development
- Game Logic Modification
- Testing and Debugging
