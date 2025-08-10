# 🛹 Thrasher Lock Screen Archive

**550+ Thrasher Magazine covers optimized for iPhone lock screens with iOS Shortcuts automation. Daily random covers with skater/trick metadata from 1981-2025.**

## 🎯 Overview

This project provides a complete solution for automatically setting Thrasher Magazine covers as your iPhone lock screen. Features include:

- **550+ verified cover URLs** spanning 1981-2025
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
- 🔄 **GitHub Actions**: Automated updates

## 🚀 Quick Start

### 1. Download and Process Images

```bash
# Install dependencies
pip install -r requirements.txt

# Download and optimize all 550+ covers
python scripts/final_comprehensive_scraper.py
python scripts/image_optimizer.py
```

### 2. iOS Shortcuts Setup

1. Open **Shortcuts** app on your iPhone
2. Create new shortcut
3. Add **"Get Contents of URL"** action
4. Use: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/data/shortcuts/optimized_covers.json`
5. Add **"Get Random Item from List"**
6. Add **"Get Contents of URL"** to download image
7. Add **"Set Wallpaper"** action

## 📁 Project Structure

```
thrasher-lockscreen/
├── 📂 images/
│   ├── optimized/           # iPhone-ready cover images (550+ covers)
│   └── original/            # Original downloaded covers
├── 📂 data/                 # Data files and metadata
│   └── shortcuts/           # iOS Shortcuts JSON files
├── 📂 scripts/              # Automation scripts
│   ├── final_comprehensive_scraper.py
│   ├── 4plymag_metadata_scraper.py
│   ├── image_optimizer.py
│   ├── download_images.py
│   ├── create_shortcuts_json.py
│   └── optimize_local_images.py
├── 📂 docs/                 # Documentation
└── 📄 README.md
```

## 🛠️ Scripts

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

### `create_shortcuts_json.py`
Creates iOS Shortcuts integration files for easy automation.

### `download_images.py`
Downloads images from verified URLs with error handling.

### `optimize_local_images.py`
Optimizes local images for iPhone lock screen dimensions.

## 📱 iOS Shortcuts Integration

### Direct GitHub Access
All data is hosted on GitHub for easy iOS Shortcuts integration:

- **Cover URLs**: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/data/shortcuts/optimized_covers.json`
- **Date Pairs**: `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/data/shortcuts/final_comprehensive_date_url_pairs.json`

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

### Metadata Integration
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
4. **Downloads optimized image**
5. **Applies to lock screen**
6. **Displays metadata** in notification

### Weekly Updates
1. **GitHub Actions** automatically scrape new covers
2. **Image optimization** processes new additions
3. **Metadata enhancement** from 4plymag
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

# Create iOS Shortcuts files
python scripts/create_shortcuts_json.py
```

## 🔧 Customization

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
4. Update JSON files in `data/shortcuts/`

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
- **Examples**: See `data/shortcuts/` for sample JSON structures

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**🎉 Ready to rock your iPhone lock screen with daily Thrasher covers!**
