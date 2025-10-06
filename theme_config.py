"""
Theme Configuration for YAS Application

This module contains theme configurations including colors, styles, and other
visual elements for the web application.
"""

class ThemeConfig:
    # Primary Colors
    PRIMARY_YELLOW = "#FFD700"  # Gold yellow
    PRIMARY_BLUE = "#1E88E5"    # Bright blue
    
    # Secondary Colors
    SECONDARY_YELLOW = "#FFF176"  # Light yellow
    SECONDARY_BLUE = "#64B5F6"    # Light blue
    
    # Background Colors
    LIGHT_BACKGROUND = "#F5F5F5"  # Light gray background
    DARK_BACKGROUND = "#212121"   # Dark background
    
    # Text Colors
    PRIMARY_TEXT = "#212121"      # Dark gray
    SECONDARY_TEXT = "#757575"    # Medium gray
    TEXT_ON_YELLOW = "#212121"    # Dark text on yellow
    TEXT_ON_BLUE = "#FFFFFF"      # White text on blue
    
    # Status Colors
    SUCCESS = "#4CAF50"           # Green
    ERROR = "#E53935"             # Red
    WARNING = "#FFA000"           # Amber
    INFO = "#00ACC1"              # Cyan
    
    # Button Styles
    BUTTON_STYLES = {
        'primary': {
            'background': PRIMARY_BLUE,
            'color': TEXT_ON_BLUE,
            'hover': {
                'background': "#1976D2",  # Slightly darker blue
                'color': TEXT_ON_BLUE
            }
        },
        'secondary': {
            'background': PRIMARY_YELLOW,
            'color': TEXT_ON_YELLOW,
            'hover': {
                'background': "#FFC107",  # Slightly darker yellow
                'color': TEXT_ON_YELLOW
            }
        }
    }
    
    # Form Styles
    FORM_STYLES = {
        'input': {
            'border': "1px solid #CCCCCC",
            'border_radius': '4px',
            'focus': {
                'border': f"2px solid {PRIMARY_BLUE}",
                'box_shadow': f"0 0 0 0.2rem rgba(30, 136, 229, 0.25)"
            }
        },
        'label': {
            'color': PRIMARY_TEXT,
            'font_weight': '500'
        }
    }
    
    # Card Styles
    CARD_STYLES = {
        'background': "#FFFFFF",
        'border_radius': '8px',
        'box_shadow': '0 2px 4px rgba(0,0,0,0.1)',
        'padding': '1.5rem',
        'margin_bottom': '1rem'
    }
    
    # Alert Styles
    ALERT_STYLES = {
        'success': {
            'background': "#E8F5E9",
            'color': SUCCESS,
            'border': f"1px solid {SUCCESS}"
        },
        'error': {
            'background': "#FFEBEE",
            'color': ERROR,
            'border': f"1px solid {ERROR}"
        },
        'warning': {
            'background': "#FFF8E1",
            'color': WARNING,
            'border': f"1px solid {WARNING}"
        },
        'info': {
            'background': "#E1F5FE",
            'color': INFO,
            'border': f"1px solid {INFO}"
        }
    }
    
    @classmethod
    def get_css(cls):
        """
        Generate CSS styles based on the theme configuration.
        
        Returns:
            str: CSS styles that can be included in HTML templates.
        """
        return f"""
            :root {{
                /* Primary Colors */
                --primary-yellow: {cls.PRIMARY_YELLOW};
                --primary-blue: {cls.PRIMARY_BLUE};
                
                /* Secondary Colors */
                --secondary-yellow: {cls.SECONDARY_YELLOW};
                --secondary-blue: {cls.SECONDARY_BLUE};
                
                /* Background Colors */
                --light-bg: {cls.LIGHT_BACKGROUND};
                --dark-bg: {cls.DARK_BACKGROUND};
                
                /* Text Colors */
                --primary-text: {cls.PRIMARY_TEXT};
                --secondary-text: {cls.SECONDARY_TEXT};
                --text-on-yellow: {cls.TEXT_ON_YELLOW};
                --text-on-blue: {cls.TEXT_ON_BLUE};
                
                /* Status Colors */
                --success: {cls.SUCCESS};
                --error: {cls.ERROR};
                --warning: {cls.WARNING};
                --info: {cls.INFO};
            }}
            
            body {{
                background-color: var(--light-bg);
                color: var(--primary-text);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
            }}
            
            .btn-primary {{
                background-color: var(--primary-blue);
                color: var(--text-on-blue);
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            
            .btn-primary:hover {{
                background-color: #1976D2;
            }}
            
            .btn-secondary {{
                background-color: var(--primary-yellow);
                color: var(--text-on-yellow);
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            
            .btn-secondary:hover {{
                background-color: #FFC107;
            }}
            
            .card {{
                background: #FFFFFF;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 1.5rem;
                margin-bottom: 1rem;
            }}
            
            .form-control {{
                display: block;
                width: 100%;
                padding: 0.375rem 0.75rem;
                font-size: 1rem;
                line-height: 1.5;
                color: #495057;
                background-color: #fff;
                background-clip: padding-box;
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
                transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
            }}
            
            .form-control:focus {{
                color: #495057;
                background-color: #fff;
                border-color: #80bdff;
                outline: 0;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
            }}
            
            .alert {{
                position: relative;
                padding: 0.75rem 1.25rem;
                margin-bottom: 1rem;
                border: 1px solid transparent;
                border-radius: 0.25rem;
            }}
            
            .alert-success {{
                color: #155724;
                background-color: #d4edda;
                border-color: #c3e6cb;
            }}
            
            .alert-danger {{
                color: #721c24;
                background-color: #f8d7da;
                border-color: #f5c6cb;
            }}
            
            .alert-warning {{
                color: #856404;
                background-color: #fff3cd;
                border-color: #ffeeba;
            }}
            
            .alert-info {{
                color: #0c5460;
                background-color: #d1ecf1;
                border-color: #bee5eb;
            }}
            
            .navbar {{
                background-color: var(--primary-blue);
                color: var(--text-on-blue);
                padding: 1rem 0;
            }}
            
            .navbar-brand {{
                color: var(--text-on-blue);
                font-weight: bold;
                font-size: 1.5rem;
                text-decoration: none;
            }}
            
            .text-primary {{
                color: var(--primary-blue);
            }}
            
            .bg-primary {{
                background-color: var(--primary-blue);
                color: var(--text-on-blue);
            }}
            
            .text-yellow {{
                color: var(--primary-yellow);
            }}
            
            .bg-yellow {{
                background-color: var(--primary-yellow);
                color: var(--text-on-yellow);
            }}
        """
