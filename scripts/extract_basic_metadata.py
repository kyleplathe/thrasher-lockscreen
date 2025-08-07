#!/usr/bin/env python3
"""
Extract Basic Metadata Script
Extracts basic metadata from image filenames and creates a foundation for manual metadata entry
"""

import os
import json
import re
from datetime import datetime

class BasicMetadataExtractor:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_file = "basic_metadata_extracted.json"
        
    def extract_metadata_from_filename(self, filename):
        """Extract basic metadata from filename"""
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        metadata = {
            "filename": filename,
            "date": "",
            "year": "",
            "month": "",
            "month_name": "",
            "skaters": [],
            "tricks": [],
            "obstacles": [],
            "location": "",
            "photographer": "",
            "notes": "",
            "source": "filename_analysis"
        }
        
        # Extract date information
        date_patterns = [
            r'(\d{4})_(\d{2})',  # YYYY_MM format
            r'(\d{2})(\d{2})',   # YYMM format (like 2505 for May 2025)
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, name)
            if match:
                if len(match.groups()) == 2:
                    year, month = match.groups()
                    
                    # Handle 2-digit year format
                    if len(year) == 2:
                        year = "20" + year
                    
                    metadata["year"] = year
                    metadata["month"] = month
                    metadata["date"] = f"{year}-{month}-01"
                    metadata["month_name"] = self.get_month_name(int(month))
                    break
        
        # Extract potential skater names (common patterns in Thrasher covers)
        skater_patterns = [
            r'([A-Z][a-z]+_[A-Z][a-z]+)',  # First_Last
            r'([A-Z][a-z]+_[A-Z][a-z]+_[A-Z][a-z]+)',  # First_Middle_Last
        ]
        
        for pattern in skater_patterns:
            matches = re.findall(pattern, name)
            for match in matches:
                skater = match.replace('_', ' ')
                if skater not in metadata["skaters"]:
                    metadata["skaters"].append(skater)
        
        # Extract potential tricks from filename
        trick_keywords = [
            'kickflip', 'heelflip', 'ollie', '360', '180', 'shove', 'varial',
            'double', 'triple', 'quad', 'backside', 'frontside', 'switch',
            'nollie', 'fakie', 'nose', 'tail', 'grind', 'slide', 'manual',
            '50_50', 'boardslide', 'lipslide', 'crooked', 'smith', 'feeble',
            'nosegrind', 'tailgrind', 'overcrook', 'salad', 'soup', 'burnett'
        ]
        
        name_lower = name.lower()
        for trick in trick_keywords:
            if trick in name_lower:
                metadata["tricks"].append(trick)
        
        # Extract potential obstacles
        obstacle_keywords = [
            'rail', 'ledge', 'stairs', 'gap', 'bank', 'quarter', 'half',
            'ramp', 'bowl', 'pool', 'curb', 'handrail', 'kicker', 'funbox',
            'pyramid', 'spine', 'wall', 'wallride', 'tree', 'pole', 'bench'
        ]
        
        for obstacle in obstacle_keywords:
            if obstacle in name_lower:
                metadata["obstacles"].append(obstacle)
        
        # Extract potential locations
        location_patterns = [
            r'in_([A-Z][a-z]+)',  # in_[Location]
            r'at_([A-Z][a-z]+)',  # at_[Location]
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, name)
            if match:
                metadata["location"] = match.group(1)
                break
        
        return metadata
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def process_all_images(self):
        """Process all images to extract basic metadata"""
        print("Extracting basic metadata from image filenames...")
        
        if not os.path.exists(self.input_dir):
            print(f"Input directory {self.input_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to process")
        
        all_metadata = {
            "version": "1.0",
            "description": "Basic metadata extracted from image filenames",
            "total_images": len(image_files),
            "metadata": {}
        }
        
        for i, filename in enumerate(image_files):
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Extract metadata from filename
            metadata = self.extract_metadata_from_filename(filename)
            all_metadata["metadata"][filename] = metadata
        
        # Save metadata
        with open(self.output_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        
        print(f"\nCompleted! Extracted metadata for {len(image_files)} images.")
        print(f"Output file: {self.output_file}")
        
        # Print some statistics
        self.print_statistics(all_metadata)
        
        return all_metadata
    
    def print_statistics(self, metadata):
        """Print statistics about the extracted metadata"""
        print("\n📊 Metadata Statistics:")
        
        # Count images with different types of metadata
        with_skaters = sum(1 for m in metadata["metadata"].values() if m["skaters"])
        with_tricks = sum(1 for m in metadata["metadata"].values() if m["tricks"])
        with_obstacles = sum(1 for m in metadata["metadata"].values() if m["obstacles"])
        with_location = sum(1 for m in metadata["metadata"].values() if m["location"])
        
        print(f"Images with skater info: {with_skaters}")
        print(f"Images with trick info: {with_tricks}")
        print(f"Images with obstacle info: {with_obstacles}")
        print(f"Images with location info: {with_location}")
        
        # Show some examples
        print("\n📝 Sample Extracted Metadata:")
        sample_count = 0
        for filename, data in metadata["metadata"].items():
            if sample_count < 5:  # Show first 5 examples
                print(f"\n{filename}:")
                if data["skaters"]:
                    print(f"  Skaters: {', '.join(data['skaters'])}")
                if data["tricks"]:
                    print(f"  Tricks: {', '.join(data['tricks'])}")
                if data["obstacles"]:
                    print(f"  Obstacles: {', '.join(data['obstacles'])}")
                if data["location"]:
                    print(f"  Location: {data['location']}")
                sample_count += 1

def main():
    extractor = BasicMetadataExtractor()
    extractor.process_all_images()

if __name__ == "__main__":
    main() 