"""
Packet Data Explanation

This script explains what the telemetry parser is finding in your RDEF packet data.
"""

import struct
import datetime

def explain_packet_interpretation():
    """
    Explain what the telemetry parser found in Packet #1
    """
    
    # Your raw packet data (first 32 bytes for analysis)
    raw_hex = "00f57fc3d726ddc0001346772f3d0016003c0e0c3a1707211e22005607297900"
    raw_bytes = bytes.fromhex(raw_hex)
    
    print("NASA RDEF Packet #1 - Data Interpretation Explained")
    print("=" * 60)
    print(f"Raw hex: {raw_hex}")
    print()
    
    print("🔍 WHAT THE PARSER IS DOING:")
    print("-" * 30)
    print()
    
    # Byte 0-3: 00f57fc3
    chunk1 = raw_bytes[0:4]
    uint32_le = struct.unpack('<I', chunk1)[0]
    uint32_be = struct.unpack('>I', chunk1)[0]
    
    print("Bytes 0-3: 00f57fc3")
    print(f"  → As 32-bit unsigned (Little Endian): {uint32_le}")
    print(f"  → As 32-bit unsigned (Big Endian): {uint32_be}")
    print(f"  → As Unix timestamp (LE): {datetime.datetime.fromtimestamp(uint32_le).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  → As Unix timestamp (BE): {datetime.datetime.fromtimestamp(uint32_be).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("  → This is likely a spacecraft timestamp!")
    print()
    
    # Bytes 4-7: d726ddc0
    chunk2 = raw_bytes[4:8]
    uint32_le_2 = struct.unpack('<I', chunk2)[0]
    uint32_be_2 = struct.unpack('>I', chunk2)[0]
    
    print("Bytes 4-7: d726ddc0")
    print(f"  → As 32-bit unsigned (Little Endian): {uint32_le_2}")
    print(f"  → As 32-bit unsigned (Big Endian): {uint32_be_2}")
    print(f"  → As Unix timestamp (LE): {datetime.datetime.fromtimestamp(uint32_le_2).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  → As Unix timestamp (BE): {datetime.datetime.fromtimestamp(uint32_be_2).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("  → This is the second timestamp or related time data!")
    print()
    
    # Bytes 8-11: 00134677
    chunk3 = raw_bytes[8:12]
    uint32_le_3 = struct.unpack('<I', chunk3)[0]
    uint32_be_3 = struct.unpack('>I', chunk3)[0]
    float_le = struct.unpack('<f', chunk3)[0]
    float_be = struct.unpack('>f', chunk3)[0]
    
    print("Bytes 8-11: 00134677")
    print(f"  → As 32-bit unsigned (Little Endian): {uint32_le_3}")
    print(f"  → As 32-bit unsigned (Big Endian): {uint32_be_3}")
    print(f"  → As 32-bit float (Little Endian): {float_le:.6f}")
    print(f"  → As 32-bit float (Big Endian): {float_be:.6f}")
    print("  → This could be a sensor reading or telemetry value!")
    print()
    
    # Show 16-bit breakdown
    print("📊 16-BIT SENSOR VALUES (from first 16 bytes):")
    print("-" * 40)
    for i in range(0, 16, 2):
        chunk = raw_bytes[i:i+2]
        val = struct.unpack('<H', chunk)[0]
        print(f"  Bytes {i}-{i+1}: {chunk.hex()} → {val}")
    print()
    
    # ASCII strings
    print("🔤 ASCII STRINGS FOUND:")
    print("-" * 20)
    ascii_strings = []
    current_string = ""
    
    for byte in raw_bytes:
        if 32 <= byte <= 126:  # Printable ASCII
            current_string += chr(byte)
        else:
            if len(current_string) >= 3:
                ascii_strings.append(current_string)
            current_string = ""
    
    if current_string and len(current_string) >= 3:
        ascii_strings.append(current_string)
    
    for i, s in enumerate(ascii_strings, 1):
        print(f"  String {i}: '{s}'")
    print()
    
    print("🤔 WHAT THIS MEANS:")
    print("-" * 20)
    print("• The parser tries EVERY possible interpretation of the binary data")
    print("• It doesn't know the 'correct' format - it shows ALL options")
    print("• You (the analyst) determine which interpretation makes sense")
    print()
    print("• Timestamps around 2006-2073 could be:")
    print("  - Spacecraft mission time")
    print("  - Data collection timestamps")
    print("  - System boot time")
    print()
    print("• The float value -6.91 could be:")
    print("  - Sensor reading (temperature, voltage, etc.)")
    print("  - Engineering parameter")
    print("  - Just random binary data!")
    print()
    print("• ASCII 'Fw/=' might be:")
    print("  - Part of a protocol header")
    print("  - Compressed/encoded data")
    print("  - Checksum or identifier")
    print()
    
    print("💡 TO UNDERSTAND YOUR DATA:")
    print("-" * 30)
    print("1. Check the spacecraft mission documentation")
    print("2. Look for RDEF packet format specifications")
    print("3. Compare multiple packets to find patterns")
    print("4. Cross-reference with mission timelines")
    print("5. The 'correct' interpretation depends on the spacecraft's data format!")

if __name__ == "__main__":
    explain_packet_interpretation()
