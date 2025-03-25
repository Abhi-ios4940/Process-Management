import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager - Real-Time Monitor")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e", rowheight=25)
        style.map("Treeview", background=[("selected", "#4a6984")])

        self.cpu_data = []
        self.mem_data = []

        self.setup_tabs()
        self.update_info()

    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.process_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.performance_tab = tk.Frame(self.notebook, bg="#1e1e1e")

        self.notebook.add(self.process_tab, text="Processes")
        self.notebook.add(self.performance_tab, text="Performance")

        # Process Table
        self.tree = ttk.Treeview(self.process_tab, columns=("PID", "Name", "CPU", "Memory"), show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Process Name")
        self.tree.heading("CPU", text="CPU %")
        self.tree.heading("Memory", text="Memory %")
        self.tree.column("PID", width=100)
        self.tree.column("Name", width=400)
        self.tree.column("CPU", width=100)
        self.tree.column("Memory", width=100)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Graphs
        fig = Figure(figsize=(8, 3), dpi=100)
        self.ax_cpu = fig.add_subplot(121)
        self.ax_mem = fig.add_subplot(122)

        self.ax_cpu.set_title("CPU Usage")
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_xticks([])

        self.ax_mem.set_title("Memory Usage")
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xticks([])

        self.line_cpu, = self.ax_cpu.plot([], [], color='lime')
        self.line_mem, = self.ax_mem.plot([], [], color='orange')

        self.canvas = FigureCanvasTkAgg(fig, master=self.performance_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def update_info(self):
        # CPU and memory usage
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        self.cpu_data.append(cpu)
        self.mem_data.append(mem)

        if len(self.cpu_data) > 50:
            self.cpu_data.pop(0)
            self.mem_data.pop(0)

        self.line_cpu.set_data(range(len(self.cpu_data)), self.cpu_data)
        self.line_mem.set_data(range(len(self.mem_data)), self.mem_data)
        self.ax_cpu.set_xlim(0, len(self.cpu_data))
        self.ax_mem.set_xlim(0, len(self.mem_data))

        self.ax_cpu.figure.canvas.draw()

        # Process info
        for row in self.tree.get_children():
            self.tree.delete(row)

        process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                process_list.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by Memory usage
        process_list.sort(key=lambda x: x['memory_percent'], reverse=True)

        for proc in process_list[:30]:  # show top 30
            self.tree.insert("", "end", values=(
                proc['pid'],
                proc['name'][:30],
                f"{proc['cpu_percent']:.1f}%",
                f"{proc['memory_percent']:.1f}%"
            ))

        self.root.after(1000, self.update_info)

# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()