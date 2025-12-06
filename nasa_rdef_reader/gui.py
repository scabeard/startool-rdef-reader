"""
GUI for the NASA RDEF File Reader

This module provides a graphical user interface for viewing and analyzing
RDEF telemetry files with a clean, easy-to-use interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Dict, Any, List
import os

from .reader import RDEFReader
from .file_browser import browse_rdef_file


class RDEFGUI:
    """
    Main GUI application for viewing RDEF files.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.
        
        Args:
            root (tk.Tk): Root tkinter window
        """
        self.root = root
        self.root.title("NASA RDEF File Viewer")
        self.root.geometry("1200x800")
        
        # Set proper dark theme colors with high contrast
        self.colors = {
            'bg': '#1a1a1a',      # Main background (dark gray)
            'fg': '#e0e0e0',      # Main text color (light gray)
            'panel': '#2a2a2a',   # Panel background (medium dark gray)
            'accent': '#4a90e2',  # Accent color (blue)
            'border': '#3a3a3a',  # Border color (medium gray)
            'hover': '#357abd',   # Hover color (darker blue)
            'disabled': '#999999' # Disabled text (light gray)
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles for dark theme
        self._setup_dark_theme()
        
        # Configure text widget colors for dark theme
        self._setup_text_widget_colors()
        
        # Data storage
        self.current_file = None
        self.data = None
        
        # Create the GUI
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Header frame with file operations
        header_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(header_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(header_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(header_frame, text="Browse...", command=self._browse_file)
        browse_btn.grid(row=0, column=2, padx=(0, 10))
        
        load_btn = ttk.Button(header_frame, text="Load File", command=self._load_file)
        load_btn.grid(row=0, column=3)
        
        # Metadata frame
        metadata_frame = ttk.LabelFrame(main_frame, text="File Metadata", padding="5")
        metadata_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        metadata_frame.columnconfigure(1, weight=1)
        
        self.metadata_vars = {}
        metadata_fields = [
            ("File Type", "datatype"),
            ("APID", "apid"),
            ("Creation Date", "creation_date"),
            ("Start Time", "start_time"),
            ("End Time", "end_time"),
            ("Number of Packets", "num_packets"),
            ("Comment", "comment")
        ]
        
        for i, (label, key) in enumerate(metadata_fields):
            ttk.Label(metadata_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            self.metadata_vars[key] = tk.StringVar()
            ttk.Label(metadata_frame, textvariable=self.metadata_vars[key]).grid(row=i, column=1, sticky=tk.W)
        
        # Packets frame
        packets_frame = ttk.LabelFrame(main_frame, text="Packets", padding="5")
        packets_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        packets_frame.columnconfigure(0, weight=1)
        packets_frame.rowconfigure(0, weight=1)
        
        # Packets treeview
        columns = ("Packet #", "Offset", "Header", "Data Preview")
        self.packet_tree = ttk.Treeview(packets_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.packet_tree.heading(col, text=col)
            self.packet_tree.column(col, width=100)
        
        # Scrollbars
        vsb = ttk.Scrollbar(packets_frame, orient="vertical", command=self.packet_tree.yview)
        hsb = ttk.Scrollbar(packets_frame, orient="horizontal", command=self.packet_tree.xview)
        self.packet_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.packet_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.packet_tree.bind('<<TreeviewSelect>>', self._on_packet_select)
        
        # Packet details frame
        details_frame = ttk.LabelFrame(main_frame, text="Packet Details", padding="5")
        details_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 5))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        ttk.Label(details_frame, text="Selected Packet:").grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
        
        self.packet_details_text = tk.Text(details_frame, height=15, width=35, wrap=tk.WORD)
        self.packet_details_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        details_vsb = ttk.Scrollbar(details_frame, orient="vertical", command=self.packet_details_text.yview)
        self.packet_details_text.configure(yscrollcommand=details_vsb.set)
        details_vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=2)  # Give more weight to packets frame
        main_frame.columnconfigure(1, weight=1)  # Smaller weight to details frame
        main_frame.rowconfigure(2, weight=1)
        
    def _browse_file(self) -> None:
        """Open file dialog to select an RDEF file."""
        # Determine initial directory - use current file's directory or user's Documents
        current_file_path = self.file_path_var.get().strip()
        if current_file_path:
            initial_dir = os.path.dirname(current_file_path)
        else:
            # Try to get user's Documents folder as default
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get user's Documents folder on Windows
                CSIDL_PERSONAL = 5       # My Documents
                SHGFP_TYPE_CURRENT = 0   # Get current, not default value
                
                buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
                initial_dir = buf.value
            except:
                # Fallback to current directory
                initial_dir = os.getcwd()
        
        # Use our custom file browser with dark theme
        file_path = browse_rdef_file(self.root, initial_dir=initial_dir)
        if file_path:
            self.file_path_var.set(file_path)
            
    def _load_file(self) -> None:
        """Load and parse the selected RDEF file."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select a file to load.")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"File not found: {file_path}")
            return
            
        # Run file loading in a separate thread to avoid blocking UI
        self.status_var.set("Loading file...")
        self.root.update()
        
        def load_worker():
            try:
                reader = RDEFReader(file_path)
                self.data = reader.read()
                self.current_file = file_path
                
                # Update UI on main thread
                self.root.after(0, self._update_ui_with_data)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file: {e}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=load_worker, daemon=True).start()
        
    def _update_ui_with_data(self) -> None:
        """Update the UI with loaded file data."""
        if not self.data:
            return
            
        # Update metadata
        metadata = self.data['metadata']
        for key, var in self.metadata_vars.items():
            var.set(metadata.get(key, "N/A"))
            
        # Update packet list
        self.packet_tree.delete(*self.packet_tree.get_children())
        
        packets = self.data['packets']
        for i, packet in enumerate(packets):
            header_preview = packet.get('raw_header', '')[:16]
            data_preview = packet.get('raw_data', '')[:32]
            
            self.packet_tree.insert('', tk.END, values=(
                i + 1,
                packet.get('data_offset', 'N/A'),
                header_preview,
                data_preview
            ))
            
        self.status_var.set(f"Loaded {len(packets)} packets from {os.path.basename(self.current_file)}")
        
    def _setup_dark_theme(self) -> None:
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        
        # Configure basic colors
        style.theme_use('default')
        
        # Configure various widget styles with explicit colors
        style.configure('TFrame', 
                       background=self.colors['panel'],
                       foreground=self.colors['fg'])
        style.configure('TLabelFrame', 
                       background=self.colors['panel'], 
                       foreground=self.colors['fg'])
        style.configure('TLabelFrame.Label', 
                       background=self.colors['panel'], 
                       foreground=self.colors['fg'])
        style.configure('TLabel', 
                       background=self.colors['panel'], 
                       foreground=self.colors['fg'])
        style.configure('TButton', 
                       background=self.colors['panel'], 
                       foreground=self.colors['fg'],
                       relief='raised')
        style.map('TButton',
                 background=[('active', self.colors['hover'])],
                 foreground=[('active', '#ffffff')])
        style.configure('TEntry', 
                       fieldbackground=self.colors['panel'], 
                       foreground=self.colors['fg'],
                       insertcolor=self.colors['fg'])
        style.configure('TCombobox', 
                       fieldbackground=self.colors['panel'], 
                       foreground=self.colors['fg'],
                       insertcolor=self.colors['fg'])
        
        # Treeview style with explicit colors
        style.configure('Treeview', 
                       background=self.colors['panel'],
                       foreground=self.colors['fg'],
                       fieldbackground=self.colors['panel'],
                       bordercolor=self.colors['border'],
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'])
        style.configure('Treeview.Heading',
                       background=self.colors['accent'],
                       foreground=self.colors['fg'],
                       bordercolor=self.colors['border'])
        style.map('Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', '#000000')])
        
        # Scrollbar style
        style.configure('Vertical.TScrollbar', 
                       background=self.colors['panel'],
                       troughcolor=self.colors['bg'])
        style.configure('Horizontal.TScrollbar', 
                       background=self.colors['panel'],
                       troughcolor=self.colors['bg'])
        
        # Configure ttk defaults
        style.configure('.', 
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       selectbackground=self.colors['accent'],
                       selectforeground='#000000')
        
    def _setup_text_widget_colors(self) -> None:
        """Configure text widget colors for dark theme."""
        # This will be called when widgets are created
        pass
        
    def _on_packet_select(self, event) -> None:
        """Handle packet selection in the treeview."""
        selection = self.packet_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        packet_index = self.packet_tree.index(item)
        
        if self.data and packet_index < len(self.data['packets']):
            packet = self.data['packets'][packet_index]
            
            # Display packet details with enhanced telemetry
            details = f"Packet #{packet_index + 1}\n"
            details += f"Data Offset: {packet.get('data_offset', 'N/A')}\n"
            details += f"Raw Header: {packet.get('raw_header', 'N/A')}\n"
            details += f"Raw Data: {packet.get('raw_data', 'N/A')}\n\n"
            
            # Add telemetry data if available
            if 'telemetry' in packet:
                telemetry = packet['telemetry']
                details += "=== ENHANCED TELEMETRY ANALYSIS ===\n"
                
                # Timestamps
                if 'timestamp_readable' in telemetry:
                    details += f"Timestamp: {telemetry['timestamp_readable']}\n"
                if 'timestamp_2_readable' in telemetry:
                    details += f"Timestamp 2: {telemetry['timestamp_2_readable']}\n"
                
                # Numeric values
                if 'uint32_le_0' in telemetry:
                    details += f"32-bit Value (LE): {telemetry['uint32_le_0']}\n"
                if 'uint32_be_0' in telemetry:
                    details += f"32-bit Value (BE): {telemetry['uint32_be_0']}\n"
                
                if 'uint16_le_0' in telemetry:
                    details += f"16-bit Value 1 (LE): {telemetry['uint16_le_0']}\n"
                if 'uint16_le_1' in telemetry:
                    details += f"16-bit Value 2 (LE): {telemetry['uint16_le_1']}\n"
                
                # Float values
                if 'float32_le_0' in telemetry:
                    details += f"Float Value (LE): {telemetry['float32_le_0']:.6f}\n"
                if 'float32_be_0' in telemetry:
                    details += f"Float Value (BE): {telemetry['float32_be_0']:.6f}\n"
                
                # Small sensor values
                if 'small_uint16_values' in telemetry:
                    details += f"Sensor Values: {telemetry['small_uint16_values']}\n"
                
                # ASCII strings
                if 'ascii_strings' in telemetry:
                    details += f"ASCII Strings: {', '.join(telemetry['ascii_strings'])}\n"
                
                # Parse errors
                if 'parse_error' in telemetry:
                    details += f"Parse Error: {telemetry['parse_error']}\n"
                
                # LASCO-specific decoding (NEW)
                if 'lasco_decoded' in telemetry:
                    lasco = telemetry['lasco_decoded']
                    details += "\n=== LASCO SOHO DECODED DATA ===\n"
                    
                    # CCSDS Header
                    if 'ccsds_header' in lasco:
                        ccsds = lasco['ccsds_header']
                        details += f"CCSDS Packet:\n"
                        details += f"  APID: 0x{ccsds['apid']:03X}\n"
                        details += f"  Type: {ccsds['type']}\n"
                        details += f"  Sequence: {ccsds['sequence']}\n"
                        details += f"  Length: {ccsds['packet_length']} bytes\n"
                    
                    # Instrument type
                    if 'instrument_type' in lasco:
                        details += f"Instrument: {lasco['instrument_type']}\n"
                    
                    # Housekeeping data
                    if 'housekeeping' in lasco:
                        hk = lasco['housekeeping']
                        details += f"\nHousekeeping Data:\n"
                        if 'voltage_1' in hk:
                            details += f"  Voltage 1: {hk['voltage_1']:.3f} V\n"
                        if 'voltage_2' in hk:
                            details += f"  Voltage 2: {hk['voltage_2']:.3f} V\n"
                        if 'temperature_1_c' in hk:
                            details += f"  Temperature 1: {hk['temperature_1_c']:.1f} °C\n"
                        if 'temperature_2_c' in hk:
                            details += f"  Temperature 2: {hk['temperature_2_c']:.1f} °C\n"
                        if 'current_1' in hk:
                            details += f"  Current 1: {hk['current_1']:.3f} A\n"
                        if 'status_flags' in hk:
                            status = hk['status_flags']
                            details += f"  Status Flags:\n"
                            for flag, value in status.items():
                                details += f"    {flag}: {'✓' if value else '✗'}\n"
                    
                    # Science data
                    if 'science_data' in lasco:
                        sci = lasco['science_data']
                        details += f"\nScience Data:\n"
                        if 'image_width' in sci and 'image_height' in sci:
                            details += f"  Image: {sci['image_width']} x {sci['image_height']}\n"
                        if 'compression_type' in sci:
                            details += f"  Compression: {sci['compression_type']}\n"
                        if 'bit_depth' in sci:
                            details += f"  Bit Depth: {sci['bit_depth']} bits\n"
                        if 'exposure_time_ms' in sci:
                            details += f"  Exposure: {sci['exposure_time_ms']} ms\n"
                        if 'filter_position' in sci:
                            details += f"  Filter: {sci['filter_position']}\n"
                        if 'expected_image_size' in sci:
                            details += f"  Expected Size: {sci['expected_image_size']} bytes\n"
                    
                    # Compressed data
                    if 'compressed_data' in lasco:
                        comp = lasco['compressed_data']
                        details += f"\nCompressed Data:\n"
                        if 'compressed_size' in comp:
                            details += f"  Compressed Size: {comp['compressed_size']} bytes\n"
                        if 'uncompressed_size' in comp:
                            details += f"  Uncompressed Size: {comp['uncompressed_size']} bytes\n"
                        if 'compression_ratio' in comp:
                            details += f"  Compression Ratio: {comp['compression_ratio']:.2f}:1\n"
                        if 'data_checksum' in comp:
                            details += f"  Checksum: 0x{comp['data_checksum']:08X}\n"
                    
                # LASCO decode errors
                if 'lasco_decode_error' in lasco:
                    details += f"LASCO Decode Error: {lasco['lasco_decode_error']}\n"
            
            # Enhanced Analysis Section (NEW)
            if 'timestamps' in telemetry:
                details += "\n=== ENHANCED TIMESTAMPS ===\n"
                for ts_name, ts_data in telemetry['timestamps'].items():
                    details += f"{ts_data['type']} ({ts_data['offset']}): {ts_data['readable']}\n"
            
            if 'sensors' in telemetry:
                details += "\n=== SENSOR ANALYSIS ===\n"
                for sensor_name, sensor_data in telemetry['sensors'].items():
                    details += f"{sensor_data['description']} ({sensor_data['offset']}): {sensor_data['converted']} {sensor_data['unit']}"
                    if 'context' in sensor_data:
                        details += f" [{sensor_data['context']}]\n"
                    else:
                        details += "\n"
            
            if 'status_analysis' in telemetry:
                details += "\n=== STATUS FLAG ANALYSIS ===\n"
                for status_name, status_data in telemetry['status_analysis'].items():
                    details += f"{status_data['status_type']} (offset {status_data['offset']}, {status_data['health_indicator']}):\n"
                    details += f"  Value: {status_data['hex_value']} ({status_data['binary_value']})\n"
                    details += f"  Set Bits: {status_data['set_bits']}/8\n"
                    for bit_desc, bit_val in status_data['bits'].items():
                        details += f"    {bit_desc}: {'✓' if bit_val else '✗'}\n"
                    details += "\n"
            
            if 'structures' in telemetry:
                details += "\n=== DATA STRUCTURES ===\n"
                for struct_name, struct_data in telemetry['structures'].items():
                    details += f"{struct_data['type']} (offset {struct_data['start_offset']}):\n"
                    details += f"  Description: {struct_data['description']}\n"
                    details += f"  Count: {struct_data['count']} values\n"
                    if 'range' in struct_data:
                        details += f"  Range: {struct_data['range']}\n"
                    if 'pattern' in struct_data:
                        details += f"  Pattern: {struct_data['pattern']}\n"
                    if 'unique_values' in struct_data:
                        details += f"  Values: {struct_data['unique_values']}\n"
                    details += "\n"
            
            if 'correlations' in telemetry:
                details += "\n=== PARAMETER CORRELATIONS ===\n"
                for corr_name, corr_data in telemetry['correlations'].items():
                    details += f"{corr_name}:\n"
                    for key, value in corr_data.items():
                        if isinstance(value, list):
                            details += f"  {key}: {', '.join(map(str, value[:5]))}{'...' if len(value) > 5 else ''}\n"
                        else:
                            details += f"  {key}: {value}\n"
                    details += "\n"
            
            self.packet_details_text.delete(1.0, tk.END)
            self.packet_details_text.insert(tk.END, details)
            
            # Configure text widget colors after creation
            self.packet_details_text.configure(
                bg=self.colors['panel'],
                fg=self.colors['fg'],
                insertbackground=self.colors['fg'],
                selectbackground=self.colors['accent'],
                selectforeground='#000000'
            )


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = RDEFGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
