# Quick Reference: Credentials Setup Behavior

## User Actions & Expected Outcomes

### 🚀 First App Launch
```
App Starts
  ↓
Check if .setup_complete exists? → YES → Go to Login
                                → NO  → Show Setup Screen
  ↓
[Setup Screen Opens]
User Action:
  • Close (X) → Confirm dialog → If Yes: No save, go back to login/app
  • Skip Setup → Warn about consequences → If Yes: No save, go to login
  • Save & Continue → Validate both fields → If OK: Save & go to login
                    → If missing: Show error, stay in setup
```

### 🔑 Change Credentials (Anytime)
```
Logged In or Not
  ↓
Click "🔑 Change Credentials"
  ↓
[Setup Screen Opens - "Update Your Credentials" mode]
  ↓
Enter new API key or select new credentials file
  ↓
Click Save & Continue
  ↓
Success message
  ↓
Auto-logout (token.pkl deleted)
  ↓
Back to login screen
```

### 🔓 Login Flow
```
Click "🔓 Login"
  ↓
Check for credentials.json:
  • Found in AppData? Use it
  • Not found? Offer setup screen
  ↓
Browser opens for Google login
  ↓
User closes browser? → Show warning "Login Cancelled"
User completes login? → Save session token → Ready to load emails
```

### 🔐 Logout
```
Click "🔐 Logout"
  ↓
Confirm: "Logout and delete cached credentials?"
  ↓
If YES:
  • Delete: token.pkl (session)
  • Keep: credentials.json (stays safe)
  • Keep: .env file with API key
  • Keep: .setup_complete marker
  ↓
Back to login screen
```

---

## What Gets Saved Where

### ✅ Saved to AppData (persistent)
- `.env` - API key (survives logout, restart)
- `credentials.json` - Gmail OAuth credentials (survives logout, restart)
- `.setup_complete` - Marker file (survives logout, restart)

### ❌ Deleted on Logout
- `token.pkl` - Current session token only

### ❌ Never Sent Anywhere
- No data uploaded to servers
- All local-only operation

---

## Validation Rules

### API Key Required ✓
- Cannot be empty
- Cannot contain spaces only
- Error message if missing: "❌ Please enter your Gemini/OpenAI API key"

### Credentials File Required ✓
- Must be valid JSON
- Must have 'installed' or 'web' key (OAuth structure)
- Error message if missing: "❌ Please select your credentials.json file"

### Both Required Together ✓
- Cannot save with only API key
- Cannot save with only credentials file
- Must have both to click "Save & Continue" successfully

---

## Error Messages & What To Do

| Message | What It Means | What To Do |
|---------|--------------|-----------|
| ❌ Missing API Key | Didn't enter API key | Go to Google AI Studio, get key, paste it |
| ❌ Missing Credentials | Didn't select file | Click 📁 button, find credentials.json |
| ⚠️ Invalid File | File isn't credentials | Make sure file is credentials.json from Google |
| ⚠️ Login Cancelled | Closed browser during login | Click Login again, select your account this time |
| ✓ Setup Complete | Ready to use! | Click OK, you're all set |

---

## If Something Goes Wrong

### Setup keeps appearing on startup
- Delete: `C:\Users\{username}\AppData\Roaming\email-summarizer\.setup_complete`
- Restart app
- Setup will appear again for you to re-enter credentials

### Credentials won't save
- Make sure API key isn't empty
- Make sure credentials.json is selected
- Check that `C:\Users\{username}\AppData\Roaming\email-summarizer\` folder is writable
- Try clicking "Change Credentials" instead of initial setup

### Can't log back in after logout
- You don't need to! Logout only removes session token
- The credentials.json and API key are still saved
- Click Login → it will use saved credentials → browser will open
- Select your Google account in browser

### App froze during login
- This shouldn't happen anymore (fixed)
- If it does: Close browser window during login
- App should show message: "⚠️ Login was cancelled"
- Click Login again

---

## Advanced: Manual File Management

### View saved credentials
```powershell
# Open AppData folder
$appdata = "$env:APPDATA\email-summarizer"
explorer $appdata

# You'll see:
# .env (contains API key)
# credentials.json (Gmail credentials)
# .setup_complete (marker file)
# token.pkl (session - only exists when logged in)
```

### Force reset credentials
```powershell
# Remove AppData folder (careful!)
Remove-Item "$env:APPDATA\email-summarizer" -Recurse -Force

# Next app start: Setup will appear again
```

### Check if setup is complete
```powershell
# Marker exists?
Test-Path "$env:APPDATA\email-summarizer\.setup_complete"

# Output: True (setup done) or False (not done yet)
```

---

## Summary Table

| Feature | Status | Behavior |
|---------|--------|----------|
| Setup on first launch | ✅ | Appears once, skipped if .setup_complete exists |
| Change Credentials anytime | ✅ | Button always enabled |
| Close without saving | ✅ | Asks for confirmation |
| Validation before save | ✅ | Both API key AND credentials required |
| OAuth cancellation | ✅ | Shows friendly warning, doesn't crash |
| Logout behavior | ✅ | Only deletes session, keeps credentials |
| Error messages | ✅ | Clear with next steps |

**All Features Tested ✅**
