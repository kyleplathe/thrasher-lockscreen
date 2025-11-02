#!/usr/bin/env python3
"""
Monthly Thrasher Cover Scraper
Automatically checks for new covers and downloads them
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from pathlib import Path

class ThrasherMonthlyScraper:
    def __init__(self):
        self.base_url = "https://www.thrashermagazine.com/articles/magazine/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.original_dir = Path("images/original")
        self.optimized_dir = Path("images/optimized_final_with_text")
        self.json_file = "shortcuts_text_overlay_covers.json"
        
    def fetch_page(self):
        """Fetch the Thrasher magazine archive page"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {self.base_url}: {e}")
            return None
    
    def extract_new_covers(self, html_content):
        """Extract cover information from HTML"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        covers = []
        
        # Find all images on the page
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if not src:
                continue
            
            # Look for recent covers (2024-2025)
            if not (re.search(r'2024|2025', alt) or re.search(r'2024|2025', src)):
                continue
            
            # Parse date from alt text or src (e.g., "December 2025 Cover" or "Thrasher_Cover_12_25")
            date_info = self._extract_date(alt, src)
            if not date_info:
                continue
            
            year, month, month_name = date_info
            
            # Construct full URL
            if not src.startswith('http'):
                src = f"https://www.thrashermagazine.com{src}"
            
            # Keep original resolution for now (they only provide 350px)
            # The optimizer will upscale if needed
            
            covers.append({
                'year': year,
                'month': month,
                'month_name': month_name,
                'url': src,
                'alt': alt
            })
        
        return covers
    
    def _extract_date(self, alt_text, src):
        """Extract year and month from alt text or src"""
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Try to extract from alt text first (e.g., "Tom Schaar Thrasher Cover Disaster December 2025")
        if alt_text:
            for month_name, month_num in month_names.items():
                pattern = rf"({month_name})\s+(\d{{4}})"
                match = re.search(pattern, alt_text.lower())
                if match:
                    return int(match.group(2)), month_num, month_name.capitalize()
        
        # Try to extract from src (e.g., "Thrasher_Cover_12_25_Tom_Schaar_Disaster_350.jpg" or "CV1TH1125_1080.jpg")
        if src:
            # New CV1TH pattern: CV1THMMYY_1080.jpg (e.g., CV1TH1125 = November 2025)
            cv1th_pattern = r'CV1TH(\d{1,2})(\d{2})'
            match = re.search(cv1th_pattern, src)
            if match:
                month = int(match.group(1))
                year = int('20' + match.group(2))
                month_name = list(month_names.keys())[month - 1]
                return year, month, month_name.capitalize()
            
            # Look for MM_YY or MMYY pattern in filename
            mm_yy_pattern = r'(\d{1,2})_?(\d{2})\D'
            match = re.search(mm_yy_pattern, src)
            if match:
                month = int(match.group(1))
                year = int('20' + match.group(2))
                month_name = list(month_names.keys())[month - 1]
                return year, month, month_name.capitalize()
            
            # Also try old format: monthnameYYYYsfw.jpg
            for month_name, month_num in month_names.items():
                pattern = rf"{month_name}(\d{{4}})sfw\.jpg"
                match = re.search(pattern, src.lower())
                if match:
                    return int(match.group(1)), month_num, month_name.capitalize()
        
        return None
    
    def get_existing_covers(self):
        """Get list of covers we already have"""
        existing = set()
        
        # Check existing JSON for registered covers
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                for img in data.get('images', []):
                    if 'filename' in img:
                        existing.add(img['filename'])
        
        return existing
    
    def download_cover(self, cover_info):
        """Download a cover image"""
        try:
            print(f"Downloading {cover_info['month_name']} {cover_info['year']}...")
            response = requests.get(cover_info['url'], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Save to original directory
            filename = f"{cover_info['year']}_{cover_info['month']:02d}.jpg"
            output_path = self.original_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  Saved to {output_path}")
            return True
            
        except requests.RequestException as e:
            print(f"  Error downloading: {e}")
            return False
    
    def add_to_json(self, cover_info):
        """Add cover to shortcuts JSON"""
        try:
            # Load existing JSON
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {
                    "version": "1.0",
                    "description": "Thrasher Magazine covers with text overlays for iOS Shortcuts",
                    "total_images": 0,
                    "images": []
                }
            
            # Check if this cover already exists
            filename = f"{cover_info['year']}_{cover_info['month']:02d}.jpg"
            existing_filenames = {img['filename'] for img in data['images']}
            
            if filename in existing_filenames:
                print(f"  Cover {filename} already in JSON")
                return
            
            # Create new entry
            new_entry = {
                "filename": filename,
                "url": f"https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/optimized_final_with_text/{filename}",
                "metadata": {
                    "filename": filename,
                    "year": str(cover_info['year']),
                    "month": f"{cover_info['month']:02d}"
                }
            }
            
            # Add to images list
            data['images'].append(new_entry)
            data['total_images'] = len(data['images'])
            
            # Save updated JSON
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  Added {filename} to JSON")
            
        except Exception as e:
            print(f"  Error adding to JSON: {e}")
    
    def process_new_covers(self):
        """Main method to check for and download new covers"""
        print("🔍 Checking for new Thrasher covers...")
        
        # Fetch archive page
        html = self.fetch_page()
        if not html:
            print("❌ Failed to fetch archive page")
            return
        
        # Extract covers from page
        covers = self.extract_new_covers(html)
        print(f"📄 Found {len(covers)} covers on Thrasher website")
        
        # Get existing covers
        existing = self.get_existing_covers()
        print(f"📦 Already have {len(existing)} covers")
        
        # Filter for new covers
        new_covers = []
        for cover in covers:
            filename = f"{cover['year']}_{cover['month']:02d}.jpg"
            if filename not in existing:
                new_covers.append(cover)
        
        if not new_covers:
            print("✅ No new covers found!")
            return
        
        print(f"🆕 Found {len(new_covers)} new covers:")
        for cover in new_covers:
            print(f"   - {cover['month_name']} {cover['year']}")
        
        # Download new covers
        print("\n⬇️  Downloading new covers...")
        for cover in new_covers:
            if self.download_cover(cover):
                self.add_to_json(cover)
        
        print(f"\n✅ Successfully processed {len(new_covers)} new covers!")
        print(f"\n📝 Next steps:")
        print(f"   1. Run image_optimizer.py to process new images")
        print(f"   2. Run apply_text_overlays_all.py to add text overlays")
        print(f"   3. Commit and push to GitHub")

def main():
    scraper = ThrasherMonthlyScraper()
    scraper.process_new_covers()

if __name__ == "__main__":
    main()

