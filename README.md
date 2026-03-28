# Asset Intelligence Tool

A command-line tool for managing and analyzing asset data from JSON files. This tool allows you to list assets, filter them by operating system, and identify risky hosts based on various criteria.

## Features

- **List Assets**: Display all assets with hostname, OS info, open ports count, and software count.
- **Filter by OS**: Filter assets based on the operating system.
- **Risk Assessment**: Identify hosts with risky configurations, such as high number of open ports, specific risky ports (e.g., 3389, 22, 445), and excessive installed software.
- **Advanced Risk Assessment**: (Planned) More sophisticated risk analysis based on software vulnerabilities and other factors.

## Configuration

The tool uses a `config.json` file to define high-risk ports and their associated risk scores. The default configuration includes:

```json
{
  "high_risk_ports": {
    "3389": 3,
    "22": 3,
    "445": 2
  }
}
```

You can modify this file to add or remove ports and adjust risk scores as needed.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Asset_Intel_Tool
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The tool is run via the command line with various subcommands.

### Collection Tool

```
python collector.py
```

### List All Assets

```
python asset_intel_cli.py list --file_path /path/to/json/files
```

If `--file_path` is a directory, it will process all JSON files in that directory. Defaults to the asset_data subfolder in the current directory.

### Filter Assets by OS

```
python asset_intel_cli.py filter-os --file_path /path/to/json/files --os "Windows"
```

### List Risky Hosts

```
python asset_intel_cli.py risky-hosts --file_path /path/to/json/files
```

Use `--advanced` for advanced risk assessment (currently not implemented).

## JSON File Format

The built in collector tool will automatically collect and format data on an asset machine. 

The tool expects JSON files with the following structure:

```json
{
  "hostname": "example-host",
  "os_info": "Windows 10",
  "open_ports": [
    {
      "port": 80,
      "address": "0.0.0.0",
      "pid": 1234,
      "process_name": "httpd"
    }
  ],
  "installed_software": [
    {
      "DisplayName": "Software Name",
      "DisplayVersion": "1.0.0",
      "Publisher": "Publisher Name",
      "InstallDate": "2023-01-01"
    }
  ]
}
```

## Requirements

- Python 3.6+
- tabulate (for table formatting)
