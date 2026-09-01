# UBIQUITOUS-ENGINE

**UBIQUITOUS-ENGINE** is a lightweight, modern system monitoring and GPU crash-guard utility designed for Linux environments. It provides real-time telemetry (CPU usage, memory usage, and GPU temperature), system log auditing, automated kernel-level crash detection, and background notification alerts.

---

## Features

* **Modern Dark-Mode GUI:** Built with Python's Tkinter
* **Real-Time Telemetry:** Live tracking of system GPU load, Memory utilization, and GPU thermal sensors (If your GPU comes with thermal sensors.
* **GPU Crash Guard:** Automatically diagnoses kernel ring buffer logs (`dmesg`) for critical GPU lockups, hangs, and page faults.
* **Background Notification Daemon:** Runs a non-blocking background thread that triggers native Linux desktop notifications (`notify-send`) instantly if a GPU error occurs.
* **Multi-Platform Privilege Elevation:** Automatically handles administrative privileges (`pkexec` on Linux when launched

---

## Requirements

* **Python:** 3.8 or higher is recommended
* **Operating System:** Optimized for Linux (Ubuntu/Debian has already been tested)
* **Python Packages:** 
  * `psutil` (for system metrics)
  * `tkinter` (for the graphical interface)

---

## Installation & Running


Python
1. Clone or download the repository to your local machine
2. Use `cd` to go to the directory
3. Run `python main.py` (Or python3 main.py if you're on Linux) to open the code
4. (Optional) Type `y` to automatically download required packages for the application to work


Linux (Ubuntu/Debian)
1. Download the .deb file from releases
2. On Files, right click the file and press "Open with", open the .deb file with App Center
3. Press Install and wait
4. Now go to your apps and you should see the app
5. Authenticate with your password


Windows (Might not work)
1. Download the .exe file from releases
2. On File Explorer double-click on the .exe file
3. Press "Yes" to approve administrator to the app
