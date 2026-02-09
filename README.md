# How to Upload Screenshots to GitHub (Simple Version)

## The Problem
Your README has image links, but the images aren't on GitHub yet. That's why they show as broken.

## The Solution (5 Minutes)

### Step 1: Go to Your Repository
1. Open browser
2. Go to: https://github.com/OUSSAMA-GATTAOUI/DATA-FORGE
3. Make sure you're logged in

### Step 2: Create the Images Folder
1. Click the green **"Add file"** button (top right)
2. Click **"Create new file"**
3. In the name box, type: `docs/images/.gitkeep`
4. Scroll down and click **"Commit new file"**

### Step 3: Upload Your Screenshots
1. Click on the `docs` folder (you just created it)
2. Click on the `images` folder
3. Click **"Add file"** → **"Upload files"**
4. Drag and drop these 6 files (from my earlier download):
   - `01-login.png`
   - `02-main-interface.png`
   - `03-data-loaded.png`
   - `04-filter-dialog.png`
   - `05-dataset-summary.png`
   - `06-profiling-report.png`
5. Scroll down and click **"Commit changes"**

### Step 4: Update Your README
1. Go back to the main repository page
2. Click on `README.md`
3. Click the **pencil icon** (✏️) to edit
4. **Delete everything** in the file
5. **Copy and paste** the content from `README_WITH_ABSOLUTE_URLS.md` (I just created this)
6. Scroll down and click **"Commit changes"**

### Step 5: Wait and Check
1. Wait 30 seconds
2. Go to your repository main page
3. Scroll down
4. **Screenshots should now appear!** 🎉

---

## Still Not Working?

### Check These Things:
- ✅ File names are EXACTLY: `01-login.png` (not `Screenshot_...`)
- ✅ Files are in `docs/images/` folder (not just `docs/`)
- ✅ You committed the README changes
- ✅ You're looking at the main branch

### Quick Test:
Try visiting this URL directly (replace with your username):
```
https://github.com/OUSSAMA-GATTAOUI/DATA-FORGE/blob/main/docs/images/01-login.png
```

If you see the image, it's uploaded correctly!

---

## Alternative: Upload Everything at Once

If the above is confusing, you can:

1. Download the `docs` folder I created earlier
2. Add it to your local DATA-FORGE folder
3. Use Git commands:
```bash
git add docs/
git commit -m "Add screenshots"
git push
```

Then update README.md similarly.

---

## Need More Help?

The images are already organized and renamed for you in the download. You just need to:
1. Create `docs/images/` folder on GitHub
2. Upload the 6 PNG files
3. Update README.md

That's it! The README already has all the correct links.
