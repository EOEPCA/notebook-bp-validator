import argparse
import sys
import json

from nb_validator import validate_notebooks

def main():
    parser = argparse.ArgumentParser(
        description="Validate Jupyter notebooks metadata against a JSON schema."
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Paths to .ipynb files to validate.",
    )

    parser.add_argument(
        "-s",
        "--schema",
        required=True,
        # choices=["schema.org", "eumetsat"],
        help="Supported values: 'eumetsat' or 'schema.org'."
    )

    parser.add_argument(
        "-p",
        "--abspath",
        action="store_true",
        help="Uses absolute paths in output.",
    )

    args = parser.parse_args()

    try:
        print(json.dumps(validate_notebooks(args.files, args.schema, args.abspath), indent=4))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
