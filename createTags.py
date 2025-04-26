"""
Tag Creation Script for Atlan

This script allows you to create multiple tags in Atlan using a YAML configuration file.
It supports three types of tags:
1. Color-only tags: Simple tags with just a name and color
2. Emoji tags: Tags with a name, color, and emoji
3. Icon tags: Tags with a name and an Atlan icon

How to use:
1. Edit the tag_template.yaml file to define your tags
2. For each tag, specify:
   - type: "color", "emoji", or "icon"
   - name: The name of the tag
   - Other parameters based on the tag type
3. Run the script: python createTagsOnly.py

The script will attempt to create all tags defined in the YAML file.
If a tag already exists, Atlan will return an error which the script will handle gracefully.

Example YAML structure:
tags:
  - type: "color"
    name: "Critical"
    description: "Critical data"
    color: "RED"
  - type: "emoji"
    name: "PII"
    description: "PII data"
    color: "YELLOW"
    emoji: "🔒"
  - type: "icon"
    name: "Database"
    description: "Database assets"
    icon_name: "PhEcho"

Prerequisites:
- Python 3.7+
- pyatlan package installed (pip install pyatlan)
- pyyaml package installed (pip install pyyaml)
- Valid Atlan API credentials
"""

import os
import yaml
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.enums import AtlanTagColor, AtlanTypeCategory
from pyatlan.model.typedef import AtlanTagDef, AtlanIcon

# Set Atlan environment variables
# export ATLAN_API_KEY=""
# export ATLAN_TENANT="https://pov.atlan.com"


# Get Atlan configuration from environment variables
ATLAN_API_KEY = os.getenv('ATLAN_API_KEY')
ATLAN_TENANT = os.getenv('ATLAN_TENANT')

if not ATLAN_API_KEY or not ATLAN_TENANT:
    raise ValueError("Please set ATLAN_API_KEY and ATLAN_TENANT environment variables")

def load_tag_config(yaml_file: str) -> list:
    """
    Load tag configurations from YAML file.
    
    Args:
        yaml_file (str): Path to the YAML configuration file
        
    Returns:
        list: List of tag configurations
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the YAML file
    yaml_path = os.path.join(script_dir, yaml_file)
    
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    
    if 'tags' not in config:
        raise ValueError("YAML file must contain a 'tags' list")
    
    return config['tags']

def create_tag_from_config(client: AtlanClient, tag_config: dict) -> str:
    """
    Create a tag based on the provided configuration.
    
    Args:
        client (AtlanClient): The Atlan client instance
        tag_config (dict): Tag configuration from YAML
        
    Returns:
        str: The display name of the created tag
    """
    tag_type = tag_config['type']
    tag_name = tag_config['name']
    
    try:
        if tag_type == 'color':
            tag_def = AtlanTagDef.create(
                name=tag_name,
                color=AtlanTagColor[tag_config['color']]
            )
        elif tag_type == 'emoji':
            tag_def = AtlanTagDef.create(
                name=tag_name,
                color=AtlanTagColor[tag_config['color']],
                emoji=tag_config['emoji']
            )
        elif tag_type == 'icon':
            tag_def = AtlanTagDef.create(
                name=tag_name,
                icon=AtlanIcon(tag_config['icon_name'])
            )
            tag_def.description = tag_config['description']
        
        response = client.typedef.create(tag_def)
        print(f"Created {tag_type} tag '{tag_name}'")
        return tag_name
    except Exception as e:
        print(f"Error creating tag '{tag_name}': {str(e)}")
        return None

def main():
    # Initialize the Atlan client
    client = AtlanClient(
        base_url=ATLAN_TENANT,
        api_key=ATLAN_API_KEY
    )
    
    try:
        # Load tag configurations from YAML
        tag_configs = load_tag_config('tag_template.yaml')
        
        # Create each tag
        created_tags = []
        for config in tag_configs:
            tag_name = create_tag_from_config(client, config)
            if tag_name:
                created_tags.append(tag_name)
        
        print(f"\nSuccessfully created {len(created_tags)} tags:")
        for tag in created_tags:
            print(f"- {tag}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 