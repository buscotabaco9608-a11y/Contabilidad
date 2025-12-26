import tkinter as tk
from tkinter import ttk, messagebox

class CompraStyles:
    def __init__(self):
        self.style = ttk.Style()

        self.style.configure("Card.TFrame",
            background="#ffffff",
            relief="flat",
            borderwidth=1
        )

        # Modern entry style
        self.style.configure("Modern.TEntry",
            fieldbackground="#ffffff",
            borderwidth=1,
            relief="solid",
            padding=(8, 4)
        )

        # Modern combobox
        self.style.configure("Modern.TCombobox",
            fieldbackground="#ffffff",
            borderwidth=1,
            relief="solid",
            padding=(8, 4)
        )

        # Modern Treeview style
        self.style.configure("Modern.Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat"
        )
        self.style.configure("Modern.Treeview.Heading",
            background="#f8f8f8",
            foreground="#323130",
            relief="flat",
            font=("Segoe UI", 9, "bold")
        )

        # Modern button styles
        self.style.configure("Primary.TButton",
            background="#0078d4",
            foreground="white",
            relief="flat",
            padding=(20, 8),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        self.style.map("Primary.TButton",
            background=[("active", "#106ebe"), ("pressed", "#005a9e")])

        self.style.configure("Secondary.TButton",
            background="#f3f2f1",
            foreground="#323130",
            relief="flat",
            padding=(15, 6),
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.map("Secondary.TButton",
            background=[("active", "#e1dfdd"), ("pressed", "#edebe9")])


