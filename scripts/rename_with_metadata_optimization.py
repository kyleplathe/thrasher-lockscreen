#!/usr/bin/env python3
"""
Rename Images with Metadata Optimization
Renames images to YYYY_MM format and creates metadata mapping
"""

import os
import re
import json
import shutil
from datetime import datetime

class ImageRenamerWithMetadata:
    def __init__(self):
        self.original_dir = "images/original"
        self.renamed_dir = "images/renamed_clean"
        self.metadata_mapping_file = "metadata_image_mapping.json"
        
        # Create directories
        os.makedirs(self.renamed_dir, exist_ok=True)
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename using various patterns"""
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Pattern 1: MonthYear (e.g., January1981, Feb1981)
        month_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d{4})'
        match = re.search(month_pattern, name, re.IGNORECASE)
        if match:
            month, year = match.groups()
            return self.parse_month_year(month, year)
        
        # Pattern 2: YYYY_MM format (e.g., 2024_11)
        year_month_pattern = r'(\d{4})_(\d{1,2})'
        match = re.search(year_month_pattern, name)
        if match:
            year, month = match.groups()
            try:
                return datetime(int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 3: MM_YYYY format (e.g., 11_2024)
        month_year_pattern = r'(\d{1,2})_(\d{4})'
        match = re.search(month_year_pattern, name)
        if match:
            month, year = match.groups()
            try:
                return datetime(int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 4: CV1TH format (e.g., CV1TH0124 for Jan 2024)
        cv_pattern = r'CV1TH(\d{2})(\d{2})'
        match = re.search(cv_pattern, name)
        if match:
            month, year = match.groups()
            try:
                return datetime(2000 + int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 5: 25_XX format (e.g., 25_01 for Jan 2025)
        year25_pattern = r'25_(\d{2})'
        match = re.search(year25_pattern, name)
        if match:
            month = match.group(1)
            try:
                return datetime(2025, int(month), 1)
            except ValueError:
                pass
        
        # Pattern 6: 09_25 format (e.g., 09_25 for Sep 2025)
        month25_pattern = r'(\d{2})_25'
        match = re.search(month25_pattern, name)
        if match:
            month = match.group(1)
            try:
                return datetime(2025, int(month), 1)
            except ValueError:
                pass
        
        # Default to current date if no pattern matches
        return datetime.now()
    
    def parse_month_year(self, month_str, year_str):
        """Parse month and year strings to datetime"""
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        month = month_map.get(month_str.lower(), 1)
        year = int(year_str)
        return datetime(year, month, 1)
    
    def rename_images_with_metadata_mapping(self):
        """Rename images and create metadata mapping"""
        print("Renaming images with YYYY_MM format and creating metadata mapping...")
        
        if not os.path.exists(self.original_dir):
            print(f"Original directory {self.original_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.original_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} original images")
        
        # Extract dates and sort
        dated_files = []
        for filename in image_files:
            date = self.extract_date_from_filename(filename)
            dated_files.append((date, filename))
        
        # Sort by date
        dated_files.sort(key=lambda x: x[0])
        
        # Create metadata mapping
        metadata_mapping = {
            "image_mapping": {},
            "date_to_images": {},
            "statistics": {
                "total_images": len(dated_files),
                "year_range": {},
                "duplicate_dates": []
            }
        }
        
        # Track duplicate dates
        date_counts = {}
        
        # Rename files with YYYY_MM format
        renamed_count = 0
        for date, filename in dated_files:
            # Create new filename with YYYY_MM format
            extension = os.path.splitext(filename)[1]
            new_filename = f"{date.strftime('%Y_%m')}{extension}"
            
            # Handle duplicate dates by adding suffix
            if new_filename in date_counts:
                date_counts[new_filename] += 1
                base_name = new_filename.replace(extension, '')
                new_filename = f"{base_name}_{date_counts[new_filename]:02d}{extension}"
            else:
                date_counts[new_filename] = 0
            
            # Copy to renamed directory
            old_path = os.path.join(self.original_dir, filename)
            new_path = os.path.join(self.renamed_dir, new_filename)
            
            try:
                shutil.copy2(old_path, new_path)
                print(f"✓ {filename} → {new_filename}")
                renamed_count += 1
                
                # Add to metadata mapping
                metadata_mapping["image_mapping"][new_filename] = {
                    "original_filename": filename,
                    "date": date.strftime('%Y-%m-01'),
                    "year": date.year,
                    "month": date.month,
                    "year_month": date.strftime('%Y_%m')
                }
                
                # Add to date mapping
                date_key = date.strftime('%Y_%m')
                if date_key not in metadata_mapping["date_to_images"]:
                    metadata_mapping["date_to_images"][date_key] = []
                metadata_mapping["date_to_images"][date_key].append(new_filename)
                
                # Track year statistics
                year = date.year
                if year not in metadata_mapping["statistics"]["year_range"]:
                    metadata_mapping["statistics"]["year_range"][year] = 0
                metadata_mapping["statistics"]["year_range"][year] += 1
                
            except Exception as e:
                print(f"✗ Error copying {filename}: {e}")
        
        # Find duplicate dates
        for date_key, images in metadata_mapping["date_to_images"].items():
            if len(images) > 1:
                metadata_mapping["statistics"]["duplicate_dates"].append({
                    "date": date_key,
                    "images": images
                })
        
        # Save metadata mapping
        with open(self.metadata_mapping_file, 'w') as f:
            json.dump(metadata_mapping, f, indent=2)
        
        print(f"\nRenamed {renamed_count} images")
        print(f"Renamed images saved to: {self.renamed_dir}")
        print(f"Metadata mapping saved to: {self.metadata_mapping_file}")
        
        # Print statistics
        print(f"\nStatistics:")
        print(f"Total images: {metadata_mapping['statistics']['total_images']}")
        print(f"Year range: {min(metadata_mapping['statistics']['year_range'].keys())} - {max(metadata_mapping['statistics']['year_range'].keys())}")
        print(f"Duplicate dates: {len(metadata_mapping['statistics']['duplicate_dates'])}")
        
        return renamed_count, metadata_mapping
    
    def create_4ply_optimized_structure(self):
        """Create structure optimized for 4ply metadata integration"""
        print("\nCreating 4ply-optimized structure...")
        
        # Read metadata mapping
        with open(self.metadata_mapping_file, 'r') as f:
            metadata_mapping = json.load(f)
        
        # Create 4ply-optimized structure
        fourply_structure = {
            "version": "1.0",
            "description": "Thrasher magazine covers optimized for 4ply metadata integration",
            "image_data": {},
            "metadata_ready": True,
            "date_format": "YYYY_MM",
            "statistics": metadata_mapping["statistics"]
        }
        
        # Process each image
        for new_filename, data in metadata_mapping["image_mapping"].items():
            fourply_structure["image_data"][new_filename] = {
                "original_filename": data["original_filename"],
                "date": data["date"],
                "year": data["year"],
                "month": data["month"],
                "year_month": data["year_month"],
                "file_path": f"images/renamed_clean/{new_filename}",
                "metadata_placeholder": {
                    "skaters": [],
                    "tricks": [],
                    "obstacles": [],
                    "location": "",
                    "photographer": "",
                    "notes": ""
                }
            }
        
        # Save 4ply-optimized structure
        fourply_file = "fourply_optimized_structure.json"
        with open(fourply_file, 'w') as f:
            json.dump(fourply_structure, f, indent=2)
        
        print(f"Created 4ply-optimized structure: {fourply_file}")
        print(f"Contains {len(fourply_structure['image_data'])} images ready for metadata integration")
        
        return fourply_file

def main():
    renamer = ImageRenamerWithMetadata()
    
    print("Thrasher Image Renamer with Metadata Optimization")
    print("=" * 55)
    
    # Step 1: Rename images and create metadata mapping
    renamed_count, metadata_mapping = renamer.rename_images_with_metadata_mapping()
    
    # Step 2: Create 4ply-optimized structure
    fourply_file = renamer.create_4ply_optimized_structure()
    
    print(f"\nSummary:")
    print(f"✓ Renamed {renamed_count} images to YYYY_MM format")
    print(f"✓ Created metadata mapping: {renamer.metadata_mapping_file}")
    print(f"✓ Created 4ply-optimized structure: {fourply_file}")
    print(f"\nNext steps:")
    print(f"1. Review renamed images in '{renamer.renamed_dir}'")
    print(f"2. Use '{fourply_file}' for 4ply metadata integration")
    print(f"3. Process renamed images with optimization scripts")

if __name__ == "__main__":
    main() 