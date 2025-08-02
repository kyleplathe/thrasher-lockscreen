#!/usr/bin/env python3
"""
Download Thrasher Magazine Cover Images
Downloads all verified cover images from the JSON file
"""

import requests
import json
import os
import time
from urllib.parse import urlparse
from pathlib import Path

class ThrasherImageDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.download_dir = Path("../images/original")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def download_image(self, url, filename):
        """Download a single image with error handling"""
        try:
            print(f"Downloading: {filename}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            filepath = self.download_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {filename} ({len(response.content)} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            return False
    
    def download_all_images(self):
        """Download all images from the verified URLs JSON file"""
        # Load the verified URLs
        json_file = Path("../data/shortcuts/final_comprehensive_verified_urls.json")
        
        if not json_file.exists():
            print(f"❌ JSON file not found: {json_file}")
            return
        
        with open(json_file, 'r') as f:
            urls = json.load(f)
        
        print(f"📥 Starting download of {len(urls)} images...")
        print(f"📁 Saving to: {self.download_dir}")
        
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Skip if file already exists
            if (self.download_dir / filename).exists():
                print(f"⏭️  Skipping {filename} (already exists)")
                successful += 1
                continue
            
            # Download the image
            if self.download_image(url, filename):
                successful += 1
            else:
                failed += 1
            
            # Progress update
            if i % 10 == 0:
                print(f"📊 Progress: {i}/{len(urls)} ({i/len(urls)*100:.1f}%)")
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        print(f"\n🎉 Download Complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Images saved to: {self.download_dir}")

def main():
    downloader = ThrasherImageDownloader()
    downloader.download_all_images()

if __name__ == "__main__":
    main() 