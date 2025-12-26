import tkinter as tk
from tkinter import ttk

class MainStyles:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="#f3f3f3")

        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TLabel", 
            background="#f3f3f3", 
            foreground="#323130", 
            font=("Segoe UI", 9)
        )

        self.style.configure("Secondary.TButton",
            background="#ffffff",
            foreground="#323130",
            relief="flat",
            padding=(15, 8),
            font=("Segoe UI"),
            borderwidth=0
        )

        self.style.map("Secondary.TButton",
            background=[("active", "#e1dfdd"), ("pressed", "#edebe9")]
        )

        self.style.configure("Accent.TButton",
            background="#d13438",
            foreground="white",
            relief="flat",
            padding=(15, 8),
            borderwidth=0
        )

        self.style.map("Accent.TButton",
            background=[("active", "#c42b1c"), ("pressed", "#a72015")]
        )
