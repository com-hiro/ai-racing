# ai-racing (Formula AI Ultimate)

A high-speed autonomous racing simulation that integrates **Computer Vision (CV)** and **Reinforcement Learning (Q-Learning)**. The agent learns to navigate a complex race track by processing real-time visual data and optimizing its steering and acceleration through a trial-and-error reward system.

## 🏎️ Overview
Traditional racing games rely on hard-coded paths. This project implements a truly autonomous agent that perceives its environment through a simulated camera feed and improves its driving performance over time. By combining physics-based simulation with a Q-Learning brain, the agent achieves a realistic "0 to 400 km/h" racing experience.

## 🚀 Key Features
- **Visual Perception (CV-Based):** The agent does not "know" the track coordinates. Instead, it captures a 200x200 pixel visual field and uses OpenCV-based color masking (HSV) to detect the track's center line.
- **Autonomous Q-Learning:** Implements a reinforced decision-making process. The agent maps visual errors to optimal steering angles and acceleration values, storing its "experience" in a persistent Q-table.
- **Dynamic Physics Engine:** Simulates realistic vehicle dynamics including friction, momentum, and steering-speed correlation.
- **Persistent Memory:** The AI's learned intelligence is saved to a JSON file (`formula_ai_ultimate_best.json`), allowing it to retain and build upon its knowledge across different sessions.

## 🛡️ Technical Logic: Overcoming Racing Challenges
This agent solves the problem of autonomous navigation through two core technological pillars.

### 1. Image-Based Navigation (Computer Vision)
- **The Problem:** How does an AI know where to steer without pre-defined path coordinates?
- **The Solution:** We implement a **Real-Time Visual Processing Unit**. The agent analyzes the `m10` and `m00` moments of a yellow color mask to calculate its horizontal deviation (error) from the track center. This mimics human visual feedback.

### 2. Reward-Driven Optimization (Reinforcement Learning)
- **The Problem:** How can the AI learn to drive fast without flying off the track?
- **The Solution:** A specialized **Reward Shaping** function:
  - **Positive Reward:** Proportional to speed and alignment with the center line: `(100 - abs(error)) + (speed * 3.0)`.
  - **Negative Reward (Penalty):** A massive penalty is applied for crashing or leaving the track boundaries, forcing the agent to prioritize stability during early learning stages.

## 🛠️ Technology Stack
| Technology | Role |
| :--- | :--- |
| **Python 3.x** | Primary Development Language |
| **Pygame** | 2D Rendering Engine & Physics Simulation |
| **OpenCV (cv2)** | Image Processing & Feature Extraction |
| **NumPy** | High-speed Matrix Operations for Q-table & Images |
| **Q-Learning** | Reinforcement Learning Algorithm |

## ⚙️ Setup and Usage

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install pygame opencv-python numpy
```

## 📜 Licensing and Copyright

### Copyright Notice
Copyright (c) 2025 Akira Hirohashi. All rights reserved.

### License
The source code for this project is released under the **MIT License**. 
Please refer to the [LICENSE](./LICENSE.txt) file for the full terms and conditions. 

---
🛡️ **Disclaimer**: This software is provided "AS IS," without warranty of any kind. Use the program at your own risk.
