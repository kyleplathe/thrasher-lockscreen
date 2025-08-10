# 🛹 Thrasher Lock Screen

**Get a random Thrasher Magazine cover as your iPhone lock screen every day!**

![Thrasher Lock Screen Example](https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/lock_screen_mockup.PNG)

*Example: November 1984 cover with skater "mark gonzales" and trick "beanplant"*

## 🎯 What This Does

This project gives you **550+ Thrasher Magazine covers** from 1981-2025 that you can automatically set as your iPhone lock screen. Each cover includes:

**Coverage Details:**
- **Years:** 1981-2025 (September)
- **Total:** 550 covers
- **Missing Issues:** 1982 (May, June), 1986 (October, November)
- **Current:** Updated through September 2025

- 📅 **Date** (month and year)
- 👤 **Skater name** 
- 🛹 **Trick description**
- 📍 **Location** (when available)

## 🚀 Quick Setup (2 minutes!)

### Option 1: Download Pre-Built Shortcut ⭐ **EASIEST**
1. **Tap this link on your iPhone**: [Download Thrasher Shortcut](https://www.icloud.com/shortcuts/your-shortcut-id-here)
2. **Tap "Get Shortcut"** when prompted
3. **Test it** by tapping the ▶️ button
4. **Done!** Your lock screen changes instantly

### Option 2: Build It Yourself (Advanced)

#### Step 1: Get the Data
1. Open **Shortcuts** app on your iPhone
2. Tap the **+** button to create a new shortcut
3. Tap **"Get Contents of URL"**
4. Copy and paste this URL:
   ```
   https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/shortcuts_text_overlay_covers.json
   ```

#### Step 2: Pick Random Cover
1. Tap **+** to add another action
2. Search for **"Get Random Item from List"**
3. Connect it to the previous action

#### Step 3: Download & Set Wallpaper
1. Tap **+** again
2. Add **"Get Contents of URL"** 
3. Connect it to the random item
4. Add **"Set Wallpaper"** action
5. Set it to **Lock Screen**

#### Step 4: Test It!
1. Tap the **▶️** button to test
2. Your lock screen should change to a random Thrasher cover!

## 📱 How to Use Daily

### Option 1: Manual (Tap to change)
- Open Shortcuts app
- Tap your Thrasher shortcut
- Lock screen changes instantly

### Option 2: Automatic (Daily at 9 AM) - **RECOMMENDED**
**Note:** You cannot use the shortcut's built-in automation for lock screen changes due to Apple's security policy. You must set up the Automation tab method below.

1. Follow the **Automation Tab** setup steps below
2. Your lock screen will change automatically every morning!

### Option 3: Automation Tab (Required for Daily Updates) ⚠️ **IMPORTANT**
**Why this step is required:** Apple's security policy prevents shortcuts from automatically changing lock screens unless they're set up through the Automation tab.

1. Open **Shortcuts** app
2. Tap **Automation** tab at bottom
3. Tap **+** to create new automation
4. Choose **"Time of Day"**
5. Set to **9:00 AM** and **Daily**
6. Tap **Next**
7. Tap **Add Action**
8. Search for your **Thrasher shortcut**
9. Tap **Next**
10. Turn **OFF** "Ask Before Running" (this is crucial!)
11. Tap **Done**

## 🎨 What You Get

- **550 covers** spanning 45 years (1981-2025)
- **Complete coverage** - most years have all 12 issues
- **Perfect iPhone sizing** - no cropping or stretching
- **Rich metadata** - know the skater, trick, and location
- **High quality** - optimized for crisp display
- **Random selection** - never see the same cover twice in a row

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
- The shortcut randomly picks from 550+ options
- Run it multiple times to see different covers

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
