import json
import os
import platform
import socket
import subprocess
import psutil
import shlex
import xml.etree.ElementTree as ET
import glob
import gzip
import re
import shutil


def get_hostname():
    return socket.gethostname()

def get_os_info():
    return platform.platform()

def get_listening_ports_details():
    print("Interrogating listening ports...")
    listening_ports = []
    for conn in psutil.net_connections(kind='tcp'):
        if conn.status == 'LISTEN':
            try:
                if any(port['port'] == conn.laddr.port for port in listening_ports):
                    continue  # Skip if port already recorded
                process = psutil.Process(conn.pid)
                listening_ports.append({
                    'port': conn.laddr.port,
                    'address': conn.laddr.ip,
                    'pid': conn.pid,
                    'process_name': process.name()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                if any(port['port'] == conn.laddr.port for port in listening_ports):
                    continue  # Skip if port already recorded
                listening_ports.append({
                    'port': conn.laddr.port,
                    'address': conn.laddr.ip,
                    'pid': conn.pid,
                    'process_name': 'Unknown/Restricted'
                })
    listening_ports.sort(key=lambda x: x['port'])
    return listening_ports

def advanced_port_scan(target_ip, options=""):
    # It's recommended to use shlex.split() to correctly parse the command string into a list.
    command_string = f"nmap {options} {target_ip}"
    command_list = shlex.split(command_string)
    
    try:
        # subprocess.run is the recommended approach for most use cases in Python 3.
        result = subprocess.run(
            command_list,
            capture_output=True,  # Captures stdout and stderr
            text=True,            # Decodes output as text (str) instead of bytes
            check=True            # Raises a CalledProcessError if the command fails
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"
    except FileNotFoundError:
        return "Error: nmap executable not found. Make sure nmap is installed and in your system's PATH."


def xml_element_to_dict(element):
    """Recursively convert XML element to dictionary."""
    result = {}
    # Add attributes
    if element.attrib:
        result['@attributes'] = dict(element.attrib)
    # Add text if present
    if element.text and element.text.strip():
        result['#text'] = element.text.strip()
    # Add children
    for child in element:
        child_data = xml_element_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    return result

def xml_to_json(xml_string):
    """Convert XML string to JSON format for ports."""
    root = ET.fromstring(xml_string)
    ports_element = root.find('.//ports')
    if ports_element is not None:
        ports_dict = xml_element_to_dict(ports_element)
        if 'extraports' in ports_dict:
            del ports_dict['extraports']
        nmap_ports_list = ports_dict.get('port', [])
    else:
        nmap_ports_list = []
    
    # Transform to flat format
    transformed_ports = []
    for port in nmap_ports_list:
        new_port = {}
        attrs = port.get('@attributes', {})
        new_port['protocol'] = attrs.get('protocol')
        new_port['portid'] = attrs.get('portid')
        state_attrs = port.get('state', {}).get('@attributes', {})
        new_port['state'] = state_attrs.get('state')
        service_attrs = port.get('service', {}).get('@attributes', {})
        new_port['name'] = service_attrs.get('name')
        new_port['product'] = service_attrs.get('product')
        new_port['version'] = service_attrs.get('version')
        
        # Parse vulnerabilities from script
        vulnerabilities = []
        script = port.get('script', {})
        scripts = [script] if isinstance(script, dict) else script if isinstance(script, list) else []
        for s in scripts:
            if isinstance(s, dict):
                script_attrs = s.get('@attributes', {})
                output = script_attrs.get('output', '')
                if not output and 'table' in s:
                    table = s['table']
                    if isinstance(table, dict) and '#text' in table:
                        output = table['#text']
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if '\t' in line:
                            parts = [p.strip() for p in line.split('\t') if p.strip()]
                            if len(parts) >= 3:
                                vuln_id = parts[0]
                                cvss_str = parts[1]
                                url = parts[2]
                                if vuln_id.startswith('CVE-'):
                                    try:
                                        cvss = float(cvss_str)
                                        if cvss >= 5.0:
                                            vulnerabilities.append({
                                                'id': vuln_id,
                                                'cvss_score': cvss,
                                                'references': [url]
                                            })
                                    except ValueError:
                                        pass
        new_port['vulnerabilities'] = vulnerabilities
        transformed_ports.append(new_port)
    
    return transformed_ports


def get_installed_software_windows():
    # TODO: Will this run on legacy Windows machines? Need to test on Windows 7/8/8.1.
    process = subprocess.run(
            [
                "powershell", "-Command", 
                'Get-ItemProperty -Path HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*', 
                '| Where-Object { $_.DisplayName -ne $null } | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | ConvertTo-Json'
            ],
            capture_output=True,
            text=True,
            check=True,
            shell=True # Use shell=True for cleaner execution
        )

    # The output is a JSON string in stdout
    json_output = process.stdout
    
    # Load the JSON string into a Python dictionary
    data = json.loads(json_output)
    return data

def get_installed_software_windows_legacy():
    # TODO: untested. Need to test on a legacy windows machine. This is for Windows 7/8/8.1.
    try:
        output = subprocess.check_output(["wmic", "product", "get", "name,version"], text=True)
        # Split the output into lines and filter out empty ones
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip():
                print(line.strip())
    except Exception as e:
        print(f"An error occurred: {e}")

    return []

def get_installed_software_linux():
    """Retrieve installed software on Linux systems."""
    # TODO: Implement Linux software retrieval
    return []


def get_installed_software(os_info):
    print("Retrieving installed software...")
    if "Windows-10" in os_info or "Windows-11" in os_info:
        return get_installed_software_windows()
    elif "Windows" in os_info:
        return get_installed_software_windows_legacy()
    elif "Linux" in os_info:
        return get_installed_software_linux()
    else:
        print("Unsupported operating system for software retrieval.")
        return []

def build_inventory_as_json(hostname, os_info, open_ports, nmap_ports, installed_software):
    inventory = {
        "hostname": hostname,
        "os_info": os_info,
        "open_ports": open_ports,
        "nmap_ports": nmap_ports,
        "installed_software": installed_software
    }
    return json.dumps(inventory, indent=4)    

def save_inventory_to_json(inventory, filename):
    with open(os.path.join("asset_data", filename), "w") as f:
        f.write(inventory)

def main():
    print("Collecting system information...")

    # Collect Hostname and OS Information
    hostname = get_hostname()
    os_info = get_os_info()
    print(f"Hostname: {hostname}")
    print(f"Operating System: {os_info}")

    # Basic Open Port Scan
    open_ports = get_listening_ports_details()

    # Advanced Nmap Scan
    target = '127.0.0.1' # Localhost. Do Not Change. This is for nmap script scanning of local services.
    output_path = "nmap_output.xml"
    scan_options = f'-sV -oX {output_path} --script vulners --script-args mincvss=5.0'
    advanced_port_scan(target, options=scan_options)

    with open(output_path, 'r') as f:
            xml_data = f.read()
    nmap_ports_list = xml_to_json(xml_data)

    # Installed Software Scan
    installed_software = get_installed_software(os_info)

    # Build inventory and save to JSON
    inventory = build_inventory_as_json(hostname, os_info, open_ports, nmap_ports_list, installed_software)
    save_inventory_to_json(inventory, f"inventory_{hostname}.json")
    print(f"Asset Collection Complete: Inventory saved to inventory_{hostname}.json")


if __name__ == "__main__":
    main()