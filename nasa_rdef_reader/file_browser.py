"""
Custom file browser for RDEF files with dark theme support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from typing import Optional


class CustomFileBrowser:
    """
    Custom file browser dialog that supports dark theme
    """
    
    def __init__(self, parent, initial_dir=None):
        self.parent = parent
        # Ensure we have a proper initial directory, default to user's Documents folder
        if initial_dir:
            self.initial_dir = os.path.normpath(initial_dir)
        else:
            # Try to get user's Documents folder, fall back to current directory
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get user's Documents folder on Windows
                CSIDL_PERSONAL = 5       # My Documents
                SHGFP_TYPE_CURRENT = 0   # Get current, not default value
                
                buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
                self.initial_dir = buf.value
            except:
                # Fallback to current directory if we can't get Documents folder
                self.initial_dir = os.getcwd()
        self.selected_file = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select RDEF File")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Dark theme colors
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#e0e0e0',
            'panel': '#2a2a2a',
            'accent': '#4a90e2',
            'border': '#3a3a3a'
        }
        
        self.dialog.configure(bg=self.colors['bg'])
        
        # Create widgets
        self._create_widgets()
        
        # Populate initial directory
        self._populate_directory(self.initial_dir)
        
        # Center dialog on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_widgets(self):
        """Create the file browser widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Path entry
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky=tk.W)
        
        self.path_var = tk.StringVar(value=self.initial_dir)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self._browse_directory)
        browse_btn.grid(row=0, column=2, padx=(5, 0))
        
        go_btn = ttk.Button(path_frame, text="Go", command=lambda: self._populate_directory(self.path_var.get()))
        go_btn.grid(row=0, column=3, padx=(5, 0))
        
        # File list
        files_frame = ttk.LabelFrame(main_frame, text="Files", padding="5")
        files_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        
        # File treeview
        columns = ("Name", "Type", "Size")
        self.file_tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=100)
        
        # Scrollbars
        vsb = ttk.Scrollbar(files_frame, orient="vertical", command=self.file_tree.yview)
        hsb = ttk.Scrollbar(files_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click
        self.file_tree.bind('<Double-1>', self._on_double_click)
        self.file_tree.bind('<Return>', self._on_double_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.E), pady=(0, 10))
        
        select_btn = ttk.Button(button_frame, text="Select", command=self._select_file)
        select_btn.grid(row=0, column=0, padx=(0, 5))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        cancel_btn.grid(row=0, column=1)
        
        # Configure styles for dark theme
        self._setup_dark_theme()
        
    def _setup_dark_theme(self):
        """Setup dark theme for the file browser"""
        style = ttk.Style()
        
        # Configure treeview for dark theme
        style.configure('Treeview', 
                       background=self.colors['panel'],
                       foreground=self.colors['fg'],
                       fieldbackground=self.colors['panel'],
                       bordercolor=self.colors['border'])
        style.configure('Treeview.Heading',
                       background=self.colors['accent'],
                       foreground=self.colors['fg'],
                       bordercolor=self.colors['border'])
        style.map('Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', '#000000')])
        
        # Configure other widgets
        style.configure('TFrame', background=self.colors['panel'])
        style.configure('TLabelFrame', background=self.colors['panel'], foreground=self.colors['fg'])
        style.configure('TLabelFrame.Label', background=self.colors['panel'], foreground=self.colors['fg'])
        style.configure('TLabel', background=self.colors['panel'], foreground=self.colors['fg'])
        style.configure('TEntry', fieldbackground=self.colors['panel'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['panel'], foreground=self.colors['fg'])
        
    def _populate_directory(self, path):
        """Populate the file tree with contents of the given directory"""
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Update path
            self.path_var.set(path)
            
            # Get directory contents
            if os.path.exists(path) and os.path.isdir(path):
                items = []
                
                # Add parent directory
                parent = os.path.dirname(path)
                if parent != path:  # Not root
                    items.append(('..', 'Directory', ''))
                
                # Add files and directories
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            items.append((item, 'Directory', ''))
                        elif item.lower().endswith(('.rel', '.sdu')):
                            size = os.path.getsize(item_path)
                            items.append((item, 'RDEF File', f'{size} bytes'))
                except PermissionError:
                    messagebox.showerror("Permission Error", f"Cannot access directory: {path}")
                    return
                
                # Insert items into tree
                for name, item_type, size in items:
                    self.file_tree.insert('', tk.END, values=(name, item_type, size))
            else:
                messagebox.showerror("Error", f"Directory not found: {path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read directory: {e}")
    
    def _browse_directory(self):
        """Open system directory browser"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(initialdir=self.path_var.get())
        if directory:
            self._populate_directory(directory)
    
    def _on_double_click(self, event=None):
        """Handle double-click on file"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item)['values']
            name = values[0]
            item_type = values[1]
            
            current_path = self.path_var.get()
            
            if name == '..':
                # Go up one directory
                parent = os.path.dirname(current_path)
                self._populate_directory(parent)
            elif item_type == 'Directory':
                # Open directory
                new_path = os.path.join(current_path, name)
                self._populate_directory(new_path)
            else:
                # Select file
                self._select_file()
    
    def _select_file(self):
        """Select the currently highlighted file"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item)['values']
            name = values[0]
            item_type = values[1]
            
            if item_type != 'Directory':
                current_path = self.path_var.get()
                self.selected_file = os.path.join(current_path, name)
                self.dialog.destroy()
            else:
                messagebox.showinfo("Info", "Please select a file, not a directory.")
        else:
            messagebox.showwarning("Warning", "Please select a file.")
    
    def _cancel(self):
        """Cancel and close dialog"""
        self.selected_file = None
        self.dialog.destroy()


def browse_rdef_file(parent, initial_dir=None):
    """
    Show custom file browser and return selected file path
    
    Args:
        parent: Parent tkinter widget
        initial_dir: Initial directory to browse (optional)
        
    Returns:
        Selected file path or None
    """
    browser = CustomFileBrowser(parent, initial_dir)
    parent.wait_window(browser.dialog)
    return browser.selected_file
