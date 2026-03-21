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
        self.shop_products_url = "https://shop.thrashermagazine.com/collections/magazines/products.json?limit=250"
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
            
            # Recent / upcoming issues (alt often has "May, 2026"; src may use CV1THMMYY or /InTheMag/YYYY/)
            if not (
                re.search(r'\b202[4-9]\b', alt)
                or re.search(r'\b202[4-9]\b', src)
                or re.search(r'CV1TH\d{1,2}\d{2}', src, re.I)
            ):
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

    def extract_shop_covers(self):
        """Extract cover information from Thrasher shop products feed"""
        covers = []
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        try:
            response = requests.get(self.shop_products_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            payload = response.json()
        except Exception as e:
            print(f"Warning: Could not fetch shop products: {e}")
            return covers

        for product in payload.get("products", []):
            title = (product.get("title") or "").strip()
            handle = (product.get("handle") or "").strip()
            title_l = title.lower()
            handle_l = handle.lower()

            month_name = None
            for name in month_names:
                if name in title_l or name in handle_l:
                    month_name = name
                    break
            if not month_name:
                continue

            year_match = re.search(r"(20\d{2})", title_l) or re.search(r"(20\d{2})", handle_l)
            if not year_match:
                continue

            year = int(year_match.group(1))
            month = month_names[month_name]
            if not self._valid_issue_date(year, month):
                continue

            # Prefer primary image src; fallback to first image in images[]
            image_url = ""
            if product.get("image") and product["image"].get("src"):
                image_url = product["image"]["src"]
            elif product.get("images"):
                first_img = product["images"][0] if product["images"] else {}
                image_url = first_img.get("src", "")
            if not image_url:
                continue

            covers.append({
                "year": year,
                "month": month,
                "month_name": month_name.capitalize(),
                "url": image_url,
                "alt": title
            })
        return covers
    
    def _valid_issue_date(self, year, month):
        """Reject bogus parses (e.g. MM_YY matching inside cache hex ids)."""
        if not (1 <= month <= 12):
            return False
        y_max = datetime.now().year + 2
        return 1981 <= year <= y_max

    def _extract_date(self, alt_text, src):
        """Extract year and month from alt text or src"""
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        def ok(y, m, name):
            if self._valid_issue_date(y, m):
                return y, m, name
            return None
        
        # Try to extract from alt text first (e.g., "Tom Schaar Thrasher Cover Disaster December 2025")
        if alt_text:
            for month_name, month_num in month_names.items():
                pattern = rf"({month_name})\s+(\d{{4}})"
                match = re.search(pattern, alt_text.lower())
                if match:
                    y, m = int(match.group(2)), month_num
                    got = ok(y, m, month_name.capitalize())
                    if got:
                        return got
            # "May, 2026" style
            for month_name, month_num in month_names.items():
                pattern = rf"({month_name}),\s*(\d{{4}})"
                match = re.search(pattern, alt_text.lower())
                if match:
                    y, m = int(match.group(2)), month_num
                    got = ok(y, m, month_name.capitalize())
                    if got:
                        return got
        
        # Try to extract from src (e.g., "Thrasher_Cover_12_25_Tom_Schaar_Disaster_350.jpg" or "CV1TH1125_1080.jpg")
        if src:
            # New CV1TH pattern: CV1THMMYY_1080.jpg (e.g., CV1TH1125 = November 2025)
            cv1th_pattern = r'CV1TH(\d{1,2})(\d{2})'
            match = re.search(cv1th_pattern, src)
            if match:
                month = int(match.group(1))
                year = int('20' + match.group(2))
                month_name = list(month_names.keys())[month - 1]
                got = ok(year, month, month_name.capitalize())
                if got:
                    return got
            
            # MM_YY only in obvious cover paths (never match inside /cache/… hex)
            if re.search(r'InTheMag|Thrasher_Cover|thrasher_cover', src, re.I):
                mm_yy_pattern = r'(\d{1,2})_?(\d{2})\D'
                match = re.search(mm_yy_pattern, src)
                if match:
                    month = int(match.group(1))
                    year = int('20' + match.group(2))
                    month_name = list(month_names.keys())[month - 1]
                    got = ok(year, month, month_name.capitalize())
                    if got:
                        return got
            
            # Also try old format: monthnameYYYYsfw.jpg
            for month_name, month_num in month_names.items():
                pattern = rf"{month_name}(\d{{4}})sfw\.jpg"
                match = re.search(pattern, src.lower())
                if match:
                    y = int(match.group(1))
                    got = ok(y, month_num, month_name.capitalize())
                    if got:
                        return got
        
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

        # Also treat local files as existing in case JSON lags behind.
        for directory in (self.original_dir, self.optimized_dir):
            if directory.exists():
                for path in directory.glob("*.jpg"):
                    existing.add(path.name)
        
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
        website_covers = self.extract_new_covers(html)
        shop_covers = self.extract_shop_covers()
        covers_by_file = {}
        for cover in website_covers + shop_covers:
            filename = f"{cover['year']}_{cover['month']:02d}.jpg"
            covers_by_file[filename] = cover
        covers = sorted(covers_by_file.values(), key=lambda c: (c["year"], c["month"]))
        print(f"📄 Found {len(website_covers)} covers on Thrasher website")
        print(f"🛒 Found {len(shop_covers)} covers in shop archive")
        print(f"🧩 Combined unique covers: {len(covers)}")
        
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
        
        new_covers.sort(key=lambda c: (c["year"], c["month"]))
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

