"""
Utility functions for RDEF file processing
"""

import logging
from typing import Dict, Any, Optional
import struct

logger = logging.getLogger(__name__)


def parse_rdef_header(header_text: str) -> Dict[str, Any]:
    """
    Parse RDEF file header from text.
    
    Args:
        header_text (str): Header text from RDEF file
        
    Returns:
        Dict containing parsed metadata
    """
    metadata = {}
    
    for line in header_text.split('\n'):
        line = line.strip()
        if not line or line == 'END':
            continue
            
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Convert numeric values
            if key in ['NUM_PACK']:
                try:
                    value = int(value)
                except ValueError:
                    logger.warning(f"Could not convert {key} to int: {value}")
            
            metadata[key] = value
    
    return metadata


def validate_rdef_file(filepath: str) -> bool:
    """
    Basic validation of RDEF file format.
    
    Args:
        filepath (str): Path to file to validate
        
    Returns:
        bool: True if file appears to be valid RDEF format
    """
    try:
        with open(filepath, 'rb') as f:
            # Read first few bytes to check for ASCII header
            header_start = f.read(500).decode('ascii', errors='ignore')
            
            # Check for RDEF signature patterns (more flexible)
            required_patterns = ['DATATYPE=', 'FILENAME=', 'END']
            optional_patterns = ['APID=', 'NUM_PACK=']
            
            # Check if we have ASCII header format
            has_ascii_header = any(pattern in header_start for pattern in required_patterns)
            
            if has_ascii_header:
                # Check required patterns
                for pattern in required_patterns:
                    if pattern not in header_start:
                        logger.warning(f"Missing expected pattern '{pattern}' in header")
                        return False
                
                # Check for at least one optional pattern to confirm it's telemetry data
                has_optional = any(pattern in header_start for pattern in optional_patterns)
                if not has_optional:
                    logger.warning("No telemetry-specific patterns found in header")
                    return False
            else:
                # Check if it's a binary format (like SDU files)
                # Look for common telemetry patterns in binary data
                binary_start = f.read(1000)
                if len(binary_start) < 100:
                    logger.warning("File too small to be valid RDEF")
                    return False
                
                # Check for reasonable binary structure
                # (This is a basic check - could be enhanced)
                null_bytes = binary_start.count(b'\x00')
                if null_bytes > len(binary_start) * 0.8:
                    logger.warning("File appears to be mostly null bytes")
                    return False
            
            return True
            
    except Exception as e:
        logger.error(f"Error validating file {filepath}: {e}")
        return False


def format_packet_summary(packet: Dict[str, Any]) -> str:
    """
    Create a formatted summary of a packet.
    
    Args:
        packet (Dict[str, Any]): Packet data
        
    Returns:
        str: Formatted summary string
    """
    summary = []
    
    if 'data_offset' in packet:
        summary.append(f"Offset: {packet['data_offset']}")
    
    if 'raw_header' in packet:
        header = packet['raw_header']
        summary.append(f"Header: {header[:16]}{'...' if len(header) > 16 else ''}")
    
    if 'timestamp' in packet:
        summary.append(f"Time: {packet['timestamp']}")
    
    return " | ".join(summary)


def hex_dump(data: bytes, width: int = 16) -> str:
    """
    Create a hex dump of binary data.
    
    Args:
        data (bytes): Binary data to dump
        width (int): Number of bytes per line
        
    Returns:
        str: Formatted hex dump
    """
    result = []
    
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        
        result.append(f"{i:08x}: {hex_part:<{width*3}} |{ascii_part}|")
    
    return "\n".join(result)


def extract_telemetry_values(packet_data: bytes) -> Dict[str, Any]:
    """
    Extract telemetry values from packet data.
    
    This is a basic implementation that can be extended for specific telemetry formats.
    
    Args:
        packet_data (bytes): Raw packet data
        
    Returns:
        Dict containing extracted telemetry values
    """
    values = {}
    
    # Basic structure analysis
    if len(packet_data) >= 4:
        # Try to extract common telemetry patterns
        try:
            # 32-bit unsigned integer
            if len(packet_data) >= 4:
                values['uint32_0'] = struct.unpack('<I', packet_data[0:4])[0]
            
            # 16-bit unsigned integers
            if len(packet_data) >= 8:
                values['uint16_0'] = struct.unpack('<H', packet_data[4:6])[0]
                values['uint16_1'] = struct.unpack('<H', packet_data[6:8])[0]
            
            # 32-bit float
            if len(packet_data) >= 12:
                values['float32_0'] = struct.unpack('<f', packet_data[8:12])[0]
                
        except struct.error as e:
            logger.debug(f"Error unpacking telemetry values: {e}")
    
    return values


def create_packet_filter(packets: list, **filters) -> list:
    """
    Filter packets based on criteria.
    
    Args:
        packets (list): List of packet dictionaries
        **filters: Filter criteria
        
    Returns:
        list: Filtered packets
    """
    filtered = []
    
    for packet in packets:
        match = True
        
        for key, value in filters.items():
            if key not in packet:
                match = False
                break
            
            if packet[key] != value:
                match = False
                break
        
        if match:
            filtered.append(packet)
    
    return filtered
