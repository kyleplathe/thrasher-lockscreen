#!/usr/bin/env python3
"""
Create iOS Shortcuts Ready JSON
Generates JSON files optimized for iOS Shortcuts integration
"""

import json
import os
from pathlib import Path
from datetime import datetime

class ShortcutsJSONGenerator:
    def __init__(self):
        self.optimized_dir = Path("../images/optimized")
        self.output_dir = Path("../data/shortcuts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_shortcuts_json(self):
        """Create iOS Shortcuts ready JSON files"""
        # Get all optimized images
        optimized_images = list(self.optimized_dir.glob("lock_screen_*.jpg"))
        
        if not optimized_images:
            print("❌ No optimized images found. Run the optimizer first.")
            return
        
        print(f"📱 Creating iOS Shortcuts JSON for {len(optimized_images)} images...")
        
        # Create the main covers list for iOS Shortcuts
        covers_list = []
        
        for image_path in optimized_images:
            # Extract date from filename
            filename = image_path.stem.replace("lock_screen_", "")
            
            # Create GitHub raw URL (assuming this will be hosted on GitHub)
            github_url = f"https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/optimized/{image_path.name}"
            
            cover_info = {
                "filename": image_path.name,
                "url": github_url,
                "date": filename,
                "size": os.path.getsize(image_path),
                "optimized": True
            }
            
            covers_list.append(cover_info)
        
        # Create different JSON formats for different use cases
        
        # 1. Simple URL list (for basic shortcuts)
        simple_urls = [cover["url"] for cover in covers_list]
        
        # 2. Random sample (for testing)
        import random
        random_sample = random.sample(covers_list, min(50, len(covers_list)))
        
        # 3. Full covers with metadata
        full_covers = covers_list
        
        # Save all formats
        files_created = {}
        
        files_created['optimized_covers.json'] = full_covers
        files_created['simple_urls.json'] = simple_urls
        files_created['random_sample.json'] = random_sample
        
        for filename, data in files_created.items():
            output_path = self.output_dir / filename
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Created {filename} with {len(data)} items")
        
        # Create instructions file
        instructions = {
            "created_at": datetime.now().isoformat(),
            "total_covers": len(covers_list),
            "files_created": list(files_created.keys()),
            "ios_shortcuts_setup": {
                "step_1": "Open Shortcuts app on your iPhone",
                "step_2": "Create new shortcut",
                "step_3": "Add 'Get Contents of URL' action",
                "step_4": "Use: https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/data/shortcuts/optimized_covers.json",
                "step_5": "Add 'Get Dictionary from Input' action",
                "step_6": "Add 'Get Random Item from List' action",
                "step_7": "Add 'Get Dictionary Value' with key 'url'",
                "step_8": "Add 'Get Contents of URL' to download image",
                "step_9": "Add 'Set Wallpaper' action",
                "step_10": "Test the shortcut!"
            },
            "recommended_files": {
                "full_featured": "optimized_covers.json - Complete with metadata",
                "simple": "simple_urls.json - Just URLs for basic shortcuts",
                "testing": "random_sample.json - 50 random covers for testing"
            }
        }
        
        instructions_path = self.output_dir / "shortcuts_instructions.json"
        with open(instructions_path, 'w') as f:
            json.dump(instructions, f, indent=2)
        
        print(f"✅ Created shortcuts_instructions.json")
        print(f"\n📱 iOS Shortcuts Setup Complete!")
        print(f"📁 Files saved to: {self.output_dir}")
        print(f"🎯 Ready for GitHub deployment!")

def main():
    generator = ShortcutsJSONGenerator()
    generator.create_shortcuts_json()

if __name__ == "__main__":
    main() 