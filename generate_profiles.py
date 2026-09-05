"""
Script to generate synthetic customer profiles and save to data/profiles.json

This script generates 4-5 customer profiles with varied patterns and saves them
to the data directory for use by the application.
"""

import json
from src.data_generator import SyntheticDataGenerator


def generate_and_save_profiles():
    """
    Generate synthetic customer profiles and save to data/profiles.json
    """
    # Create data generator
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate profiles
    print("Generating customer profiles...")
    profiles = generator.generate_profiles()
    
    print(f"Generated {len(profiles)} profiles:")
    for profile in profiles:
        print(f"  - {profile.name} ({profile.customer_id}): {len(profile.transactions)} transactions")
    
    # Convert profiles to dictionaries
    profiles_data = {
        'generated_at': generator.base_date.isoformat(),
        'profiles': [profile.to_dict() for profile in profiles]
    }
    
    # Save to JSON file
    output_path = 'data/profiles.json'
    with open(output_path, 'w') as f:
        json.dump(profiles_data, f, indent=2)
    
    print(f"\nSaved profiles to {output_path}")
    print(f"Total file size: {len(json.dumps(profiles_data))} bytes")


def load_profiles():
    """
    Load customer profiles from data/profiles.json
    
    Returns:
        dict: Dictionary containing generated_at timestamp and list of profiles
    """
    with open('data/profiles.json', 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    generate_and_save_profiles()
    
    # Verify loading works
    print("\nVerifying profiles can be loaded...")
    data = load_profiles()
    print(f"Successfully loaded {len(data['profiles'])} profiles")
    print(f"Generated at: {data['generated_at']}")
