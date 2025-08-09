#!/usr/bin/env python3
"""
Apply Multiple Cover Fixes Script
Applies the correct data mappings for all months with multiple covers
"""

from fix_multiple_covers_per_month import MultipleCoversFixer

def main():
    fixer = MultipleCoversFixer()
    
    print("🔧 APPLYING COMPREHENSIVE FIXES FOR MULTIPLE COVERS")
    print("="*60)
    
    # Complete manual mappings for all multiple cover months
    manual_mappings = {
        # 1988 December - 2 covers
        "1988_12.jpg": "1988_12",  # Lance Mountain (current data is probably wrong)
        
        # 2012 June - 2 covers  
        "2012_06.jpg": "2012_06",        # Danny Way
        "2012_06_01.jpg": "2012_06_01",  # Kreayshawn
        
        # 2013 January - 5 covers (the main issue you noticed)
        "2013_01.jpg": "2013_01_04",     # Should be Stevie Perez (currently assigned)
        "2013_01_01.jpg": "2013_01",     # Should be Vincent Alvarez
        "2013_01_02.jpg": "2013_01_01",  # Should be Elijah Berle  
        "2013_01_03.jpg": "2013_01_02",  # Should be Corey Kennedy
        "2013_01_04.jpg": "2013_01_03",  # Should be Raven Tershy
        
        # 2015 January - 4 covers
        "2015_01.jpg": "2015_01",        # Ishod Wair
        "2015_01_01.jpg": "2015_01_01",  # Torey Pudwill
        "2015_01_02.jpg": "2015_01_02",  # Blake Carpenter
        "2015_01_03.jpg": "2015_01_03",  # Brandon Westgate
        
        # 2015 September - 2 covers
        "2015_09.jpg": "2015_09",        # Raven Tershy
        "2015_09_01.jpg": "2015_09_01",  # Figgy
        
        # 2017 January - 2 covers
        "2017_01.jpg": "2017_01",        # Kyle Walker
        "2017_01_01.jpg": "2017_01_01",  # Dylan Reider
    }
    
    print("📋 Mapping Summary:")
    print("-" * 40)
    
    # Show what we're about to fix
    for image_file, data_key in manual_mappings.items():
        metadata = fixer.fourply_data.get(data_key, {})
        skater = metadata.get('skater', 'Unknown')
        trick = metadata.get('trick', 'Unknown')
        special = metadata.get('special', metadata.get('detailer', ''))
        identifier = f" ({special})" if special else ""
        print(f"  {image_file} → {skater} - {trick}{identifier}")
    
    # Apply the fixes
    print(f"\n🚀 Applying fixes to {len(manual_mappings)} images...")
    fixed_count = fixer.apply_fixes(manual_mappings)
    
    print(f"\n✅ FIXES COMPLETE!")
    print(f"Successfully fixed {fixed_count} images with correct data!")
    
    return fixed_count

if __name__ == "__main__":
    main()
