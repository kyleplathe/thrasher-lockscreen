#!/usr/bin/env python3
"""
Test Text Layout with Space for Reduce Interruptions Badge
Creates layout with gap for the badge in the middle of the text
"""

import os
from PIL import Image, ImageDraw, ImageFont

class BadgeSpaceLayoutTester:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/badge_space_tests"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test different layouts
        self.layouts = [
            {
                "name": "Layout A - Current (no gap)",
                "y_center": 2390,
                "gap_before_skater": False
            },
            {
                "name": "Layout B - Gap before skater (date on top)",
                "y_center": 2390,
                "gap_before_skater": True
            },
            {
                "name": "Layout C - Gap in middle (symmetrical)",
                "y_center": 2410,
                "gap_before_skater": False,
                "gap_in_middle": True
            },
            {
                "name": "Layout D - Just date + trick/location",
                "y_center": 2440,
                "skip_skater": True
            }
        ]
        
        # Test cover matching screenshot
        self.test_cover = {
            "filename": "November1991.jpg",
            "metadata": {
                "year": "1991", "month": "11",
                "skater": "eric dressen",
                "trick": "nose bonk tail grab",
                "location": "Los Angeles CA"
            }
        }
        
    def load_fonts(self):
        """Load fonts with fallback"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    font_large = ImageFont.truetype(path, 56)
                    font_medium = ImageFont.truetype(path, 48)
                    return {"large": font_large, "medium": font_medium}
        except Exception:
            pass
        default = ImageFont.load_default()
        return {"large": default, "medium": default}
    
    def create_image_with_text(self, layout, test_data):
        """Create image with specific layout"""
        try:
            filename = test_data["filename"]
            metadata = test_data["metadata"]
            
            input_path = os.path.join(self.input_dir, filename)
            if not os.path.exists(input_path):
                print(f"  ⚠️  {filename} not found")
                return None
            
            # Open and format image
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
            text_x = 590  # Center
            
            # Build lines based on layout
            lines = []
            line_spacing = 56  # Closer spacing
            
            # Date line
            lines.append(("date", f"November 1991", fonts["large"]))
            
            # Gap for badge if needed
            if layout.get("gap_before_skater"):
                lines.append(("gap", None, None))
            
            # Skater line (if not skipped)
            if not layout.get("skip_skater"):
                lines.append(("skater", metadata["skater"], fonts["large"]))
            
            # Gap in middle for symmetrical layout
            if layout.get("gap_in_middle"):
                lines.append(("gap", None, None))
            
            # Trick line
            if metadata.get("trick"):
                lines.append(("trick", metadata["trick"], fonts["medium"]))
            
            # Location line
            if metadata.get("location"):
                lines.append(("location", metadata["location"], fonts["medium"]))
            
            # Calculate total height (without gaps)
            total_height = 0
            for line_type, text, font in lines:
                if line_type == "gap":
                    total_height += 60  # Gap space
                else:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    total_height += (bbox[3] - bbox[1])
            
            if len([l for l in lines if l[0] != "gap"]) > 1:
                total_height += (len([l for l in lines if l[0] != "gap"]) - 1) * line_spacing
            
            # Calculate starting Y to center the block
            y_center = layout["y_center"]
            start_y = y_center - (total_height // 2)
            
            # Draw lines
            current_y = start_y
            for line_type, text, font in lines:
                if line_type == "gap":
                    current_y += 60
                    continue
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                text_width = bbox[2] - bbox[0]
                
                y = current_y + (text_height // 2)
                x = text_x - (text_width // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, 
                                     fill=outline_color, anchor="mm")
                
                # Draw main text with anchor="mm" for perfect centering
                draw.text((text_x, y), text, font=font, fill=text_color, anchor="mm")
                
                current_y += text_height + line_spacing
            
            # Save
            layout_name = layout["name"].split(" - ")[1].lower().replace(" ", "_").replace("/", "_").replace("+", "_")
            output_filename = f"{layout_name}_{filename}"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ Created: {output_filename}")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def run_tests(self):
        """Test all layouts"""
        print("🧪 Testing Text Layouts with Badge Space")
        print("━" * 70)
        print("📱 Matching screenshot layout")
        print("🎯 Goal: Space for 'Reduce Interruptions' badge")
        print("━" * 70)
        print()
        
        for layout in self.layouts:
            print(f"Testing: {layout['name']}")
            self.create_image_with_text(layout, self.test_cover)
        
        print()
        print("✅ Layout tests complete!")
        print(f"📁 Output: {self.output_dir}/")

if __name__ == "__main__":
    tester = BadgeSpaceLayoutTester()
    tester.run_tests()

