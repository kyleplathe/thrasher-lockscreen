# 🛹 Thrasher Lock Screen Archive

**550+ Thrasher Magazine covers with 4ply metadata text overlays, optimized for iPhone lock screens with iOS Shortcuts automation. Daily random covers with skater/trick/location information from 1981-2025.**

## 🎯 Overview

This project provides a complete solution for automatically setting Thrasher Magazine covers as your iPhone lock screen. Features include:

- **550+ verified cover URLs** spanning 1981-2025
- **Text overlays with 4ply metadata** (skaters, tricks, locations)
- **iPhone-optimized images** (1080x1920 resolution)
- **iOS Shortcuts integration** for daily automation
- **Rich metadata** from 4plymag.com (skaters, tricks, obstacles)
- **Random daily selection** with fallback mechanisms

## 📊 Project Status

- ✅ **URLs Collected**: 550+ verified Thrasher cover URLs
- ✅ **Scraping Scripts**: Complete automation pipeline
- ✅ **Image Processing**: iPhone lock screen optimization
- ✅ **Metadata Integration**: 4plymag scraper for detailed info
- ✅ **Image Download**: All 550+ covers processed and optimized
- ✅ **Text Overlays**: Complete with skater/trick/location metadata
- 🔄 **GitHub Actions**: Automated updates

## 🚀 Quick Start

### 1. Download and Process Images

```bash
# Install dependencies
pip install -r requirements.txt

# Download and optimize all 550+ covers
python scripts/final_comprehensive_scraper.py
python scripts/image_optimizer.py

# Apply text overlays with 4ply metadata
python scripts/apply_text_overlays_all.py
```

### 2. iOS Shortcuts Setup

1. Open **Shortcuts** app on your iPhone
2. Create new shortcut
3. Add **"Get Contents of URL"** action
4. Use: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/shortcuts_text_overlay_covers.json`
5. Add **"Get Random Item from List"**
6. Add **"Get Contents of URL"** to download image
7. Add **"Set Wallpaper"** action

## 📁 Project Structure

```
thrasher-lockscreen/
├── 📂 images/
│   ├── optimized_final_with_text/ # iPhone-ready covers with text overlays
│   ├── original/                   # Original downloaded covers
│   ├── optimized_final/            # Optimized images without text
│   └── text_overlay_samples/       # Sample images for testing
├── 📂 scripts/                     # Automation scripts
│   ├── apply_text_overlays_all.py  # Main text overlay script
│   ├── final_comprehensive_scraper.py
│   ├── 4plymag_metadata_scraper.py
│   ├── image_optimizer.py
│   ├── create_text_overlay_images.py
│   └── create_text_overlay_shortcuts_json.py
├── 📂 data/                        # Data files and metadata
│   └── shortcuts/                  # iOS Shortcuts JSON files
├── 📄 shortcuts_text_overlay_covers.json # Main iOS Shortcuts file
├── 📄 text_overlay_config.json     # Text overlay configuration
└── 📄 README.md
```

## 🛠️ Scripts

### `apply_text_overlays_all.py`
**Main script** that applies text overlays to all optimized images with:
- **Skater names** from 4plymag metadata
- **Trick descriptions** and obstacle types
- **Location information** when available
- **Date formatting** for consistent display

### `final_comprehensive_scraper.py`
Downloads all 550+ verified Thrasher cover images with error handling and progress tracking.

### `image_optimizer.py`
Optimizes images for iPhone lock screens:
- **Resolution**: 1080x1920 (perfect iPhone ratio)
- **File Size**: <500KB per image
- **Quality**: 85% JPEG compression

### `4plymag_metadata_scraper.py`
Extracts detailed metadata from [4plymag.com](http://4plymag.com/thrashersearch/):
- Skater names
- Trick descriptions
- Obstacle types
- Locations

### `create_text_overlay_images.py`
Creates text overlay images with customizable positioning and styling.

### `create_text_overlay_shortcuts_json.py`
Creates iOS Shortcuts integration files for the text overlay covers.

## 📱 iOS Shortcuts Integration

### Direct GitHub Access
All data is hosted on GitHub for easy iOS Shortcuts integration:

- **Text Overlay Covers**: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/shortcuts_text_overlay_covers.json`
- **Optimized Covers**: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/shortcuts_final_optimized_covers.json`

### Automation Features
- **Daily random selection** from 550+ covers
- **Metadata display** in notifications
- **Error handling** with fallback covers
- **Offline caching** for reliability

## 🎨 Image Specifications

### Optimization Details
- **Target Resolution**: 1080x1920 pixels
- **Aspect Ratio**: 9:16 (perfect for iPhone lock screens)
- **File Format**: JPEG with 85% quality
- **File Size**: <500KB per image
- **Processing**: Lanczos resampling for high quality

### Text Overlay Features
Each cover includes rich information:
- 📅 **Date**: "December 2020"
- 👤 **Skaters**: "Tony Hawk, Rodney Mullen"
- 🛹 **Tricks**: "kickflip, 360 flip"
- 🏗️ **Obstacles**: "rail, stairs"
- 📍 **Location**: "Los Angeles, CA"

## 🔄 Automation Workflow

### Daily Operation
1. **iOS Shortcut triggers** (manual or automated)
2. **Fetches latest data** from GitHub
3. **Randomly selects** a cover from 550+ options
4. **Downloads optimized image with text overlay**
5. **Applies to lock screen**
6. **Displays metadata** in notification

### Weekly Updates
1. **GitHub Actions** automatically scrape new covers
2. **Image optimization** processes new additions
3. **Text overlay application** with metadata
4. **Repository updates** with new content

## 📈 Coverage Statistics

### Time Period: 1981-2025 (45 years!)
- **Total Covers**: 550+ verified URLs
- **Date Range**: January 1981 to September 2025
- **Coverage**: Complete archive spanning nearly half a century
- **Quality**: All covers verified and accessible

### Why 550+ vs Expected 537?
The extra covers come from:
- **Special editions** and anniversary issues
- **Multiple covers per month** in some years
- **International releases** and variants
- **Limited edition** and promotional covers

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip package manager
- Internet connection for image downloads

### Installation
```bash
# Clone the repository
git clone https://github.com/kyleplathe/thrasher-lockscreen.git
cd thrasher-lockscreen

# Install dependencies
pip install -r requirements.txt
```

### First Run
```bash
# Download all covers
python scripts/final_comprehensive_scraper.py

# Optimize for iPhone
python scripts/image_optimizer.py

# Apply text overlays with metadata
python scripts/apply_text_overlays_all.py

# Create iOS Shortcuts files
python scripts/create_text_overlay_shortcuts_json.py
```

## 🔧 Customization

### Text Overlay Configuration
Edit `text_overlay_config.json` to customize:
- **Text positioning** (x, y coordinates)
- **Font size** and style
- **Metadata display** (show/hide skater, trick, location)
- **Color scheme** and transparency

### Image Optimization
Edit `scripts/image_optimizer.py` to adjust:
- **Resolution**: Change target dimensions
- **Quality**: Adjust JPEG compression
- **Format**: Switch to PNG or other formats

### Metadata Sources
Modify `scripts/4plymag_metadata_scraper.py` to:
- **Add new sources** for cover information
- **Enhance data extraction** for better accuracy
- **Customize metadata fields** for your needs

## 📝 Adding New Covers

### Manual Process
1. Update `final_comprehensive_scraper.py` with new URL patterns
2. Run the scraper to download new covers
3. Process images with `image_optimizer.py`
4. Apply text overlays with `apply_text_overlays_all.py`
5. Update JSON files in root directory

### Improving Metadata
1. Enhance `4plymag_metadata_scraper.py` for better data extraction
2. Add new metadata sources for comprehensive coverage
3. Validate and clean extracted data for consistency

## 🤝 Contributing

### How to Help
- **Report bugs** in GitHub Issues
- **Suggest improvements** for image processing
- **Add new metadata sources** for better cover information
- **Test iOS Shortcuts** on different devices

### Getting Help
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `docs/` folder for detailed guides
- **Examples**: See root directory for sample JSON structures

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**🎉 Ready to rock your iPhone lock screen with daily Thrasher covers featuring rich 4ply metadata!**
