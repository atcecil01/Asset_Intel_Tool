import json
import platform
import socket
import subprocess
import psutil

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

def build_inventory_as_json(hostname, os_info, open_ports, installed_software):
    inventory = {
        "hostname": hostname,
        "os_info": os_info,
        "open_ports": open_ports,
        "installed_software": installed_software
    }
    return json.dumps(inventory, indent=4)    

def save_inventory_to_json(inventory, filename):
    with open(filename, "w") as f:
        f.write(inventory)

def main():
    print("Collecting system information...")
    hostname = get_hostname()
    os_info = get_os_info()
    print(f"Hostname: {hostname}")
    print(f"Operating System: {os_info}")

    open_ports = get_listening_ports_details()

    installed_software = get_installed_software(os_info)
    inventory = build_inventory_as_json(hostname, os_info, open_ports, installed_software)
    save_inventory_to_json(inventory, "inventory.json")


if __name__ == "__main__":
    main()