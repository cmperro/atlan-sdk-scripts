#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pyatlan.client.atlan import AtlanClient
from pyatlan.client.atlan import AtlanTypeCategory
from pyatlan.errors import NotFoundError
from pyatlan.model.typedef import EnumDef
from pyatlan.model.typedef import AttributeDef, CustomMetadataDef
from pyatlan.model.typedef import _get_all_qualified_names
from pyatlan.model.enums import AtlanCustomAttributePrimitiveType
from pyatlan.model.enums import AtlanIcon
from pyatlan.model.enums import AtlanTagColor
from pyatlan.model.constants import DomainTypes
from typing import Set
from pyatlan.model.constants import (
    AssetTypes,
    DomainTypes,
    EntityTypes,
    GlossaryTypes,
    OtherAssetTypes,
)



def _get_all_qualified_names(asset_type: str) -> Set[str]:
    from pyatlan.client.atlan import AtlanClient
    from pyatlan.model.assets import Asset
    from pyatlan.model.fluent_search import FluentSearch

    client = AtlanClient.get_current_client()
    request = (
        FluentSearch.select()
        .where(Asset.TYPE_NAME.eq(asset_type))
        .include_on_results(Asset.QUALIFIED_NAME)
        .to_request()
    )
    results = client.asset.search(request)
    names = [result.qualified_name or "" for result in results]
    return set(names)


_complete_type_list: AssetTypes = {
    "ADLSAccount",
    "ADLSContainer",
    "ADLSObject",
    "AnaplanPage",
    "AnaplanList",
    "AnaplanLineItem",
    "AnaplanWorkspace",
    "AnaplanModule",
    "AnaplanModel",
    "AnaplanApp",
    "AnaplanDimension",
    "AnaplanView",
    "APIObject",
    "APIQuery",
    "APIField",
    "APIPath",
    "APISpec",
    "Application",
    "ApplicationField",
    "Collection",
    "Query",
    "BIProcess",
    "Badge",
    "Column",
    "ColumnProcess",
    "Connection",
    "CustomEntity",
    "DataStudioAsset",
    "DataverseAttribute",
    "DataverseEntity",
    "Database",
    "DbtColumnProcess",
    "DbtMetric",
    "DbtModel",
    "DbtModelColumn",
    "DbtProcess",
    "DbtSource",
    "Folder",
    "GCSBucket",
    "GCSObject",
    "Insight",
    "KafkaConsumerGroup",
    "KafkaTopic",
    "Process",
    "Link",
    "LookerDashboard",
    "LookerExplore",
    "LookerField",
    "LookerFolder",
    "LookerLook",
    "LookerModel",
    "LookerProject",
    "LookerQuery",
    "LookerTile",
    "LookerView",
    "MCIncident",
    "MCMonitor",
    "MaterialisedView",
    "MetabaseCollection",
    "MetabaseDashboard",
    "MetabaseQuestion",
    "ModeChart",
    "ModeCollection",
    "ModeQuery",
    "ModeReport",
    "ModeWorkspace",
    "PowerBIColumn",
    "PowerBIDashboard",
    "PowerBIDataflow",
    "PowerBIDataset",
    "PowerBIDatasource",
    "PowerBIMeasure",
    "PowerBIPage",
    "PowerBIReport",
    "PowerBITable",
    "PowerBITile",
    "PowerBIWorkspace",
    "PresetChart",
    "PresetDashboard",
    "PresetDataset",
    "PresetWorkspace",
    "Procedure",
    "QlikApp",
    "QlikChart",
    "QlikDataset",
    "QlikSheet",
    "QlikSpace",
    "QlikStream",
    "QuickSightAnalysis",
    "QuickSightAnalysisVisual",
    "QuickSightDashboard",
    "QuickSightDashboardVisual",
    "QuickSightDataset",
    "QuickSightDatasetField",
    "QuickSightFolder",
    "Readme",
    "ReadmeTemplate",
    "RedashDashboard",
    "RedashQuery",
    "RedashVisualization",
    "S3Bucket",
    "S3Object",
    "SalesforceDashboard",
    "SalesforceField",
    "SalesforceObject",
    "SalesforceOrganization",
    "SalesforceReport",
    "Schema",
    "SigmaDataElement",
    "SigmaDataElementField",
    "SigmaDataset",
    "SigmaDatasetColumn",
    "SigmaPage",
    "SigmaWorkbook",
    "SnowflakePipe",
    "SnowflakeStream",
    "SnowflakeTag",
    "SupersetChart",
    "SupersetDashboard",
    "SupersetDataset",
    "Table",
    "TablePartition",
    "TableauCalculatedField",
    "TableauDashboard",
    "TableauDatasource",
    "TableauDatasourceField",
    "TableauFlow",
    "TableauMetric",
    "TableauProject",
    "TableauSite",
    "TableauWorkbook",
    "TableauWorksheet",
    "ThoughtspotAnswer",
    "ThoughtspotDashlet",
    "ThoughtspotLiveboard",
    "View",
}

_all_glossary_types: GlossaryTypes = {
    "AtlasGlossary",
    "AtlasGlossaryCategory",
    "AtlasGlossaryTerm",
}

_all_domains: Set[str] = {"*/super"}

_all_domain_types: DomainTypes = {
    "DataDomain",
    "DataProduct",
}

_all_other_types: OtherAssetTypes = {"File"}


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


    mapping = {
        "Text": AtlanCustomAttributePrimitiveType.STRING,
        "URL": AtlanCustomAttributePrimitiveType.URL,
        "Enum": AtlanCustomAttributePrimitiveType.OPTIONS,
        "Users": AtlanCustomAttributePrimitiveType.USERS,
        "Groups": AtlanCustomAttributePrimitiveType.GROUPS,
        "Boolean": AtlanCustomAttributePrimitiveType.BOOLEAN,
        "Int": AtlanCustomAttributePrimitiveType.INTEGER,
        "SQL": AtlanCustomAttributePrimitiveType.SQL,
        "Date": AtlanCustomAttributePrimitiveType.DATE,
        "Decimal": AtlanCustomAttributePrimitiveType.DECIMAL
    }

    client = AtlanClient(
        base_url="",
        api_key=""
    )

    for item in loaded_data:
        try:
            existing = client.custom_metadata_cache.get_custom_metadata_def(name=item.get("name"))
        except NotFoundError:
            existing = None
        
        if existing:
            print("Updating " + existing.display_name)
            defs = []
            for existing_def in existing.attribute_defs:
                if existing_def.display_name in item.get("attributes").keys():
                    
                    app_conn = item.get("attributes").get(existing_def.display_name).get("applicable_connections")
                    app_asset_types = item.get("attributes").get(existing_def.display_name).get("applicable_asset_types")
                    app_gloss = item.get("attributes").get(existing_def.display_name).get("applicable_glossaries")
                    app_gloss_types = item.get("attributes").get(existing_def.display_name).get("applicable_glossary_types")
                    app_other_asset_types = item.get("attributes").get(existing_def.display_name).get("applicable_other_asset_types")
                    app_domains = item.get("attributes").get(existing_def.display_name).get("applicable_domains")
                    app_domain_types = item.get("attributes").get(existing_def.display_name).get("applicable_domain_types")

                    existing_def.applicable_connections=set() if not app_conn else _get_all_qualified_names("Connection") if app_conn[0] == "all" else set(app_conn)
                    existing_def.applicable_glossaries=set() if not app_gloss else _get_all_qualified_names("AtlasGlossary") if app_gloss[0] == "all" else set(app_gloss)
                    existing_def.applicable_domains=set() if not app_domains else _all_domains if app_domains[0] == "all" else set(app_domains)

                    existing_def.applicable_asset_types=set() if not app_asset_types else _complete_type_list if app_asset_types[0] == "all" else set(app_asset_types)
                    existing_def.applicable_glossary_types=set() if not app_gloss_types else _all_glossary_types if app_gloss_types[0] == "all" else set(app_gloss_types)
                    existing_def.applicable_domain_types=set() if not app_domain_types else _all_domain_types if app_domain_types[0] == "all" else set(app_domain_types)
                    existing_def.applicable_other_asset_types=set() if not app_other_asset_types else _all_other_types if  app_other_asset_types[0] == "all" else set(app_other_asset_types)
                    
                    item.get("attributes").pop(existing_def.display_name)
                    defs.append(existing_def)
            for attr_key, attr in item.get("attributes").items():
                app_conn = attr.get("applicable_connections")
                app_asset_types = attr.get("applicable_asset_types")
                app_gloss = attr.get("applicable_glossaries")
                app_gloss_types = attr.get("applicable_glossary_types")
                app_other_asset_types = attr.get("applicable_other_asset_types")
                app_domains = attr.get("applicable_domains")
                app_domain_types = attr.get("applicable_domain_types")
                defs.append(
                AttributeDef.create(
                    display_name=attr_key, # 
                    attribute_type=mapping.get(attr.get("type")), # 
                    options_name=attr.get("options"), # 
                    multi_valued=attr.get("multivalue"),
                    applicable_connections=set() if not app_conn else _get_all_qualified_names("Connection") if app_conn[0] == "all" else set(app_conn),
                    applicable_glossaries=set() if not app_gloss else _get_all_qualified_names("AtlasGlossary") if app_gloss[0] == "all" else set(app_gloss),
                    applicable_domains=set() if not app_domains else _all_domains if app_domains[0] == "all" else set(app_domains),
                    applicable_asset_types=set() if not app_asset_types else _complete_type_list if app_asset_types[0] == "all" else set(app_asset_types),
                    applicable_glossary_types=set() if not app_gloss_types else _all_glossary_types if app_gloss_types[0] == "all" else set(app_gloss_types),
                    applicable_domain_types=set() if not app_domain_types else _all_domain_types if app_domain_types[0] == "all" else set(app_domain_types),
                    applicable_other_asset_types=set() if not app_other_asset_types else _all_other_types if  app_other_asset_types[0] == "all" else set(app_other_asset_types)
                )
                )
            existing.attribute_defs = defs
            response = client.typedef.update(existing)
        else:
            #We need to create
            print("Creating " + item.get("name"))
            cm_def = CustomMetadataDef.create(display_name=item.get("name"))
            defs = []
            for attr_key, attr in item.get("attributes").items():
                app_conn = attr.get("applicable_connections")
                app_asset_types = attr.get("applicable_asset_types")
                app_gloss = attr.get("applicable_glossaries")
                app_gloss_types = attr.get("applicable_glossary_types")
                app_other_asset_types = attr.get("applicable_other_asset_types")
                app_domains = attr.get("applicable_domains")
                app_domain_types = attr.get("applicable_domain_types")
                defs.append(
                AttributeDef.create(
                    display_name=attr_key, # 
                    attribute_type=mapping.get(attr.get("type")), # 
                    options_name=attr.get("options"), # 
                    multi_valued=attr.get("multivalue"),
                    applicable_connections=set() if not app_conn else _get_all_qualified_names("Connection") if app_conn[0] == "all" else set(app_conn),
                    applicable_glossaries=set() if not app_gloss else _get_all_qualified_names("AtlasGlossary") if app_gloss[0] == "all" else set(app_gloss),
                    applicable_domains=set() if not app_domains else _all_domains if app_domains[0] == "all" else set(app_domains),
                    applicable_asset_types=set() if not app_asset_types else _complete_type_list if app_asset_types[0] == "all" else set(app_asset_types),
                    applicable_glossary_types=set() if not app_gloss_types else _all_glossary_types if app_gloss_types[0] == "all" else set(app_gloss_types),
                    applicable_domain_types=set() if not app_domain_types else _all_domain_types if app_domain_types[0] == "all" else set(app_domain_types),
                    applicable_other_asset_types=set() if not app_other_asset_types else _all_other_types if  app_other_asset_types[0] == "all" else set(app_other_asset_types)
                )
                )
            cm_def.attribute_defs = defs
            if "icon" in item:
                #Use Icon
                continue
            elif "emoji" in item:
                #Use emoji
                continue
            else:
                "Use Default"
                cm_def.options = CustomMetadataDef.Options.with_logo_from_icon(AtlanIcon.BAG_SIMPLE, AtlanTagColor.YELLOW)
            
            response = client.typedef.create(cm_def)
            

    print("\nScript finished successfully.")


# Standard Python entry point check
if __name__ == "__main__":
    main()
