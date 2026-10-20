
# 🛹 Thrasher Lock Screen - Private Repository

**⚠️ This is a private repository containing personal lock screen images and automation tools.**

## 🔒 Security Notice

This repository is kept private to prevent malicious actors from hijacking the image URLs and potentially changing users' lock screens to inappropriate content. The automation methods and shortcuts are shared below for educational purposes, but the actual image data remains secure.

![December 2026 Cover](https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/original/2026_12.jpg)

## 🎯 What This Project Does

This project provides **565 Thrasher Magazine covers** from 1981-2026 that can be automatically set as iPhone lock screens. Each cover includes:

- 📅 **Date** (month and year)
- 👤 **Skater name** 
- 🛹 **Trick description**
- 📍 **Location** (when available)

## 📊 Data Sources

The complete collection of 565 covers was built by scraping:
- **[Thrasher Magazine website](https://www.thrashermagazine.com/articles/magazine/)** - Current covers from 1981-present
- **[4Ply Magazine archive](https://archive.4plymag.com)** - Metadata from 1981-2019
- Manual metadata extraction from cover filenames and descriptions
- Text overlay generation with skater names, tricks, and locations

## 🚀 How to Use the Thrasher Lock Screen Shortcut

### Download the Pre-Built Shortcut ⭐ **EASIEST**
1. **Tap this link on your iPhone**: [Download Thrasher Shortcut](https://www.icloud.com/shortcuts/2374fd29de134e4788b63084f8872bbb)
2. **Tap "Get Shortcut"** when prompted
3. **Test it** by tapping the ▶️ button
4. **Add the cover choice** with the menu steps below (this iCloud copy still picks a random cover until you do)

## 📱 How to Use Daily

### Option 1: Manual (Tap to change)
- Open Shortcuts app
- Tap your Thrasher shortcut
- Choose **Pick a date**, **Most recent cover**, or **Random cover**
- **Pick a date** opens a date picker. The month and year choose the issue. The day is ignored.
- If that month has more than one cover, a second list lets you pick which one.
- Lock screen changes to that cover

**Update the shortcut already on your phone** (the iCloud copy always picks at random until you add this menu):

1. Open **Thrasher Covers, Baby** and delete the **Get Dictionary Value** action for `images` and the **Get Item from List** action under it.
2. After **Get Dictionary**, add **Choose from Menu**. Prompt: `Which cover?` Items, in order: **Pick a date**, **Most recent cover**, **Random cover**.
3. **Pick a date**
   - **Ask for Input**, type **Date**, prompt `Which issue? The day is ignored.`
   - **Format Date**, custom format `yyyy_MM`
   - **Get Dictionary Value** `covers_by_month`, then **Get Dictionary Value** again using that formatted date as the key. That value is the list of issue names for the month.
   - **Count** the list. If it is less than 1, show an alert `No Thrasher cover for that month.` and **Stop Shortcut**.
   - Otherwise, if the count is greater than 1, **Choose from List** (`Which cover?`). If the count is 1, **Get Item from List** → **First Item**.
   - **Get Dictionary Value** `url_by_label`, then **Get Dictionary Value** using the chosen name as the key. That value is the image URL.
4. **Most recent cover**: **Get Dictionary Value** `latest`, then **Get Dictionary Value** `url`.
5. **Random cover**: **Get Dictionary Value** `images`, then **Get Item from List** → **Random Item**, then **Get Dictionary Value** `url`.
6. After the menu, **Get Contents of URL** from the menu result and **Set Wallpaper** to the Lock Screen.

`latest` is always the newest issue. `covers_by_month` and `url_by_label` are what the date picker looks up. An untouched copy of this shortcut is in `shortcuts/Thrasher_Covers_Baby.shortcut`. iOS only installs signed shortcuts, so the edit above is how you update the phone. On a Mac you can sign that file with Shortcuts and share a new iCloud link.

### Option 2: Automatic Daily Automation - **RECOMMENDED** ⚠️ **REQUIRES CUSTOM SETUP**
**Important:** You cannot use the shortcut's built-in automation for lock screen changes due to Apple's security policy. You must manually build the automation logic below.

**Set up daily automation (e.g., 9 AM):**

1. Open **Shortcuts** app
2. Tap **Automation** tab at bottom
3. Tap **+** to create new automation
4. Choose **"Time of Day"**
5. Set to **9:00 AM** and **Daily**
6. Tap **Next**
7. Tap **Add Action**
8. **Get Contents of URL**: Add `https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/shortcuts_text_overlay_covers.json`
9. **Get Random Item from List**
10. **Get Value** (to extract the URL from the random item)
11. **Get Contents of URL** (to download the image)
12. **Set Wallpaper** (set to Lock Screen)
13. Tap **Next**
14. Turn **OFF** "Ask Before Running" (crucial for automation!)
15. Tap **Done**
16. Your lock screen will now change automatically every morning!

**Newest issue instead of a random one:** use the same automation, but read the dictionary value `latest`, then `url`, instead of taking a random item from `images`. That `latest` value is the newest issue in the catalog.

## 🎨 What You Get

- **565 covers** spanning 46 years (1981-2026)
- **Complete coverage** - all 12 months for most years
- **Perfect iPhone sizing** - no cropping or stretching
- **Rich metadata** - know the skater, trick, and location
- **High quality** - optimized for crisp display
- **Your choice** - pick an issue on the date picker, use the most recent cover, or take a random one

## 🔧 Customization

### Change Text Position
Edit `text_overlay_config.json` to move the date/skater text around on the image.

### Change Font Size
Adjust the font size in the same config file.

### Hide/Show Info
Choose which details to display (date, skater, trick, location).

## 📚 Examples

**Cover might show:**
- **December 2020** - Tony Hawk - Kickflip - Los Angeles, CA
- **March 1995** - Rodney Mullen - 360 Flip - Tampa, FL
- **August 2008** - Paul Rodriguez - Nollie Heelflip - San Francisco, CA

## 🆘 Troubleshooting

### Shortcut won't work?
- Make sure you're connected to WiFi/cellular
- Check that the URL is copied exactly
- Try running the shortcut manually first

### Images look blurry?
- All images are optimized for iPhone lock screens
- They should look crisp on any iPhone model

### Want different covers?
- The shortcut randomly picks from 565 options
- Run it multiple times to see different covers
- Choose **Most recent cover** when you want the newest issue
- Choose **Pick a date** and spin to a month and year

### Automation not running?
- Make sure "Ask Before Running" is turned OFF
- Check that you're in the Automation tab, not Shortcuts tab
- Verify the time is set correctly

## 🤝 Support

- **GitHub Issues**: Report problems or request features
- **Questions**: Open an issue with your question
- **Improvements**: Suggest ways to make it better

## 📄 License

Open source - feel free to use and modify!

---

**🎉 That's it! You're ready to rock a new Thrasher cover every day! 🛹**

## 🔐 Repository Security

This repository is kept private to:
- Prevent URL hijacking of lock screen images
- Protect users from malicious content injection
- Maintain control over the image distribution
- Ensure only authorized users can access the automation tools

The automation methods and shortcuts are shared publicly for educational purposes, but the actual image URLs and data remain secure within this private repository.
