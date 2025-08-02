#!/usr/bin/env python3
"""
4plymag Thrasher Cover Archive Metadata Scraper
Extracts detailed metadata for enhanced lock screen information
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import sqlite3

class FourPlyMagScraper:
    def __init__(self):
        self.base_url = "http://4plymag.com/thrashersearch/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.metadata = []
        
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def search_covers(self, search_term=None):
        """Search for covers with optional search term"""
        print(f"Searching 4plymag archive...")
        
        if search_term:
            # POST search request
            data = {'search': search_term}
            try:
                response = requests.post(self.base_url, data=data, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Error searching: {e}")
                return None
        else:
            # GET main page
            return self.fetch_page(self.base_url)
    
    def extract_cover_data(self, html):
        """Extract cover data from search results"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        covers = []
        
        # Look for table rows with cover data
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                info_cell = cells[0]
                cover_cell = cells[1]
                
                # Extract info text
                info_text = info_cell.get_text(strip=True)
                
                # Extract cover image
                cover_img = cover_cell.find('img')
                cover_url = None
                if cover_img and cover_img.get('src'):
                    cover_url = cover_img.get('src')
                    if not cover_url.startswith('http'):
                        cover_url = f"http://4plymag.com{cover_url}"
                
                # Parse info text for metadata
                metadata = self.parse_info_text(info_text)
                
                if metadata:
                    covers.append({
                        'info_text': info_text,
                        'cover_url': cover_url,
                        'metadata': metadata
                    })
        
        return covers
    
    def parse_info_text(self, info_text):
        """Parse info text to extract structured metadata"""
        metadata = {}
        
        # Extract date (various formats)
        date_patterns = [
            r'(\d{4})',  # Year
            r'(\w+ \d{4})',  # Month Year
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, info_text)
            if match:
                metadata['date'] = match.group(1)
                break
        
        # Extract skater names (common patterns)
        skater_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
            r'([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)',  # First Middle Last
        ]
        
        skaters = []
        for pattern in skater_patterns:
            matches = re.findall(pattern, info_text)
            skaters.extend(matches)
        
        if skaters:
            metadata['skaters'] = list(set(skaters))  # Remove duplicates
        
        # Extract tricks
        trick_keywords = [
            'kickflip', 'heelflip', 'ollie', '360', '180', 'shove-it', 'pop shove-it',
            'varial', 'double', 'triple', 'quad', 'backside', 'frontside', 'switch',
            'nollie', 'fakie', 'nose', 'tail', 'grind', 'slide', 'manual', 'nose manual',
            'tail manual', '50-50', 'boardslide', 'lipslide', 'crooked', 'smith',
            'feeble', 'nosegrind', 'tailgrind', 'overcrook', 'salad', 'soup'
        ]
        
        tricks = []
        info_lower = info_text.lower()
        for trick in trick_keywords:
            if trick in info_lower:
                tricks.append(trick)
        
        if tricks:
            metadata['tricks'] = tricks
        
        # Extract obstacles/spots
        obstacle_keywords = [
            'rail', 'ledge', 'stairs', 'gap', 'bank', 'quarter pipe', 'half pipe',
            'ramp', 'bowl', 'pool', 'curb', 'handrail', 'kicker', 'funbox',
            'pyramid', 'spine', 'wall', 'wallride', 'tree', 'pole', 'bench'
        ]
        
        obstacles = []
        for obstacle in obstacle_keywords:
            if obstacle in info_lower:
                obstacles.append(obstacle)
        
        if obstacles:
            metadata['obstacles'] = obstacles
        
        # Extract location (if mentioned)
        location_patterns = [
            r'in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',  # "in [Location]"
            r'at ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',  # "at [Location]"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, info_text)
            if match:
                metadata['location'] = match.group(1)
                break
        
        return metadata
    
    def search_by_year(self, year):
        """Search for covers from a specific year"""
        print(f"Searching for covers from {year}...")
        html = self.search_covers(str(year))
        return self.extract_cover_data(html)
    
    def search_by_skater(self, skater_name):
        """Search for covers featuring a specific skater"""
        print(f"Searching for covers featuring {skater_name}...")
        html = self.search_covers(skater_name)
        return self.extract_cover_data(html)
    
    def search_by_trick(self, trick):
        """Search for covers featuring a specific trick"""
        print(f"Searching for covers featuring {trick}...")
        html = self.search_covers(trick)
        return self.extract_cover_data(html)
    
    def get_all_covers(self):
        """Get all available covers (may take time)"""
        print("Fetching all available covers from 4plymag...")
        
        # Search by years (1981-2025)
        all_covers = []
        
        for year in range(1981, 2026):
            year_covers = self.search_by_year(year)
            all_covers.extend(year_covers)
            print(f"Found {len(year_covers)} covers from {year}")
            time.sleep(1)  # Be respectful
        
        return all_covers
    
    def create_enhanced_metadata(self, thrasher_covers_file):
        """Create enhanced metadata by combining Thrasher covers with 4plymag data"""
        print("Creating enhanced metadata...")
        
        # Load existing Thrasher covers
        with open(thrasher_covers_file, 'r') as f:
            thrasher_covers = json.load(f)
        
        enhanced_covers = []
        
        for cover in thrasher_covers:
            enhanced_cover = {
                'url': cover.get('url', cover),  # Handle both dict and string formats
                'date': cover.get('date', ''),
                'metadata': {}
            }
            
            # Try to find matching 4plymag data
            if isinstance(cover, dict) and 'date' in cover:
                # Search 4plymag for this date
                year = cover['date'][:4]
                month = cover['date'][5:7]
                
                # Search by year and month
                search_term = f"{year} {self.get_month_name(int(month))}"
                matching_covers = self.search_covers(search_term)
                
                if matching_covers:
                    # Find best match
                    best_match = self.find_best_match(cover, matching_covers)
                    if best_match:
                        enhanced_cover['metadata'] = best_match['metadata']
            
            enhanced_covers.append(enhanced_cover)
        
        return enhanced_covers
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def find_best_match(self, thrasher_cover, fourply_covers):
        """Find the best matching cover from 4plymag data"""
        # Simple matching logic - can be enhanced
        for fourply_cover in fourply_covers:
            if fourply_cover['metadata'].get('date'):
                # Check if dates match
                thrasher_date = thrasher_cover.get('date', '')
                fourply_date = fourply_cover['metadata']['date']
                
                if thrasher_date[:4] in fourply_date:  # Year match
                    return fourply_cover
        
        return None
    
    def save_metadata(self, data, filename):
        """Save metadata to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved metadata to {filename}")

def main():
    scraper = FourPlyMagScraper()
    
    # Test with a few searches
    print("Testing 4plymag scraper...")
    
    # Search for a specific year
    covers_2020 = scraper.search_by_year(2020)
    print(f"Found {len(covers_2020)} covers from 2020")
    
    # Search for a specific skater
    covers_tony = scraper.search_by_skater("Tony Hawk")
    print(f"Found {len(covers_tony)} covers featuring Tony Hawk")
    
    # Search for a specific trick
    covers_kickflip = scraper.search_by_trick("kickflip")
    print(f"Found {len(covers_kickflip)} covers featuring kickflip")
    
    # Save sample data
    sample_data = {
        '2020_covers': covers_2020,
        'tony_hawk_covers': covers_tony,
        'kickflip_covers': covers_kickflip
    }
    
    scraper.save_metadata(sample_data, '4plymag_sample_data.json')
    
    # Create enhanced metadata for our Thrasher covers
    enhanced_covers = scraper.create_enhanced_metadata('final_comprehensive_verified_urls.json')
    scraper.save_metadata(enhanced_covers, 'enhanced_covers_with_metadata.json')
    
    print(f"Enhanced {len(enhanced_covers)} covers with 4plymag metadata")

if __name__ == "__main__":
    main() 