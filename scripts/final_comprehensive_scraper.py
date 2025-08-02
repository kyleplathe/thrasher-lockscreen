#!/usr/bin/env python3
"""
Final Comprehensive Thrasher Magazine Covers Scraper
Extracts ALL covers from 1981-2025 to get the complete 537 covers
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin
import time
import random
from datetime import datetime

class FinalComprehensiveScraper:
    def __init__(self):
        self.base_url = "https://api.thrashermagazine.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.all_covers = []
        
    def extract_all_urls_from_analysis(self):
        """Extract ALL cover URLs from the analysis results"""
        print("Extracting all cover URLs from analysis results...")
        
        with open('thrasher_analysis_results.json', 'r') as f:
            data = json.load(f)
        
        covers = []
        seen_urls = set()
        
        for item in data.get('covers_found', []):
            src = item.get('image_url', '')
            alt = item.get('alt_text', '')
            date = item.get('date')
            
            # Skip UI elements
            if any(ui_element in src for ui_element in ['zoom.png', 'read.png', 'watch.png']):
                continue
            
            # Skip if no date or already seen
            if not date or src in seen_urls:
                continue
            
            # Normalize URL
            if src.startswith('/'):
                full_url = self.base_url + src
            elif src.startswith('http'):
                full_url = src
            else:
                continue
            
            seen_urls.add(src)
            
            cover_info = {
                'date': date,
                'url': full_url,
                'alt_text': alt,
                'filename': os.path.basename(src),
                'source': 'analysis_results',
                'verified': False
            }
            covers.append(cover_info)
        
        print(f"Extracted {len(covers)} unique cover URLs from analysis results")
        return covers
    
    def generate_all_comprehensive_patterns(self):
        """Generate ALL comprehensive patterns for 1981-2025"""
        print("Generating ALL comprehensive patterns for 1981-2025...")
        
        all_patterns = []
        
        # Pattern 1: 1981-1999: /images/image/Covers Section/images/[Month][Year].jpg
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        for year in range(1981, 2000):
            for month in months:
                pattern = f"/images/image/Covers Section/images/{month}{year}.jpg"
                date = f"{year:04d}-{months.index(month)+1:02d}-01"
                
                all_patterns.append({
                    'date': date,
                    'url': self.base_url + pattern,
                    'pattern': pattern,
                    'source': 'pattern_1981_1999',
                    'verified': False
                })
        
        # Pattern 2: 2000-2008: /images/image/Covers Section/images/[Month][Year][sfw].jpg
        for year in range(2000, 2009):
            for month in months:
                # Try multiple variations for 2000-2008
                patterns_2000_2008 = [
                    f"/images/image/Covers Section/images/{month}{year}.jpg",
                    f"/images/image/Covers Section/images/{month}{year}sfw.jpg",
                    f"/images/image/Covers Section/images/{month}{year}_sfw.jpg",
                    f"/images/image/Covers Section/images/{month}{year}sfw.jpg",
                    f"/images/image/Covers Section/images/{month}{year}.jpg"
                ]
                
                for pattern in patterns_2000_2008:
                    date = f"{year:04d}-{months.index(month)+1:02d}-01"
                    all_patterns.append({
                        'date': date,
                        'url': self.base_url + pattern,
                        'pattern': pattern,
                        'source': 'pattern_2000_2008',
                        'verified': False
                    })
        
        # Pattern 3: 2009-2019: Various patterns
        for year in range(2009, 2020):
            for month in range(1, 13):
                month_str = f"{month:02d}"
                short_year = str(year)[-2:]
                
                # Multiple pattern variations for 2009-2019
                patterns_2009_2019 = [
                    f"/images/image/Covers Section/images/{year}_{month_str}_Thrasher_Magazine_Cover_1080.jpg",
                    f"/images/image/Covers Section/images/{year}_{month_str}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers Section/images/{month_str}_{short_year}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers Section/images/{short_year}_{month_str}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers Section/images/{year}_{month_str}.jpg",
                    f"/images/image/Covers Section/images/{month_str}_{year}.jpg",
                    f"/images/image/Covers Section/images/{year}_{month_str}sfw.jpg",
                    f"/images/image/Covers Section/images/{month_str}{year}sfw.jpg",
                    f"/images/CV1TH{month_str}{short_year}.jpg",
                    f"/images/CV1TH{month_str}{short_year}_Sml.jpg"
                ]
                
                for pattern in patterns_2009_2019:
                    date = f"{year:04d}-{month:02d}-01"
                    all_patterns.append({
                        'date': date,
                        'url': self.base_url + pattern,
                        'pattern': pattern,
                        'source': 'pattern_2009_2019',
                        'verified': False
                    })
        
        # Pattern 4: 2020-2025: Modern patterns
        for year in range(2020, 2026):
            for month in range(1, 13):
                short_year = str(year)[-2:]
                month_str = f"{month:02d}"
                
                modern_patterns = [
                    f"/images/{month_str}_{short_year}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers_Archive/{short_year}_{month_str}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers_Archive/{short_year}_{month_str}_Thrasher-Cover_1080.jpg",
                    f"/images/{month_str}{short_year}_Thrasher_Cover_1080.jpg",
                    f"/images/image/Covers Section/images/{year}_{month_str}_Thrasher_Magazine_Cover_1080.jpg",
                    f"/images/{short_year}_{month_str}_Thrasher_Cover_1080.jpg",
                    f"/images/CV1TH{month_str}{short_year}.jpg",
                    f"/images/CV1TH{month_str}{short_year}_Sml.jpg"
                ]
                
                for pattern in modern_patterns:
                    date = f"{year:04d}-{month:02d}-01"
                    all_patterns.append({
                        'date': date,
                        'url': self.base_url + pattern,
                        'pattern': pattern,
                        'source': 'pattern_2020_2025',
                        'verified': False
                    })
        
        print(f"Generated {len(all_patterns)} potential patterns")
        return all_patterns
    
    def test_url_accessibility(self, urls, max_tests=None):
        """Test which URLs are accessible"""
        if max_tests is None:
            max_tests = len(urls)
        
        accessible_urls = []
        
        print(f"Testing {min(max_tests, len(urls))} URLs for accessibility...")
        
        for i, cover in enumerate(urls[:max_tests]):
            try:
                response = requests.head(cover['url'], headers=self.headers, timeout=5)
                if response.status_code == 200:
                    cover['verified'] = True
                    accessible_urls.append(cover)
                    print(f"✓ {cover['date']}: {cover['url']}")
                else:
                    print(f"✗ {cover['date']}: {response.status_code}")
            except:
                print(f"✗ {cover['date']}: Connection failed")
            
            # Be respectful with requests
            time.sleep(0.1)
        
        return accessible_urls
    
    def create_final_comprehensive_list(self):
        """Create the final comprehensive list of all available covers"""
        
        print("Final Comprehensive Thrasher Magazine Covers Scraper")
        print("=" * 70)
        
        # Extract all URLs from analysis results
        analysis_covers = self.extract_all_urls_from_analysis()
        
        # Generate comprehensive patterns
        pattern_covers = self.generate_all_comprehensive_patterns()
        
        # Test analysis covers first (these are more likely to work)
        print("\nTesting analysis results covers...")
        verified_analysis = self.test_url_accessibility(analysis_covers, max_tests=300)
        
        # Test pattern covers
        print("\nTesting generated pattern covers...")
        verified_patterns = self.test_url_accessibility(pattern_covers, max_tests=1000)
        
        # Combine all covers
        all_covers = verified_analysis + verified_patterns
        
        # Remove duplicates based on date
        unique_covers = {}
        for cover in all_covers:
            date = cover['date']
            if date not in unique_covers:
                unique_covers[date] = cover
            elif cover.get('verified', False) and not unique_covers[date].get('verified', False):
                # Prefer verified covers
                unique_covers[date] = cover
        
        covers_list = list(unique_covers.values())
        covers_list.sort(key=lambda x: x['date'])
        
        print(f"\nTotal unique covers found: {len(covers_list)}")
        
        # Create different formats for iOS Shortcuts
        
        # Format 1: All verified covers
        verified_urls = [cover['url'] for cover in covers_list if cover.get('verified', False)]
        
        # Format 2: All covers (including unverified)
        all_urls = [cover['url'] for cover in covers_list]
        
        # Format 3: Date-URL pairs
        date_url_pairs = [{'date': cover['date'], 'url': cover['url']} for cover in covers_list]
        
        # Format 4: Categorized by source
        analysis_covers = [cover for cover in covers_list if cover.get('source') == 'analysis_results']
        pattern_1981_1999_covers = [cover for cover in covers_list if cover.get('source') == 'pattern_1981_1999']
        pattern_2000_2008_covers = [cover for cover in covers_list if cover.get('source') == 'pattern_2000_2008']
        pattern_2009_2019_covers = [cover for cover in covers_list if cover.get('source') == 'pattern_2009_2019']
        pattern_2020_2025_covers = [cover for cover in covers_list if cover.get('source') == 'pattern_2020_2025']
        
        # Format 5: Random samples
        random_verified = random.sample(verified_urls, min(25, len(verified_urls))) if verified_urls else []
        random_all = random.sample(all_urls, min(50, len(all_urls))) if all_urls else []
        
        # Save all formats
        files_created = {}
        
        files_created['final_comprehensive_verified_urls.json'] = verified_urls
        files_created['final_comprehensive_all_urls.json'] = all_urls
        files_created['final_comprehensive_date_url_pairs.json'] = date_url_pairs
        files_created['analysis_results_covers.json'] = analysis_covers
        files_created['pattern_1981_1999_covers.json'] = pattern_1981_1999_covers
        files_created['pattern_2000_2008_covers.json'] = pattern_2000_2008_covers
        files_created['pattern_2009_2019_covers.json'] = pattern_2009_2019_covers
        files_created['pattern_2020_2025_covers.json'] = pattern_2020_2025_covers
        files_created['random_verified_sample.json'] = random_verified
        files_created['random_all_sample.json'] = random_all
        
        for filename, data in files_created.items():
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Created {filename} with {len(data)} items")
        
        # Create comprehensive instructions
        instructions = {
            "discovered_patterns": {
                "pattern_1981_1999": "/images/image/Covers Section/images/[Month][Year].jpg",
                "pattern_2000_2008": "/images/image/Covers Section/images/[Month][Year][sfw].jpg",
                "pattern_2009_2019": "Various patterns for 2009-2019",
                "pattern_2020_2025": "Modern patterns for 2020-2025",
                "analysis_results": "Directly from archive analysis"
            },
            "recommended_approach": {
                "primary": "Use final_comprehensive_verified_urls.json for most reliable results",
                "secondary": "Use final_comprehensive_all_urls.json for maximum variety",
                "fallback": "Use random_verified_sample.json for immediate testing"
            },
            "shortcut_setup": {
                "step_1": "Import final_comprehensive_verified_urls.json into your Shortcut",
                "step_2": "Use 'Get Item from List' with 'Random Item'",
                "step_3": "Add 'Get Contents of URL' to fetch the image",
                "step_4": "Add 'Set Wallpaper' action",
                "step_5": "Add error handling for failed requests"
            },
            "statistics": {
                "total_covers": len(covers_list),
                "verified_covers": len(verified_urls),
                "analysis_results_covers": len([c for c in covers_list if c.get('source') == 'analysis_results']),
                "pattern_1981_1999_covers": len(pattern_1981_1999_covers),
                "pattern_2000_2008_covers": len(pattern_2000_2008_covers),
                "pattern_2009_2019_covers": len(pattern_2009_2019_covers),
                "pattern_2020_2025_covers": len(pattern_2020_2025_covers),
                "date_range": f"{covers_list[0]['date']} to {covers_list[-1]['date']}" if covers_list else "No covers"
            }
        }
        
        with open('final_comprehensive_instructions.json', 'w') as f:
            json.dump(instructions, f, indent=2)
        
        return covers_list

def main():
    scraper = FinalComprehensiveScraper()
    covers = scraper.create_final_comprehensive_list()
    
    print(f"\nFinal Summary:")
    print(f"Total covers found: {len(covers)}")
    
    if covers:
        print(f"Date range: {covers[0]['date']} to {covers[-1]['date']}")
        
        # Show breakdown by source
        analysis_count = len([c for c in covers if c.get('source') == 'analysis_results'])
        pattern_1981_1999_count = len([c for c in covers if c.get('source') == 'pattern_1981_1999'])
        pattern_2000_2008_count = len([c for c in covers if c.get('source') == 'pattern_2000_2008'])
        pattern_2009_2019_count = len([c for c in covers if c.get('source') == 'pattern_2009_2019'])
        pattern_2020_2025_count = len([c for c in covers if c.get('source') == 'pattern_2020_2025'])
        
        print(f"Analysis results covers: {analysis_count}")
        print(f"1981-1999 pattern covers: {pattern_1981_1999_count}")
        print(f"2000-2008 pattern covers: {pattern_2000_2008_count}")
        print(f"2009-2019 pattern covers: {pattern_2009_2019_count}")
        print(f"2020-2025 pattern covers: {pattern_2020_2025_count}")
    
    print(f"\nRecommended files for iOS Shortcuts:")
    print(f"1. final_comprehensive_verified_urls.json - Most reliable (recommended)")
    print(f"2. final_comprehensive_all_urls.json - Maximum variety")
    print(f"3. random_verified_sample.json - Quick testing")
    print(f"4. final_comprehensive_instructions.json - Setup guide")

if __name__ == "__main__":
    main() 