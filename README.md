# NASA RDEF File Reader

A Python tool for reading and viewing legacy NASA RDEF (Relational Data Exchange Format) telemetry files. These files are binary format used by NASA Goddard Space Flight Center for ground-system telemetry processing.

## Features

- **Easy to Use**: Simple Python API for reading RDEF files
- **GUI Application**: Clean, intuitive graphical interface for viewing files
- **Importable**: Can be imported as a Python module for use in other projects
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Uses only Python standard library
- **LASCO SOHO Decoding**: NASA-specific decoding for LASCO coronagraph data
  - CCSDS packet header parsing
  - Housekeeping parameter extraction (voltages, temperatures, status)
  - Science data decoding (image metadata, compression info)
  - Compressed data analysis
  - Human-readable unit conversions

## Installation

### From Source

```bash
git clone <repository-url>
cd nasa-rdef-reader
pip install -e .
```

### As a Module

You can also use this tool directly by copying the `nasa_rdef_reader` directory to your project.

## Usage

### Command Line (GUI)

```bash
python -m nasa_rdef_reader.gui
# or if installed
rdef-viewer
```

### Python API

```python
from nasa_rdef_reader import RDEFReader

# Read a file
reader = RDEFReader("SVMHK1_251204_120317.REL")
data = reader.read()

# Access metadata
print(f"File type: {data['metadata']['datatype']}")
print(f"APID: {data['metadata']['apid']}")
print(f"Number of packets: {len(data['packets'])}")

# Access packets
for i, packet in enumerate(data['packets'][:5]):  # Show first 5 packets
    print(f"Packet {i+1}: Offset={packet['data_offset']}")
```

### Import in Other Projects

```python
from nasa_rdef_reader import read_rdef_file

# Quick file reading
data = read_rdef_file("your_file.REL")
```

## File Format Support

This tool supports:
- `.REL` files (Real-time telemetry)
- `.SDU` files (Space Data Unit files)
- ASCII header with binary data sections
- Various telemetry packet formats

## GUI Interface

The GUI provides:
- File browser for easy file selection
- Metadata display showing file information
- Packet list with searchable/filterable view
- Detailed packet inspection
- Thread-safe file loading (non-blocking UI)

## Project Structure

```
startool-rdef-reader/
├── nasa_rdef_reader/          # Core package
│   ├── __init__.py           # Package exports
│   ├── reader.py             # RDEF file reading
│   ├── gui.py                # GUI application
│   └── utils.py              # Utility functions
├── launch_gui.py             # GUI entry point
├── setup.py                  # Package installation
├── README.md                 # Documentation
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contributor guidelines
├── CODE_OF_CONDUCT.md        # Community standards
└── .gitignore               # Python project exclusions
```

## Requirements

- Python 3.7 or higher
- No external dependencies required

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/startool-rdef-reader.git
cd startool-rdef-reader

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Examples

```bash
# Launch the GUI
python launch_gui.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

This tool is designed to work with legacy NASA telemetry files. The parsing logic may need to be enhanced for different RDEF file variants or newer formats.

For more information about RDEF format, see the [NASA GSFC documentation](https://umbra.nascom.nasa.gov/pub/tlm_files/).
