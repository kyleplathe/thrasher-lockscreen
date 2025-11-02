#!/usr/bin/env python3
"""
Extract metadata from recent Thrasher cover filenames (April 2024 - September 2025)
"""

import re
import json
import os

def parse_filename(filename):
    """Parse filename to extract date, skater, trick, etc."""
    
    # Remove extension
    name = filename.replace('.jpg', '')
    
    # Initialize metadata
    metadata = {
        'year': '',
        'month': '',
        'skater': '',
        'trick': '',
        'obstacle': '',
        'location': ''
    }
    
    # Pattern 1: 0625_Thrasher_Cover_Alex_Midler_Back_Lip_1080
    # Format: MMYY_Thrasher_Cover_Skater_Trick
    match = re.match(r'(\d{2})(\d{2})_Thrasher_Cover_(.+?)(?:_\d+)?$', name)
    if match:
        month = match.group(1)
        year = '20' + match.group(2)
        skater_trick = match.group(3)
        
        # Try to split skater and trick by capitalization
        # Look for pattern where trick starts with capital letter after lowercase
        trick_match = re.match(r'^([a-z\s]+?)([A-Z][A-Za-z\s]+)$', skater_trick)
        if trick_match:
            metadata['skater'] = trick_match.group(1).strip().title()
            metadata['trick'] = trick_match.group(2).strip()
        else:
            # Try splitting by underscore
            parts = skater_trick.split('_')
            if len(parts) >= 3:
                # First 2 parts are skater name, rest is trick
                metadata['skater'] = ' '.join(parts[:2]).title()
                metadata['trick'] = ' '.join(parts[2:]).title()
            elif len(parts) >= 2:
                metadata['skater'] = parts[0].replace('_', ' ').title()
                metadata['trick'] = ' '.join(parts[1:]).title()
            else:
                metadata['skater'] = skater_trick.replace('_', ' ').title()
        
        metadata['year'] = year
        metadata['month'] = month.lstrip('0')
        return metadata
    
    # Pattern 2: 25_01_Thrasher_Cover_Grant_Taylor_Ollie_Burnett_1080 or Thrasher-Cover
    # Format: YY_MM_Thrasher_Cover_Skater_Trick_Detail (when first part is likely a year 20-29)
    match = re.match(r'(\d{2})_(\d{2})_Thrasher[-_]Cover[-_](.+?)(?:_\d+)?$', name)
    if match:
        first_part = int(match.group(1))
        second_part = int(match.group(2))
        
        # If first part is 20-29, it's likely YY_MM format
        if 20 <= first_part <= 29:
            year = '20' + match.group(1)
            month = match.group(2)
        else:
            # Otherwise it's MM_YY format
            month = match.group(1)
            year = '20' + match.group(2)
        
        skater_trick = match.group(3)
        
        # Try to split by looking for pattern where we have First_Last_ then rest is trick
        # Try splitting by underscore and looking for last name pattern
        parts = skater_trick.split('_')
        if len(parts) >= 3:
            # Likely: First_Last_Trick or First_Middle_Last_Trick
            metadata['skater'] = ' '.join(parts[:2]).title()
            metadata['trick'] = ' '.join(parts[2:]).title()
        elif len(parts) >= 2:
            metadata['skater'] = parts[0].replace('_', ' ').title()
            metadata['trick'] = ' '.join(parts[1:]).title()
        else:
            metadata['skater'] = skater_trick.replace('_', ' ').title()
        
        metadata['year'] = year
        metadata['month'] = month.lstrip('0')
        return metadata
    
    # Pattern 4: 2024_11_Thrasher_Magazine_Cover_Tiago_Lemos_1080
    # Format: YYYY_MM_Thrasher_Magazine_Cover_Skater_Trick
    match = re.match(r'(\d{4})_(\d{2})_Thrasher_Magazine_Cover_(.+?)(?:_\d+)?$', name)
    if match:
        year = match.group(1)
        month = match.group(2)
        skater_trick = match.group(3)
        
        # Split by underscore
        parts = skater_trick.split('_')
        if len(parts) >= 3:
            # First 2 parts are skater name, rest is trick
            metadata['skater'] = ' '.join(parts[:2]).title()
            metadata['trick'] = ' '.join(parts[2:]).title()
        elif len(parts) >= 2:
            # Could be First_Last or First_Trick - assume First_Last is skater only
            metadata['skater'] = ' '.join(parts[:2]).title()
            metadata['trick'] = ''
        else:
            metadata['skater'] = skater_trick.replace('_', ' ').title()
        
        metadata['year'] = year
        metadata['month'] = month.lstrip('0')
        return metadata
    
    # Pattern 5: 25_05_Jamie_Foy_Burnett_Frontside_Half_Cab_Nosegrind_CV1TH0525_1080
    # Format: YY_MM_Skater_Trick_ID
    match = re.match(r'(\d{2})_(\d{2})_(.+?)_(CV\d+[A-Z]+\d+)(?:_\d+)?$', name)
    if match:
        year = '20' + match.group(1)
        month = match.group(2)
        skater_trick = match.group(3)
        issue_id = match.group(4)
        
        # Split by underscore - first 3 parts are skater (First_Middle_Last), rest is trick
        parts = skater_trick.split('_')
        if len(parts) >= 4:
            metadata['skater'] = ' '.join(parts[:3]).title()
            metadata['trick'] = ' '.join(parts[3:]).title()
        elif len(parts) >= 2:
            # Could be First_Last_Trick or First_Trick
            metadata['skater'] = ' '.join(parts[:2]).title()
            metadata['trick'] = ' '.join(parts[2:]).title()
        else:
            metadata['skater'] = skater_trick.replace('_', ' ').title()
        
        metadata['year'] = year
        metadata['month'] = month.lstrip('0')
        return metadata
    
    return None

def main():
    # Recent filenames from the original directory
    filenames = [
        '0625_Thrasher_Cover_Alex_Midler_Back_Lip_1080.jpg',
        '0725_Thrasher_Cover_Cody_Chapman_Kickflip_1080.jpg',
        '0825_Thrasher_Cover_Curren_Caples_50_50_1080.jpg',
        '09_25_Thrasher_Cover_Jerry_Hsu_Darkslide_1080.jpg',
        '2024_11_Thrasher_Magazine_Cover_Tiago_Lemos_1080.jpg',
        '2024_12_Thrasher_Magazine_Cover_Jamie_Foy_1080.jpg',
        '25_01_Thrasher_Cover_Grant_Taylor_Ollie_Burnett_1080.jpg',
        '25_02_Thrasher_Cover_Greyson_Fletcher_One_Foot_Aguilar_1080.jpg',
        '25_03_Thrasher-Cover_Andrew_Reynollds_Kickflip_Wallride_Darwen_1080.jpg',
        '25_04_Thrasher_Cover_Tristan_Funkhouser_Tree_Ride_Marco_Hernandez_1080.jpg',
        '25_05_Jamie_Foy_Burnett_Frontside_Half_Cab_Nosegrind_CV1TH0525_1080.jpg',
    ]
    
    print("🔍 Extracting metadata from recent cover filenames...")
    print()
    
    results = []
    for filename in filenames:
        metadata = parse_filename(filename)
        if metadata:
            # Create the target filename format
            target_filename = f"{metadata['year']}_{metadata['month']:0>2}.jpg"
            
            result = {
                'original_filename': filename,
                'target_filename': target_filename,
                'metadata': metadata
            }
            results.append(result)
            
            print(f"✅ {filename}")
            print(f"   → {target_filename}")
            print(f"   Year: {metadata['year']}, Month: {metadata['month']}")
            print(f"   Skater: {metadata['skater']}")
            print(f"   Trick: {metadata['trick']}")
            print()
        else:
            print(f"❌ Could not parse: {filename}")
            print()
    
    # Save results
    output_file = 'recent_metadata_extracted.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Saved {len(results)} results to {output_file}")

if __name__ == "__main__":
    main()

