#!/usr/bin/env python3
"""
Apply Final Layout to All Images
Reads shortcuts_text_overlay_covers.json and applies the final perfected layout to all 550 covers
- Bold dates at fixed position
- Centered text below badge with tight spacing
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

class FinalLayoutApplier:
    def __init__(self):
        self.json_file = "shortcuts_text_overlay_covers.json"
        self.output_dir = "images/optimized_final_with_text"
        self.original_dir = "images/original"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_json_data(self):
        """Load the shortcuts JSON file"""
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        return data["images"]
    
    def load_fonts(self):
        """Load fonts with fallback - try to get bold for date"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        font_large_bold = ImageFont.truetype(path, size=56, index=1)  # Index 1 = Bold
                    except:
                        font_large_bold = ImageFont.truetype(path, 56)
                    font_large = ImageFont.truetype(path, 56)
                    font_medium = ImageFont.truetype(path, 48)
                    return {
                        "large_bold": font_large_bold,
                        "large": font_large,
                        "medium": font_medium
                    }
        except Exception:
            pass
        default = ImageFont.load_default()
        return {"large_bold": default, "large": default, "medium": default}
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        try:
            month_int = int(month_num)
            return months[month_int - 1] if 1 <= month_int <= 12 else ''
        except:
            return ''
    
    def find_original_image(self, target_filename):
        """Find the original image that matches the target filename"""
        # Target format: YYYY_MM.jpg (e.g., 2010_12.jpg)
        # Find in original dir which has various formats
        
        # Try exact match in original dir first
        path = os.path.join(self.original_dir, target_filename)
        if os.path.exists(path):
            return path
        
        # Extract year and month from target
        parts = target_filename.replace('.jpg', '').split('_')
        if len(parts) != 2:
            return None
        year = parts[0]
        month = parts[1]
        
        # Convert month number to month name
        month_name = self.get_month_name(month)
        
        # Try various filename patterns
        patterns = [
            f"{year}_{month}.jpg",
            f"{month}_{year}.jpg",
            f"{month_name}{year}.jpg",
            f"{month_name}_{year}.jpg",
        ]
        
        # Try in original dir
        for pattern in patterns:
            path = os.path.join(self.original_dir, pattern)
            if os.path.exists(path):
                return path
        
        return None
    
    def apply_layout(self, image_path, metadata, output_filename):
        """Apply final layout to image"""
        try:
            # Open and format image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create lock screen with black background
            lock_screen_image = Image.new('RGB', self.lock_screen_size, (0, 0, 0))
            img_ratio = image.width / image.height
            target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
            
            if img_ratio > target_ratio:
                scale_factor = self.lock_screen_size[0] / image.width
                new_width = self.lock_screen_size[0]
                new_height = int(image.height * scale_factor)
            else:
                scale_factor = self.lock_screen_size[1] / image.height
                new_width = int(image.width * scale_factor)
                new_height = self.lock_screen_size[1]
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            x_offset = (self.lock_screen_size[0] - new_width) // 2
            y_offset = (self.lock_screen_size[1] - new_height) // 2
            lock_screen_image.paste(resized_image, (x_offset, y_offset))
            
            overlay_image = lock_screen_image
            draw = ImageDraw.Draw(overlay_image)
            fonts = self.load_fonts()
            
            # Colors
            text_color = (255, 255, 255)
            outline_color = (0, 0, 0)
            outline_width = 3
            text_x = 590  # Center horizontally
            
            # FIXED POSITIONING - Date at fixed position
            date_y = 2228
            
            # Build date line (BOLD)
            month_name = self.get_month_name(metadata.get('month', ''))
            date_text = f"{month_name} {metadata.get('year', '')}"
            date_font = fonts["large_bold"]
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            
            # Draw date with outline
            date_y_centered = date_y + (date_height // 2)
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, date_y_centered + dy), date_text, font=date_font, 
                                 fill=outline_color, anchor="mm")
            draw.text((text_x, date_y_centered), date_text, font=date_font, fill=text_color, anchor="mm")
            
            # Badge gap
            badge_gap = 80
            after_badge_y = date_y + date_height + badge_gap
            
            # Build lines BELOW badge
            below_lines = []
            if metadata.get('skater') and metadata['skater'].strip():
                below_lines.append((metadata['skater'].strip(), fonts["large"]))
            if metadata.get('trick') and metadata['trick'].strip():
                below_lines.append((metadata['trick'].strip(), fonts["medium"]))
            if metadata.get('location') and metadata['location'].strip():
                below_lines.append((metadata['location'].strip(), fonts["medium"]))
            
            # Tight spacing for all lines
            tight_spacing = 20
            
            # Calculate total height of all lines below badge
            total_height = 0
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                total_height += (bbox[3] - bbox[1])
            if len(below_lines) > 1:
                total_height += (len(below_lines) - 1) * tight_spacing
            
            # Center the entire block in available space below badge
            bottom_limit = 2520  # Home swipe
            available_space = bottom_limit - after_badge_y
            start_y_below = after_badge_y + ((available_space - total_height) // 2)
            
            # Draw lines BELOW badge with tight spacing
            current_draw_y = start_y_below
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                text_y = current_draw_y + (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), text, font=font, 
                                     fill=outline_color, anchor="mm")
                
                # Draw main text
                draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="mm")
                
                current_draw_y += text_height + tight_spacing
            
            # Save the image
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_all(self):
        """Process all covers from JSON"""
        print("🚀 Applying final layout to all 550 covers...")
        print("   Using: bold dates, centered text below badge, tight spacing (20px)")
        print()
        
        images_data = self.load_json_data()
        print(f"📁 Loaded {len(images_data)} covers from JSON")
        print()
        
        processed_count = 0
        failed_count = 0
        
        for i, image_data in enumerate(images_data):
            if (i + 1) % 50 == 0:
                print(f"Processing {i+1}/{len(images_data)}...")
            
            filename = image_data["filename"]
            metadata = image_data["metadata"]
            
            # Find the original image
            original_path = self.find_original_image(filename)
            if not original_path:
                print(f"  ⚠️  Could not find original for {filename}")
                failed_count += 1
                continue
            
            # Apply the layout
            output_path = self.apply_layout(original_path, metadata, filename)
            if output_path:
                processed_count += 1
            else:
                failed_count += 1
        
        print()
        print("✅ Processing complete!")
        print(f"   Successfully processed: {processed_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Output directory: {self.output_dir}")
        
        return processed_count

def main():
    applier = FinalLayoutApplier()
    applier.process_all()
    
    print()
    print("🎨 Final layout applied to all covers!")

if __name__ == "__main__":
    main()



