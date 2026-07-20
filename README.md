# Whitworth Quick Return Mechanism Simulator

An interactive **Python-based desktop application** for simulating the **Whitworth Quick Return Mechanism** with real-time animation, comprehensive kinematic analysis, and dynamic force analysis. The simulator provides an intuitive graphical interface that allows users to visualize mechanism motion, study engineering concepts, and analyze the behavior of the mechanism under different input parameters. :contentReference[oaicite:0]{index=0}

---

## Features

- 🎥 Real-time animation of the Whitworth Quick Return Mechanism
- ⚙️ Adjustable mechanism parameters
- ▶️ Start, Pause, and Reset simulation controls
- 🎚️ Adjustable animation speed
- 🔍 Interactive zooming and panning
- 📍 Position, Velocity, and Acceleration analysis
- 📈 Dynamic torque analysis using the **Virtual Power Method**
- 📊 Numerical kinematic analysis at different mechanism positions
- 🖥️ Fullscreen visualization for analysis diagrams
- 🎨 Clean and interactive Tkinter-based GUI

---

## Technologies Used

- **Python**
- **Tkinter**
- **NumPy**
- **Matplotlib**

---

## Engineering Concepts Implemented

- Whitworth Quick Return Mechanism
- Mechanism Synthesis
- Position Analysis
- Velocity Analysis
- Acceleration Analysis
- Relative Velocity Method
- Relative Acceleration Method
- Coriolis Acceleration
- Virtual Power Method
- Rigid Body Dynamics
- Vector Loop Equations

---

## Installation

Clone the repository

```bash
git clone https://github.com/your-username/Whitworth-Quick-Return-Mechanism-Simulator.git
```

Navigate to the project directory

```bash
cd Whitworth-Quick-Return-Mechanism-Simulator
```

Install the required dependencies

```bash
pip install numpy matplotlib
```

Run the simulator

```bash
python simulator.py
```

---

## How to Use

1. Enter the required mechanism dimensions.
2. Click **Update Parameters**.
3. Start the animation.
4. Adjust the animation speed if required.
5. Use the **Kinematic Analysis** window to visualize:
   - Position Diagram
   - Velocity Polygon
   - Acceleration Polygon
6. Open the **Dynamic Analysis** window to observe the required input torque throughout one complete crank revolution.
7. Use mouse controls to zoom and pan while observing the mechanism.

---

## Kinematic Analysis

The simulator performs complete kinematic analysis of the mechanism, including:

- Position analysis
- Velocity analysis
- Acceleration analysis
- Angular velocity computation
- Angular acceleration computation
- Slider velocity and acceleration
- Coriolis acceleration
- Slip velocity
- Loop closure validation

---

## Dynamic Analysis

The dynamic analysis module evaluates the mechanism using the **Virtual Power Method**.

It considers:

- Link masses
- Link moments of inertia
- Slider masses
- Gravity
- Rotating object's inertia
- Required driving torque throughout one complete cycle

The simulator generates a graph of **Required Input Torque vs Crank Angle**, highlighting the maximum torque required during operation.

---


## Future Improvements

- Export analysis results to CSV
- Save plots as images
- Support multiple quick-return mechanisms
- 3D visualization
- CAD model integration
- Stress and force analysis
- Improved simulation performance

---

## Learning Outcomes

This project strengthened my understanding of:

- Object-Oriented Programming in Python
- GUI development using Tkinter
- Scientific computing with NumPy
- Data visualization using Matplotlib
- Mechanism synthesis and kinematic analysis
- Dynamic force analysis of mechanical systems
- Engineering simulation development

---

## License

This project is intended for educational and learning purposes.

---

## Author

**Mahika**

B.Tech Mechanical Engineering  
Indian Institute of Technology Hyderabad
