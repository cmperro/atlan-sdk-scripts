#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pyatlan.client.atlan import AtlanClient
from pyatlan.client.atlan import AtlanTypeCategory
from pyatlan.errors import NotFoundError
from pyatlan.model.typedef import EnumDef

def load_json_from_file(file_path):
    """
    Validates the file path and loads JSON data from the file.

    Args:
        file_path (str): The path to the JSON file provided as input.

    Returns:
        dict or list: The loaded data from the JSON file.
                      Exits the program if validation or loading fails.
    """
    # --- Validation 1: Check if the file path exists ---
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at '{file_path}'", file=sys.stderr)
        sys.exit(1) # Exit with a non-zero status code indicates error

    # --- Validation 2: Check if it's actually a file (not a directory) ---
    if not os.path.isfile(file_path):
        print(f"Error: Input path '{file_path}' is a directory, not a file.", file=sys.stderr)
        sys.exit(1)

    # --- Validation 3: Check if the file has a .json extension ---
    # This is a basic check; the content is the real test.
    if not file_path.lower().endswith('.json'):
        print(f"Warning: Input file '{file_path}' does not have a .json extension.", file=sys.stderr)
        # Decide if you want to exit or just warn. Let's continue but warn.
        # If strict checking is needed, uncomment the next line:
        # sys.exit(1)

    # --- Load the JSON data ---
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Load JSON data from the file object
            data = json.load(f)
        print(f"Successfully loaded JSON data from '{file_path}'.")
        return data
    except json.JSONDecodeError as e:
        # Handle errors if the file content is not valid JSON
        print(f"Error: Failed to decode JSON from '{file_path}'. Invalid JSON format.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        # Handle errors like permission denied
        print(f"Error: Could not read file '{file_path}'. Check permissions.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during file loading
        print(f"An unexpected error occurred during file loading: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Main function to parse arguments and orchestrate the loading.
    """
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Load and validate a JSON file provided as a command-line argument."
    )

    # Add one positional argument for the input JSON file path
    parser.add_argument(
        "input_json_file", # The name used to access the argument later (e.g., args.input_json_file)
        metavar="INPUT_JSON_FILE", # How the argument is displayed in help messages
        type=str,          # The expected type of the argument
        help="The path to the input JSON file." # Help text description
    )

    # Parse the arguments provided via the command line
    args = parser.parse_args()

    # Get the file path from the parsed arguments
    json_file_path = args.input_json_file

    # Load the data using our validation function
    loaded_data = load_json_from_file(json_file_path)

    # --- Use the loaded_data variable here ---
    # At this point, 'loaded_data' holds the Python dictionary or list
    # parsed from the JSON file. You can now work with it.

    print("\n--- Data Usage Example ---")
    print(f"The loaded data is of type: {type(loaded_data)}")

    # Example: Print keys if it's a dictionary
    if isinstance(loaded_data, dict):
        print(f"Top-level keys found: {list(loaded_data.keys())}")
    # Example: Print length if it's a list
    elif isinstance(loaded_data, list):
        print(f"Number of items in the list: {len(loaded_data)}")


    client = AtlanClient(
        base_url="",
        api_key=""
    )

    for item in loaded_data:
        #Check if exists
        try:
            num_def = client.typedef.get_by_name(item.get("name"))
        except NotFoundError:
            num_def = None
        
        if num_def:
            #We need to update
            print("Updating " + num_def.name)
            enum_def = EnumDef.update(
                name=item.get("name"),
                values=item.get("values"),
                replace_existing=True 
            )
            response = client.typedef.update(enum_def)
        else:
            #We need to create
            print("Creating " + item.get("name"))
            enum_def = EnumDef.create(
                name=item.get("name"),
                values=item.get("values")
            )
            response = client.typedef.create(enum_def)

    print("\nScript finished successfully.")


# Standard Python entry point check
if __name__ == "__main__":
    main()
