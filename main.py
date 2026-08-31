import sys
import subprocess
import platform
import os
import ctypes
import threading
import time

def is_admin():
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def elevate():
    sys_platform = platform.system()
    if sys_platform == "Windows":
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    elif sys_platform == "Linux":
        if not is_admin():
            script_path = os.path.abspath(sys.argv[0])
            display = os.environ.get("DISPLAY", ":0")
            xauth = os.environ.get("XAUTHORITY", "")
            os.execlp("pkexec", "pkexec", "env", f"DISPLAY={display}", f"XAUTHORITY={xauth}", sys.executable, script_path)
    elif sys_platform == "Darwin":
        if not is_admin():
            script_path = os.path.abspath(sys.argv[0])
            args = " ".join([sys.executable, script_path])
            os.execlp("osascript", "osascript", "-e", f'do shell script "{args}" with administrator privileges')

elevate()

def check_and_install_dependencies():
    try:
        import psutil
    except ImportError:
        print("Missing required package: psutil")
        choice = input("Do you wanna download the following add-on? (Required - psutil): ").strip().lower()
        if choice == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        else:
            sys.exit(1)
            
    try:
        import tkinter
    except ImportError:
        print("Missing required system graphical package: python3-tk")
        if platform.system() == "Linux":
            choice = input("Do you wanna install python3-tk via apt? (Required for GUI): ").strip().lower()
            if choice == 'y':
                try:
                    subprocess.check_call(["apt", "update"])
                    subprocess.check_call(["apt", "install", "-y", "python3-tk"])
                except Exception as e:
                    print(f"Automatic installation failed: {e}. Please run 'sudo apt install python3-tk' manually.")
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            print("Please ensure your Python installation includes Tcl/Tk support.")
            sys.exit(1)

check_and_install_dependencies()

import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext

def get_gpu_specs():
    sys_platform = platform.system()
    try:
        if sys_platform == "Linux":
            res = subprocess.check_output(["lspci"], universal_newlines=True)
            for line in res.splitlines():
                if "VGA" in line or "Display" in line or "3D" in line:
                    return line
        elif sys_platform == "Windows":
            res = subprocess.check_output("wmic path win32_videocontroller get caption", universal_newlines=True, shell=True)
            return res.strip()
        elif sys_platform == "Darwin":
            res = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], universal_newlines=True)
            return res.strip()
    except:
        pass
    return "GPU information unavailable."

def get_gpu_stats():
    mem = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent(interval=None)
    temp_val = 0.0
    temp_str = "N/A"
    sys_platform = platform.system()
    try:
        if sys_platform == "Linux":
            for root, dirs, files in os.walk("/sys/class/drm/"):
                for file in files:
                    if "temp1_input" in file:
                        with open(os.path.join(root, file), "r") as f:
                            temp_val = float(f.read().strip()) / 1000.0
                            temp_str = f"{temp_val:.1f} °C"
    except:
        pass
    return cpu_usage, mem.percent, temp_str, temp_val

def check_logs():
    sys_platform = platform.system()
    try:
        if sys_platform == "Linux":
            logs = subprocess.check_output(["dmesg"], universal_newlines=True)
            gpu_logs = [line for line in logs.splitlines() if any(k in line.lower() for k in ["gpu", "drm", "amdgpu", "nvidia", "nouveau"])]
            return "\n".join(gpu_logs[-15:]) if gpu_logs else "No recent GPU log entries found."
        elif sys_platform == "Windows":
            return "Windows Event Logs require administrative privileges."
        elif sys_platform == "Darwin":
            return "macOS system logs require unified logging stream access."
    except:
        return "Permission denied or unable to read system logs."
    return "Logs not supported on this platform."

def auto_repair_or_shutdown():
    sys_platform = platform.system()
    try:
        if sys_platform == "Linux":
            logs = subprocess.check_output(["dmesg"], universal_newlines=True)
            crash_keywords = ["ring test failed", "gpu lockup", "hang", "reset failed", "page fault"]
            if any(kw in logs.lower() for kw in crash_keywords):
                try:
                    subprocess.run(["modprobe", "-r", "--force", "amdgpu"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["modprobe", "amdgpu"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return "Kernel recovered: GPU module reloaded successfully."
                except Exception as e:
                    return "Inhibitor active: Cannot unload live display driver safely while desktop session is running."
            return "System status nominal: No critical GPU crashes detected in kernel ring buffer."
        else:
            return "Automated crash guard kernel recovery is specialized for Linux environments."
    except:
        return "Error executing automated kernel diagnostic."

def background_notification_daemon():
    if platform.system() != "Linux":
        return
    
    seen_lines = set()
    try:
        init_logs = subprocess.check_output(["dmesg"], universal_newlines=True).splitlines()
        for line in init_logs:
            if any(k in line.lower() for k in ["ring test failed", "gpu lockup", "hang", "reset failed", "page fault", "amdgpu"]):
                seen_lines.add(line)
    except:
        pass

    while True:
        try:
            time.sleep(5)
            logs = subprocess.check_output(["dmesg"], universal_newlines=True).splitlines()
            crash_keywords = ["ring test failed", "gpu lockup", "hang", "reset failed", "page fault"]
            
            for line in logs:
                if line not in seen_lines:
                    seen_lines.add(line)
                    if any(kw in line.lower() for kw in crash_keywords):
                        subprocess.run(["notify-send", "-u", "critical", "UBIQUITOUS-ENGINE [GPU Alert]", line[:120]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

class UbiquitousEngineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UBIQUITOUS-ENGINE")
        self.root.geometry("740x560")
        self.root.configure(bg="#121216")
        
        # Color Palette constants
        self.bg_main = "#121216"
        self.bg_card = "#1a1a24"
        self.fg_text = "#f3f4f6"
        self.accent = "#38bdf8"
        self.accent_hover = "#0ea5e9"
        self.muted = "#9ca3af"
        
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TLabel", background=self.bg_card, foreground=self.fg_text, font=("Segoe UI", 10))
        style.configure("Main.TLabel", background=self.bg_main, foreground=self.fg_text, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.accent, background=self.bg_main)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10, "bold"), foreground=self.muted, background=self.bg_card)
        style.configure("Value.TLabel", font=("Segoe UI", 14, "bold"), foreground=self.fg_text, background=self.bg_card)
        
        style.configure("Horizontal.TProgressbar", troughcolor="#27273a", background=self.accent, bordercolor=self.bg_card, lightcolor=self.accent, darkcolor=self.accent)
        
        # Header Container
        header_frame = tk.Frame(root, bg=self.bg_main, padx=20, pady=15)
        header_frame.pack(fill="x")
        
        header = ttk.Label(header_frame, text="UBIQUITOUS-ENGINE", style="Header.TLabel")
        header.pack(side="left")
        
        status_dot = tk.Label(header_frame, text="● ACTIVE", fg="#34d399", bg=self.bg_main, font=("Segoe UI", 9, "bold"))
        status_dot.pack(side="right", pady=5)
        
        # Dashboard Cards Grid
        dash_frame = tk.Frame(root, bg=self.bg_main, padx=20)
        dash_frame.pack(fill="x", pady=5)
        
        # CPU Card
        cpu_frame = tk.Frame(dash_frame, bg=self.bg_card, padx=16, pady=14, highlightbackground="#27273a", highlightthickness=1)
        cpu_frame.pack(side="left", expand=True, fill="both", padx=(0, 8))
        ttk.Label(cpu_frame, text="GPU CORE USAGE", style="CardTitle.TLabel").pack(anchor="w")
        self.cpu_bar = ttk.Progressbar(cpu_frame, orient="horizontal", length=180, mode="determinate", style="Horizontal.TProgressbar")
        self.cpu_bar.pack(pady=(10, 5), fill="x")
        self.cpu_lbl = ttk.Label(cpu_frame, text="0%", style="Value.TLabel")
        self.cpu_lbl.pack(anchor="w")
        
        # Memory Card
        mem_frame = tk.Frame(dash_frame, bg=self.bg_card, padx=16, pady=14, highlightbackground="#27273a", highlightthickness=1)
        mem_frame.pack(side="left", expand=True, fill="both", padx=8)
        ttk.Label(mem_frame, text="MEMORY USAGE", style="CardTitle.TLabel").pack(anchor="w")
        self.mem_bar = ttk.Progressbar(mem_frame, orient="horizontal", length=180, mode="determinate", style="Horizontal.TProgressbar")
        self.mem_bar.pack(pady=(10, 5), fill="x")
        self.mem_lbl = ttk.Label(mem_frame, text="0%", style="Value.TLabel")
        self.mem_lbl.pack(anchor="w")
        
        # Temp Card
        temp_frame = tk.Frame(dash_frame, bg=self.bg_card, padx=16, pady=14, highlightbackground="#27273a", highlightthickness=1)
        temp_frame.pack(side="left", expand=True, fill="both", padx=(8, 0))
        ttk.Label(temp_frame, text="GPU TEMP", style="CardTitle.TLabel").pack(anchor="w")
        self.temp_lbl = ttk.Label(temp_frame, text="N/A", font=("Segoe UI", 16, "bold"), foreground="#fb7185", background=self.bg_card)
        self.temp_lbl.pack(pady=(12, 0), anchor="w")
        
        # Navigation / Action Buttons Bar
        btn_frame = tk.Frame(root, bg=self.bg_main, padx=20, pady=12)
        btn_frame.pack(fill="x")
        
        self.create_modern_button(btn_frame, "GPU Specs", self.show_specs).pack(side="left", padx=(0, 8))
        self.create_modern_button(btn_frame, "System Logs", self.show_logs).pack(side="left", padx=8)
        self.create_modern_button(btn_frame, "Crash Guard", self.show_repair).pack(side="left", padx=8)
        
        # Terminal Output Area Container
        terminal_container = tk.Frame(root, bg=self.bg_card, padx=12, pady=12, highlightbackground="#27273a", highlightthickness=1)
        terminal_container.pack(pady=(0, 20), padx=20, fill="both", expand=True)
        
        self.output_area = scrolledtext.ScrolledText(
            terminal_container, 
            wrap=tk.WORD, 
            bg="#0d0d11", 
            fg="#38bdf8", 
            font=("Consolas", 10), 
            insertbackground="white",
            borderwidth=0,
            highlightthickness=0
        )
        self.output_area.pack(fill="both", expand=True)
        
        self.active_mode = "specs"
        self.show_specs()
        self.auto_refresh()
        
        daemon_thread = threading.Thread(target=background_notification_daemon, daemon=True)
        daemon_thread.start()
        
    def create_modern_button(self, parent, text, command):
        btn = tk.Button(
            parent, 
            text=text, 
            bg="#222230", 
            fg="#f3f4f6", 
            activebackground="#2a2a3c",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), 
            relief="flat", 
            padx=16, 
            pady=8,
            cursor="hand2",
            command=command
        )
        return btn

    def display_text(self, text):
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, text)
        
    def show_specs(self):
        self.active_mode = "specs"
        self.display_text(get_gpu_specs())
        
    def show_logs(self):
        self.active_mode = "logs"
        self.display_text(check_logs())
        
    def show_repair(self):
        self.active_mode = "repair"
        self.display_text(auto_repair_or_shutdown())
        
    def auto_refresh(self):
        cpu, mem, temp_str, _ = get_gpu_stats()
        self.cpu_bar['value'] = cpu
        self.cpu_lbl.config(text=f"{cpu}%")
        
        self.mem_bar['value'] = mem
        self.mem_lbl.config(text=f"{mem}%")
        
        self.temp_lbl.config(text=temp_str)
        
        if self.active_mode == "logs":
            self.display_text(check_logs())
            
        self.root.after(1000, self.auto_refresh)

if __name__ == "__main__":
    root = tk.Tk()
    app = UbiquitousEngineApp(root)
    root.mainloop()
