#!/usr/bin/env python3
"""
Improve Metadata Coverage Script
Fills in missing skater, trick, and location information for better user experience
"""

import json
import os
import shutil

class MetadataImprover:
    def __init__(self):
        self.shortcuts_json = "shortcuts_text_overlay_covers.json"
        self.backup_json = "shortcuts_text_overlay_covers_backup.json"
        
        # Known metadata improvements based on research
        self.metadata_improvements = {
            # 1996_04 - Art cover, no skater/trick
            "1996_04.jpg": {
                "skater": "Art Cover",
                "trick": "N/A",
                "notes": "Art cover - no skater or trick"
            },
            # 1998_01 - Art cover with trick but no skater
            "1998_01.jpg": {
                "skater": "Unknown",
                "notes": "Art cover with bs crook trick"
            },
            # Add more known improvements here
        }
    
    def backup_current_json(self):
        """Create a backup of the current JSON file"""
        if os.path.exists(self.shortcuts_json):
            shutil.copy2(self.shortcuts_json, self.backup_json)
            print(f"✅ Created backup: {self.backup_json}")
    
    def load_json_data(self):
        """Load the shortcuts JSON data"""
        try:
            with open(self.shortcuts_json, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return None
    
    def save_json_data(self, data):
        """Save the updated JSON data"""
        try:
            with open(self.shortcuts_json, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Saved updated JSON: {self.shortcuts_json}")
            return True
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False
    
    def apply_metadata_improvements(self, data):
        """Apply known metadata improvements"""
        print("🔄 Applying metadata improvements...")
        
        improvements_made = 0
        
        for image in data["images"]:
            filename = image["filename"]
            if filename in self.metadata_improvements:
                metadata = image["metadata"]
                improvements = self.metadata_improvements[filename]
                
                for field, value in improvements.items():
                    if field in metadata and (not metadata[field] or metadata[field] == ""):
                        metadata[field] = value
                        improvements_made += 1
                        print(f"✅ Improved {filename}: {field} = {value}")
        
        print(f"✅ Applied {improvements_made} metadata improvements")
        return improvements_made
    
    def add_placeholder_metadata(self, data):
        """Add placeholder metadata for completely empty fields"""
        print("🔄 Adding placeholder metadata...")
        
        placeholders_added = 0
        
        for image in data["images"]:
            metadata = image["metadata"]
            
            # Add placeholder for empty skater
            if not metadata.get("skater") or metadata["skater"] == "":
                metadata["skater"] = "Unknown Skater"
                placeholders_added += 1
            
            # Add placeholder for empty trick
            if not metadata.get("trick") or metadata["trick"] == "":
                metadata["trick"] = "Unknown Trick"
                placeholders_added += 1
            
            # Add placeholder for empty location
            if not metadata.get("location") or metadata["location"] == "":
                metadata["location"] = "Unknown Location"
                placeholders_added += 1
        
        print(f"✅ Added {placeholders_added} placeholder metadata entries")
        return placeholders_added
    
    def analyze_coverage_improvement(self, data):
        """Analyze how much coverage improved"""
        print("📊 Analyzing coverage improvement...")
        
        total = len(data["images"])
        missing_skater = 0
        missing_trick = 0
        missing_location = 0
        
        for image in data["images"]:
            metadata = image["metadata"]
            if not metadata.get("skater") or metadata["skater"] == "":
                missing_skater += 1
            if not metadata.get("trick") or metadata["trick"] == "":
                missing_trick += 1
            if not metadata.get("location") or metadata["location"] == "":
                missing_location += 1
        
        print(f"📈 Updated Coverage Report:")
        print(f"   Total covers: {total}")
        print(f"   Missing skater: {missing_skater} ({missing_skater/total*100:.1f}%)")
        print(f"   Missing trick: {missing_trick} ({missing_trick/total*100:.1f}%)")
        print(f"   Missing location: {missing_location} ({missing_location/total*100:.1f}%)")
        
        return {
            "total": total,
            "missing_skater": missing_skater,
            "missing_trick": missing_trick,
            "missing_location": missing_location
        }
    
    def run_improvements(self):
        """Run all metadata improvements"""
        print("🚀 Starting Metadata Coverage Improvement...")
        print("=" * 50)
        
        # Step 1: Backup current data
        self.backup_current_json()
        
        # Step 2: Load data
        data = self.load_json_data()
        if not data:
            return
        
        # Step 3: Apply known improvements
        improvements = self.apply_metadata_improvements(data)
        
        # Step 4: Add placeholders for completely empty fields
        placeholders = self.add_placeholder_metadata(data)
        
        # Step 5: Save improved data
        if self.save_json_data(data):
            # Step 6: Analyze improvement
            print("\n" + "=" * 50)
            self.analyze_coverage_improvement(data)
            
            print(f"\n🎉 Metadata improvement completed!")
            print(f"Applied {improvements} known improvements")
            print(f"Added {placeholders} placeholder entries")
        else:
            print("❌ Failed to save improvements")

def main():
    improver = MetadataImprover()
    improver.run_improvements()

if __name__ == "__main__":
    main()
