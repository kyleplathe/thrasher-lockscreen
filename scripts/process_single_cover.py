#!/usr/bin/env python3
"""
Process a single Thrasher cover with the final layout
Optimizes and adds text overlays to a single cover image
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class SingleCoverProcessor:
    def __init__(self):
        self.input_dir = Path("images/original")
        self.output_dir = Path("images/optimized_final_with_text")
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_fonts(self):
        """Load fonts with fallback"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        font_large_bold = ImageFont.truetype(path, size=56, index=1)
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
    
    def process_cover(self, filename):
        """Process a single cover image"""
        input_path = self.input_dir / filename
        
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return False
        
        # Load metadata from JSON
        metadata = self.load_metadata(filename)
        
        try:
            # Open image
            image = Image.open(input_path)
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
            month_name = self.get_month_name(metadata.get('month', 0))
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
            bottom_limit = 2520
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
            output_path = self.output_dir / filename
            overlay_image.save(output_path, quality=95)
            
            print(f"✅ Successfully processed {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            return False
    
    def load_metadata(self, filename):
        """Load metadata from JSON"""
        json_file = "shortcuts_text_overlay_covers.json"
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            for img in data.get('images', []):
                if img.get('filename') == filename:
                    return img.get('metadata', {})
        except Exception as e:
            print(f"Warning: Could not load metadata: {e}")
        
        # Fallback: try to parse from filename
        parts = filename.replace('.jpg', '').split('_')
        if len(parts) == 2:
            return {
                'year': parts[0],
                'month': parts[1]
            }
        
        return {}

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 process_single_cover.py <filename>")
        print("Example: python3 process_single_cover.py 2025_12.jpg")
        sys.exit(1)
    
    filename = sys.argv[1]
    processor = SingleCoverProcessor()
    processor.process_cover(filename)

if __name__ == "__main__":
    main()

