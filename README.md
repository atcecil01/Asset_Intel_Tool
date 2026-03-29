# Asset Intelligence Tool

A command-line tool for managing and analyzing asset data from JSON files. This tool allows you to list assets, filter them by operating system, and identify risky hosts based on various criteria.

## Features

- **List Assets**: Display all assets with hostname, OS info, open ports count, and software count.
- **Filter by OS**: Filter assets based on the operating system.
- **Risk Assessment**: Identify hosts with risky configurations, such as high number of open ports, specific risky ports (e.g., 3389, 22, 445), and excessive installed software.
- **Advanced Risk Assessment**: (Planned) More sophisticated risk analysis based on software vulnerabilities and other factors.

## Configuration

The tool uses a `config.json` file to define high-risk ports and their associated risk scores, risk thresholds, and risk score intervals. These values can be modified locally as needed.

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

## Risk Scoring Logic

Basic risk scoring logic looks at the number of open ports, number of installed software, and any known high-risk ports. Each asset will accumulate a risk score based on these factors. The thresholds for each risk factor, and the list of high-risk ports, are customizable in the `config.json` file.

Advanced risk assessment logic (not implemented) will also consider additional risk factors such as last updated dates, and whether any known vulnerabilities exist for an installed software/open port.

## Limitations

- The tool is currently only tested on Windows 10/11. Future versions will contain support for legacy versions of Windows, and Linux systems.
- Advanced risk assessment is under development, and unavailable at this time.  

## Requirements

- Python 3.6+
- tabulate (for table formatting)
