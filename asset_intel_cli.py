import argparse
from asset_manager import AssetManager

def asset_mgr() -> AssetManager:
    print("Initializing Inventory Manager.")
    return AssetManager()


def list_assets(args) -> None:
    print("Listing all assets items.")



def filter_by_os(args) -> None:
    print(f"Filtering assets by operating system: {args.os}")


def list_risky_hosts(args) -> None:
    print("Listing hosts with risky software.")



def main():
    parser = argparse.ArgumentParser(description='Asset Intelligence CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    p_list = subparsers.add_parser('list', help='List all asset items')
    p_list.add_argument('--file_path', '-f', help='Path to the JSON file or directory containing asset data')
    p_list.set_defaults(func=list_assets)
    
    p_filter_os = subparsers.add_parser('filter-os', help='Filter assets by operating system')
    p_filter_os.add_argument('--file_path', '-f', help='Path to the JSON file or directory containing asset data')
    p_filter_os.add_argument('--os', '-o', help='Operating system to filter by')
    p_filter_os.set_defaults(func=filter_by_os)

    p_risky_hosts = subparsers.add_parser('risky-hosts', help='List hosts with risky software')
    p_risky_hosts.add_argument('--file_path', '-f', help='Path to the JSON file or directory containing asset data')
    p_risky_hosts.set_defaults(func=list_risky_hosts)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()