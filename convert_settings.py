#!/usr/bin/env python3
"""
JSON to TOML Converter for NWN:EE Settings

This script converts the intermediary settings.json file to settings.tml
for use by the NWN:EE server. It handles nested JSON structures and preserves
data types appropriately for TOML format.
"""

import json
import sys
import os

def to_toml(data):
    """
    Convert a nested dict to TOML string.
    """
    lines = []
    tables = {}
    
    def flatten(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    flatten(value, current_path)
                else:
                    table_path = ".".join(current_path.split(".")[:-1])
                    key_name = current_path.split(".")[-1]
                    if table_path not in tables:
                        tables[table_path] = {}
                    tables[table_path][key_name] = value
        else:
            # Root level value
            if "" not in tables:
                tables[""] = {}
            tables[""][path] = obj
    
    flatten(data)
    
    for table in sorted(tables.keys()):
        if table:
            lines.append(f"[{table}]")
        for key, value in tables[table].items():
            lines.append(f"{key} = {repr(value)}")
        lines.append("")  # Blank line between sections
    
    return "\n".join(lines).strip()

def convert_json_to_toml(json_file, toml_file):
    """
    Convert JSON file to TOML file.

    Args:
        json_file (str): Path to the input JSON file
        toml_file (str): Path to the output TOML file
    """
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to TOML
        toml_data = to_toml(data)

        # Write TOML file
        with open(toml_file, 'w', encoding='utf-8') as f:
            f.write(toml_data)

        print(f"Successfully converted {json_file} to {toml_file}")
        return True

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"Error: Conversion failed - {e}")
        return False

def main():
    # Default paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'user', 'settings.json')
    toml_file = os.path.join(script_dir, 'user', 'settings.tml')

    # Allow command line arguments for custom paths
    if len(sys.argv) >= 3:
        json_file = sys.argv[1]
        toml_file = sys.argv[2]

    success = convert_json_to_toml(json_file, toml_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

