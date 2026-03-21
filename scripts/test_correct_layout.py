#!/usr/bin/env python3
"""
Test Correct Layout for Badge
- Date ABOVE the badge area
- Skater/trick/location BELOW the badge area
- All text centered between widgets and home swipe
"""

import os
from PIL import Image, ImageDraw, ImageFont

class CorrectLayoutTester:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/correct_layout_tests"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test different badge Y positions (where the gap is)
        self.badge_y_positions = [2370, 2380, 2390, 2400]
        
        # Test covers
        self.test_covers = [
            {"filename": "January1981.jpg", "lines": 1, "metadata": {"year": "1981", "month": "01"}},
            {"filename": "February1981.jpg", "lines": 2, "metadata": {"year": "1981", "month": "02", "skater": "Chris Stople"}},
            {"filename": "March1981.jpg", "lines": 3, "metadata": {"year": "1981", "month": "03", "skater": "Chris Miller", "trick": "FS Air"}},
            {"filename": "November1991.jpg", "lines": 4, "metadata": {"year": "1991", "month": "11", "skater": "eric dressen", "trick": "nose bonk tail grab", "location": "Los Angeles CA"}},
        ]
        
    def load_fonts(self):
        """Load fonts with fallback"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
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
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def create_layout(self, badge_y, test_data):
        """Create layout with date above badge, info below"""
        try:
            filename = test_data["filename"]
            metadata = test_data["metadata"]
            expected_lines = test_data["lines"]
            
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
            text_x = 590  # Center horizontally
            
            # Layout structure:
            # ABOVE badge: Date line (centered in its space)
            # BELOW badge: Skater, trick, location (centered in their space)
            
            line_spacing = 50  # Moderate spacing
            
            # Calculate space ABOVE badge (from somewhere above to badge_y)
            # If badge_y = 2380, and space starts around 2250, we have ~130px for date
            space_above_badge_top = 2250  # Approximate start of text area
            space_above_badge = badge_y - space_above_badge_top
            
            # Calculate space BELOW badge (from badge_y + badge_height to bottom)
            badge_height = 80  # Approximate badge height
            space_below_badge_top = badge_y + badge_height
            space_below_badge_bottom = 2520  # Just above home swipe
            space_below_badge = space_below_badge_bottom - space_below_badge_top
            
            # Build lines ABOVE badge
            month_name = self.get_month_name(int(metadata["month"]))
            date_text = f"{month_name} {metadata['year']}"
            date_font = fonts["large"]
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            
            # Center date in space above badge
            date_y = space_above_badge_top + (space_above_badge // 2)
            date_y_centered = date_y + (date_height // 2)
            
            # Draw date with outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, date_y_centered + dy), date_text, font=date_font, 
                                 fill=outline_color, anchor="mm")
            draw.text((text_x, date_y_centered), date_text, font=date_font, fill=text_color, anchor="mm")
            
            # Build lines BELOW badge
            below_lines = []
            if metadata.get("skater"):
                below_lines.append((metadata["skater"], fonts["large"]))
            if metadata.get("trick"):
                below_lines.append((metadata["trick"], fonts["medium"]))
            if metadata.get("location"):
                below_lines.append((metadata["location"], fonts["medium"]))
            
            # Calculate total height of lines below badge
            total_below_height = 0
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                total_below_height += (bbox[3] - bbox[1])
            if len(below_lines) > 1:
                total_below_height += (len(below_lines) - 1) * line_spacing
            
            # Center all lines below badge in their space
            start_y_below = space_below_badge_top + (space_below_badge // 2) - (total_below_height // 2)
            
            # Draw lines below badge
            current_y = start_y_below
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                text_y = current_y + (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), text, font=font, 
                                     fill=outline_color, anchor="mm")
                
                # Draw main text
                draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="mm")
                
                current_y += text_height + line_spacing
            
            # Save
            output_filename = f"badge{badge_y}_{expected_lines}line_{filename}"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ Badge Y={badge_y}, {expected_lines} lines: {output_filename}")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_tests(self):
        """Test all badge positions"""
        print("🧪 Testing Correct Layout (Date Above, Info Below Badge)")
        print("━" * 70)
        print("📱 Layout:")
        print("   - Date: Centered ABOVE badge area")
        print("   - Badge: Floating in gap")
        print("   - Skater/trick/location: Centered BELOW badge area")
        print("━" * 70)
        print()
        
        for test_cover in self.test_covers:
            print(f"Testing {test_cover['lines']}-line cover: {test_cover['filename']}")
            for badge_y in self.badge_y_positions:
                self.create_layout(badge_y, test_cover)
            print()
        
        print("✅ Correct layout tests complete!")
        print(f"📁 Output: {self.output_dir}/")

if __name__ == "__main__":
    tester = CorrectLayoutTester()
    tester.run_tests()



