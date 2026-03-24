import json
import platform
import socket
import subprocess
import time
import threading
import concurrent.futures


def get_hostname():
    return socket.gethostname()


def get_os_info():
    return platform.platform()

def _is_port_open(host: str, port: int, timeout: float) -> bool:
    """Return True if the TCP port is open on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0

def get_open_ports(host: str = "127.0.0.1", ports=None, timeout: float = 0.1, max_workers: int = 100):
    print("Collecting open ports...")
    if ports is None:
        ports = range(1, 65536)

    total_ports = len(ports)
    scanned = [0]  # mutable counter for cross-thread updates
    scanned_lock = threading.Lock()
    done = threading.Event()
    open_ports = []

    def _print_progress():
        while not done.wait(10):
            with scanned_lock:
                count = scanned[0]
            print(f"Scanned {count}/{total_ports} ports...")

    progress_thread = threading.Thread(target=_print_progress, daemon=True)
    progress_thread.start()

    start = time.perf_counter()

    # Avoid creating more threads than there are ports.
    max_workers = min(max_workers, total_ports)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_is_port_open, host, port, timeout): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            try:
                is_open = future.result()
            except Exception:
                is_open = False
            finally:
                with scanned_lock:
                    scanned[0] += 1

            if is_open:
                open_ports.append(port)

    done.set()
    progress_thread.join(timeout=0.1)

    end = time.perf_counter()
    print(f"Scanned {scanned[0]}/{total_ports} ports in {end - start:.1f}s")
    open_ports.sort()
    return open_ports

def get_open_ports_details(ports, host: str = "127.0.0.1"):
    print("Interrogating port details...")
    port_details = {}
    for port in ports:
        print(f"Checking details for port {port}...")
        try:
            # Create a new socket and set a timeout to avoid hanging indefinitely
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1) 
            
            # Attempt to connect
            result = s.connect_ex((host, port))
            
            if result == 0:
                try:
                    # Get the service name associated with the port
                    service_name = socket.getservbyport(port, 'tcp')
                    print(f"Port {port} is OPEN. Service: {service_name}")
                except OSError:
                    print(f"Port {port} is OPEN. Service: Unknown")
            else:
                print(f"Port {port} is CLOSED or FILTERED (Error code: {result})")

        except socket.error as e:
            return f"Error: {e}"
        finally:
            s.close() # Ensure the socket is closed





def get_installed_software_windows():
    # TODO: Will this run on legacy Windows machines? Need to test on Windows 7/8/8.1.
    process = subprocess.run(
            [
                "powershell", "-Command", 
                'Get-ItemProperty -Path HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*', 
                '| Where-Object { $_.DisplayName -ne $null } | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | ConvertTo-Json'
                # '> "installed.txt"'
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

    # TODO: Uncomment before final release. For testing, we want to avoid the long runtime of scanning all ports.
    open_ports = get_open_ports()
    get_open_ports_details(open_ports)

    installed_software = get_installed_software(os_info)
    inventory = build_inventory_as_json(hostname, os_info, open_ports, installed_software)
    save_inventory_to_json(inventory, "inventory.json")





if __name__ == "__main__":
    main()