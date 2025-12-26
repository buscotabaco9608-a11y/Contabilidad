import tkinter as tk
from tkinter import ttk, messagebox
from Core.logger import setup_logger

# Modulos
from Gui.Pages.Styles.Main_styles import MainStyles
from Gui.Pages.resumenes import ResumenesFrame
from Gui.Pages.compras import ComprasFrame
from Gui.Pages.produccion import ProduccionFrame
from Gui.Pages.ventas import VentasFrame
from Gui.Pages.Productos import ProductosFrame

class MainInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicacion de Economia")
        self.root.attributes("-fullscreen", True)
        self.styles = MainStyles(self.root)
        self.logger = setup_logger()

        # Make menu extensible: List of (label, page_name) tuples
        self.menu_items = [
                        (
                "Compras",
                "compras",
            ),  # Button for Compras: Manage purchases and inventory
            (
                "Resumenes",
                "resumenes",
            ),  # Button for Resumenes: Overview of summaries and reports
            (
                "Produccion",
                "produccion",
            ),  # Button for Produccion: Track production processes and costs
            (
                "Productos",
                "productos",
            ), 
            (
                "Ventas",
                "ventas",
            ),  # Button for Ventas: Handle sales and revenue tracking
 # Button for Productos: Catalog and manage products
            ("Gastos", "gastos"),  # Button for Gastos: Record and categorize expenses
        ]

        self.current_page = None
        self.setup_ui()
        self.root.update()  # Force update to show the UI immediately
        #self.show_page("compras")  # Load initial page after UI is set up

        # Bind escape key to exit
        self.root.bind("<Escape>", self.confirm_exit)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Side menu frame (left) - Modern card-like design
        self.menu_frame = ttk.Frame(main_container, width=220, relief="flat")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        self.menu_frame.pack_propagate(False)  # Fixed width

        # Menu card background
        menu_card = tk.Frame(self.menu_frame, bg="#ffffff", relief="flat", bd=0)
        menu_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Title in menu
        title_label = ttk.Label(
            menu_card, text="Menú Principal", font=("Segoe UI", 16, "bold"), foreground="#2d2d30"
        )
        title_label.pack(pady=(20, 15))

        # Create buttons for each menu item with modern styling
        for label, page_name in self.menu_items:
            btn = ttk.Button(
                menu_card,
                text=label,
                command=lambda p=page_name: self.show_page(p),
                style="Secondary.TButton"
            )
            btn.pack(fill=tk.X, padx=15, pady=3)
            # Log button creation (commented for now, but extensible)
            self.logger.debug(f"Botón creado para {label}")

        # Exit button at the bottom with accent color
        exit_btn = ttk.Button(menu_card, text="Salir", command=self.root.quit, style="Accent.TButton")
        exit_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(10, 20))
        self.logger.info("Botón de salida agregado al menú")

        # Central content frame (right)
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        # Initial placeholder page
        self.show_page("compras")

    def show_page(self, page_name):
        # Clear current page
        if self.current_page:
            self.current_page.destroy()

        if page_name == "compras":
            
            self.current_page = ComprasFrame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)

        elif page_name == "resumenes":
            
            self.current_page = ResumenesFrame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)

        elif page_name == "produccion":
            self.current_page = ProduccionFrame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)

        elif page_name == "productos":
            self.current_page = ProductosFrame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)
            
        elif page_name == "ventas":
            self.current_page = VentasFrame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)

        else:
            # Create new page frame
            self.current_page = ttk.Frame(self.content_frame)
            self.current_page.pack(fill=tk.BOTH, expand=True)

            # Placeholder label for the page
            placeholder_label = ttk.Label(
                self.current_page,
                text=f"Página: {page_name.title()}\n(Placeholder - Contenido a desarrollar)",
                font=("Arial", 12),
                justify=tk.CENTER,
            )
            placeholder_label.pack(expand=True)

        self.logger.info(f"Navegando a página: {page_name}")
        # Here, in future, load actual content from modules (e.g., Gui/pages/resumenes.py)

    def confirm_exit(self, event=None):
        # Confirm exit with a dialog
        if messagebox.askyesno(
            "Confirmar Salida", "¿Estás seguro de que quieres salir de la aplicación?"
        ):
            self.logger.info("Usuario confirmó salida de la aplicación")
            self.root.quit()
        else:
            self.logger.info("Salida cancelada por el usuario")


def run_gui():
    root = tk.Tk()
    app = MainInterface(root)
    root.mainloop()
    # Log app exit
    app.logger.info("Aplicación cerrada")


if __name__ == "__main__":
    run_gui()
