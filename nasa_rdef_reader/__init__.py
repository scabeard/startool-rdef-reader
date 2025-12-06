"""
NASA RDEF File Reader - A tool for reading legacy NASA telemetry files

This module provides functionality to read and parse RDEF (Relational Data Exchange Format) files,
which are legacy binary format used by NASA Goddard Space Flight Center for ground-system 
telemetry processing.

Example usage:
    from nasa_rdef_reader import RDEFReader
    
    # Read a file
    reader = RDEFReader("SVMHK1_251204_120317.REL")
    data = reader.read()
    
    # Access metadata and packets
    print(f"File type: {data['metadata']['datatype']}")
    print(f"Number of packets: {len(data['packets'])}")
    
    # View specific packet
    packet = data['packets'][0]
    print(f"Packet time: {packet['time']}")
"""

from .reader import RDEFReader
from .gui import RDEFGUI
from .utils import parse_rdef_header, validate_rdef_file, hex_dump

__version__ = "1.0.0"
__all__ = ["RDEFReader", "RDEFGUI", "parse_rdef_header", "validate_rdef_file", "hex_dump"]
