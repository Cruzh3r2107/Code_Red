# Light Swarm Logger and Controller System  

This repository implements a distributed logging and control system for managing a swarm of devices using **Python** and **Raspberry Pi GPIO**. The project uses UDP for communication and offers real-time data visualization and control capabilities.  

---

## 📜 Features  

- **Real-Time Communication**:  
  - Sends and receives UDP packets to control and log swarm activity.  
  - Supports packet types like `RESET_SWARM_PACKET`, `DEFINE_SERVER_LOGGER_PACKET`, and more.  

- **Swarm Control**:  
  - Commands to reset swarm, blink LEDs, and manage tests dynamically.  
  - Data visualization using LED matrices and seven-segment displays.  

- **Data Logging**:  
  - Logs data to files with timestamps for every event.  
  - Supports graphing and average value calculations over time slices.  

- **Hardware Integration**:  
  - Interfaces with GPIO for LED matrices and button inputs.  
  - Supports visual feedback with toggling LEDs and digit displays.  

---

## 🚀 Getting Started  

### Prerequisites  
- Raspberry Pi (configured with GPIO access).  
- Python 3.x with required libraries:  
  ```bash
  pip install matplotlib netifaces RPi.GPIO
