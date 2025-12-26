"""
Modern ttkbootstrap theme configuration for the Contabilidad application.

This module provides centralized theme management using ttkbootstrap
to create modern, professional UI styling for the application.
"""

from typing import Dict, Tuple
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ThemeConfig:
    """Configuration class for managing application themes."""
    
    # Available themes from ttkbootstrap
    AVAILABLE_THEMES = [
        'darkly',
        'flatly',
        'journal',
        'litera',
        'lumen',
        'minty',
        'morph',
        'pulse',
        'sandstone',
        'simplex',
        'sketchy',
        'solar',
        'superhero',
        'united',
        'yeti'
    ]
    
    # Default theme
    DEFAULT_THEME = 'morph'
    
    # Color palette for the application
    COLORS: Dict[str, str] = {
        'primary': '#0d6efd',      # Bootstrap primary blue
        'secondary': '#6c757d',    # Bootstrap secondary gray
        'success': '#198754',      # Bootstrap success green
        'danger': '#dc3545',       # Bootstrap danger red
        'warning': '#ffc107',      # Bootstrap warning yellow
        'info': '#0dcaf0',         # Bootstrap info cyan
        'light': '#f8f9fa',        # Bootstrap light gray
        'dark': '#212529',         # Bootstrap dark
        'accent': '#00bcd4',       # Accent cyan
    }
    
    # Font configurations
    FONTS: Dict[str, Tuple[str, int, str]] = {
        'title': ('Segoe UI', 14, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'normal': ('Segoe UI', 10, 'normal'),
        'small': ('Segoe UI', 9, 'normal'),
        'monospace': ('Consolas', 10, 'normal'),
    }
    
    # Padding and spacing values (in pixels)
    SPACING = {
        'xs': 2,
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
        'xxl': 24,
    }
    
    # Border radius values
    BORDER_RADIUS = {
        'sm': 2,
        'md': 4,
        'lg': 8,
    }


class ModernTheme:
    """Manager class for applying modern themes to the application."""
    
    def __init__(self, theme_name: str = ThemeConfig.DEFAULT_THEME):
        """
        Initialize the theme manager.
        
        Args:
            theme_name: Name of the ttkbootstrap theme to use
            
        Raises:
            ValueError: If the theme name is not available
        """
        if theme_name not in ThemeConfig.AVAILABLE_THEMES:
            raise ValueError(
                f"Theme '{theme_name}' not found. Available themes: "
                f"{', '.join(ThemeConfig.AVAILABLE_THEMES)}"
            )
        self.theme_name = theme_name
        self.root = None
    
    def create_app(self, app_class=ttk.Window):
        """
        Create the root window with the selected theme.
        
        Args:
            app_class: The application window class (default: ttk.Window)
            
        Returns:
            The configured root window
        """
        self.root = app_class(themename=self.theme_name)
        self.configure_root()
        return self.root
    
    def configure_root(self):
        """Configure the root window with custom settings."""
        if not self.root:
            return
        
        # Configure window properties
        self.root.geometry('1200x800')
        self.root.title('Contabilidad - Accounting Management System')
        
        # Configure colors and appearance
        style = self.root.style
        self._configure_styles(style)
    
    def _configure_styles(self, style):
        """
        Configure custom ttk styles.
        
        Args:
            style: The ttk.Style object
        """
        # Configure button styles
        style.configure(
            'Primary.TButton',
            font=ThemeConfig.FONTS['normal'],
            padding=ThemeConfig.SPACING['md']
        )
        
        style.configure(
            'Success.TButton',
            font=ThemeConfig.FONTS['normal'],
            padding=ThemeConfig.SPACING['md']
        )
        
        # Configure label styles
        style.configure(
            'Title.TLabel',
            font=ThemeConfig.FONTS['title']
        )
        
        style.configure(
            'Heading.TLabel',
            font=ThemeConfig.FONTS['heading']
        )
        
        # Configure frame styles
        style.configure(
            'Card.TFrame',
            relief='flat',
            padding=ThemeConfig.SPACING['lg']
        )
        
        # Configure entry styles
        style.configure(
            'Custom.TEntry',
            padding=ThemeConfig.SPACING['sm']
        )
    
    def get_color(self, color_key: str) -> str:
        """
        Get a color from the theme palette.
        
        Args:
            color_key: The key of the color in ThemeConfig.COLORS
            
        Returns:
            The hex color value
            
        Raises:
            KeyError: If the color key is not found
        """
        if color_key not in ThemeConfig.COLORS:
            raise KeyError(
                f"Color '{color_key}' not found. Available colors: "
                f"{', '.join(ThemeConfig.COLORS.keys())}"
            )
        return ThemeConfig.COLORS[color_key]
    
    def get_font(self, font_key: str) -> Tuple[str, int, str]:
        """
        Get a font configuration from the theme.
        
        Args:
            font_key: The key of the font in ThemeConfig.FONTS
            
        Returns:
            A tuple of (font_name, size, weight)
            
        Raises:
            KeyError: If the font key is not found
        """
        if font_key not in ThemeConfig.FONTS:
            raise KeyError(
                f"Font '{font_key}' not found. Available fonts: "
                f"{', '.join(ThemeConfig.FONTS.keys())}"
            )
        return ThemeConfig.FONTS[font_key]
    
    def get_spacing(self, spacing_key: str) -> int:
        """
        Get a spacing value from the theme.
        
        Args:
            spacing_key: The key of the spacing in ThemeConfig.SPACING
            
        Returns:
            The spacing value in pixels
            
        Raises:
            KeyError: If the spacing key is not found
        """
        if spacing_key not in ThemeConfig.SPACING:
            raise KeyError(
                f"Spacing '{spacing_key}' not found. Available spacings: "
                f"{', '.join(ThemeConfig.SPACING.keys())}"
            )
        return ThemeConfig.SPACING[spacing_key]
    
    @staticmethod
    def list_available_themes() -> list:
        """
        Get a list of all available themes.
        
        Returns:
            List of available theme names
        """
        return ThemeConfig.AVAILABLE_THEMES.copy()


def create_themed_app(theme_name: str = ThemeConfig.DEFAULT_THEME) -> Tuple[ttk.Window, ModernTheme]:
    """
    Convenience function to create a themed application window.
    
    Args:
        theme_name: Name of the theme to use
        
    Returns:
        A tuple of (root_window, theme_manager)
    """
    theme = ModernTheme(theme_name)
    root = theme.create_app()
    return root, theme


if __name__ == '__main__':
    # Example usage
    root, theme = create_themed_app('morph')
    
    # Create example widgets
    main_frame = ttk.Frame(root, style='Card.TFrame')
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    title = ttk.Label(
        main_frame,
        text='Contabilidad Theme Example',
        style='Title.TLabel'
    )
    title.pack(pady=theme.get_spacing('lg'))
    
    # Display available themes
    themes_frame = ttk.LabelFrame(main_frame, text='Available Themes')
    themes_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    for theme_name in ModernTheme.list_available_themes():
        ttk.Label(themes_frame, text=f"• {theme_name}").pack(anchor='w')
    
    # Display color palette
    colors_frame = ttk.LabelFrame(main_frame, text='Color Palette')
    colors_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    for color_key, color_value in ThemeConfig.COLORS.items():
        color_label = ttk.Label(
            colors_frame,
            text=f"{color_key}: {color_value}",
            foreground=color_value if color_key not in ['light', 'warning'] else 'black'
        )
        color_label.pack(anchor='w')
    
    root.mainloop()
