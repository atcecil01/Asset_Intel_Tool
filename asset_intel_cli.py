import argparse
import os
from tabulate import tabulate
from asset_manager import AssetManager

def asset_mgr() -> AssetManager:
    return AssetManager()


def list_assets(args) -> None:
    mgr = asset_mgr()
    mgr.add_assets(args.file_path)
    mgr.list_assets()
    
    print(tabulate([[asset.hostname, asset.os_info, len(asset.open_ports), len(asset.installed_software)] for asset in mgr.assets], headers=["Hostname", "OS Info", "Open Ports", "Software Count"]))
    print()


def filter_by_os(args) -> None:
    mgr = asset_mgr()
    mgr.add_assets(args.file_path)
    filtered_assets = [asset for asset in mgr.assets if args.os.lower() in asset.os_info.lower()]
    
    print(tabulate([[asset.hostname, asset.os_info, len(asset.open_ports), len(asset.installed_software)] for asset in filtered_assets], headers=["Hostname", "OS Info", "Open Ports", "Software Count"]))
    print()


def list_risky_hosts(args) -> None:
    mgr = asset_mgr()
    mgr.add_assets(args.file_path)
    risky_assets = mgr.risky_hosts(advanced=args.advanced)
    
    if args.advanced:
        print("Advanced Risk Assessment:")
        print(tabulate([[asset.hostname, asset.risk_score, ", ".join(asset.risk_notes)] for asset in (risky_assets if isinstance(risky_assets, list) else [])], headers=["Hostname", "Risk Score", "Risk Notes"]))
    else:
        print("Basic Risk Assessment:")
        print(tabulate([[asset.hostname, asset.risk_score, ", ".join(asset.risk_notes)] for asset in (risky_assets if isinstance(risky_assets, list) else [])], headers=["Hostname", "Risk Score", "Risk Notes"]))
    print()



def main():
    parser = argparse.ArgumentParser(description='Asset Intelligence CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    print() # Initial newline for better console formatting
    print("--------------------------------------")
    print("-------Asset Intelligence Tool--------")
    print("--------------------------------------")
    print()

    p_list = subparsers.add_parser('list', help='List all asset items')
    p_list.add_argument('--file_path', '-f', default=os.path.join(os.getcwd(), "asset_data"), help='Path to the JSON file or directory containing asset data')
    p_list.set_defaults(func=list_assets)
    
    p_filter_os = subparsers.add_parser('filter-os', help='Filter assets by operating system')
    p_filter_os.add_argument('--file_path', '-f', default=os.path.join(os.getcwd(), "asset_data"), help='Path to the JSON file or directory containing asset data')
    p_filter_os.add_argument('--os', '-o', help='Operating system to filter by')
    p_filter_os.set_defaults(func=filter_by_os)

    p_risky_hosts = subparsers.add_parser('risky-hosts', help='List hosts with risky software')
    p_risky_hosts.add_argument('--file_path', '-f', default=os.path.join(os.getcwd(), "asset_data"), help='Path to the JSON file or directory containing asset data')
    p_risky_hosts.add_argument('--advanced', '-a', action='store_true', help='Use advanced risk assessment criteria', default=False)
    p_risky_hosts.set_defaults(func=list_risky_hosts)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()