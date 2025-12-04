# Release & CodeCanyon Upload Guide

## Pre-Upload Security Checklist

Before uploading to CodeCanyon, ensure:

- [ ] `credentials.json` is **DELETED** (users provide their own)
- [ ] `.env` contains only template values (no real API keys)
- [ ] `token.pkl` is **NOT** in the package
- [ ] `.gitignore` is included
- [ ] All `.example.json/.example.*` files are present
- [ ] No `__pycache__` directories included
- [ ] No `.pyc` files included

### Run Security Check

```batch
cd build-scripts
security-check.bat
```

Should see: `✓ All checks passed`

---

## Creating the Release ZIP

### Step 1: Run Pre-Flight Check
```batch
cd build-scripts
security-check.bat
```

### Step 2: Create Release Package
```batch
cd build-scripts
create-release-zip.bat
```

This creates:
- `packaging/email-summarizer-release.zip` (the main package)
- `packaging/SHA256SUMS.txt` (checksum for verification)

---

## CodeCanyon Upload Steps

### 1. Create an Envato Account (if needed)
- Go to [Envato Market](https://market.envato.com/)
- Sign up or log in
- Become an author (Author → Dashboard → Submit Item)

### 2. Prepare Your Item Listing

**Basic Information:**
- **Item Name**: Email Summarizer Pro
- **Category**: Code → Scripts → Utility
- **Tags**: gmail, email, ai, summarizer, gemini, python, windows, productivity
- **Description**: Use the content from `item_description.txt`
- **Supported Software**: Windows 7+, Python 3.8+

**Preview Assets:**
- **Preview Image** (770 × 440px): Main screenshot showing the UI
- **Screenshots** (6-10 images, 1600 × 1200px or larger):
  - Login screen
  - Email loading interface
  - Summary display
  - Draft reply generation
  - Settings/configuration
  - Troubleshooting examples
- **Demo Video** (optional but recommended):
  - 30-90 seconds showing key features
  - Screen recording of the workflow

**Documentation:**
- Upload as text or links:
  - INSTALL.md (installation steps)
  - README.md (features & overview)
  - SUPPORT.md (troubleshooting)
  - CHANGELOG.md (version history)

### 3. Upload the Package

- **Item File**: `email-summarizer-release.zip`
- Ensure it includes:
  - `email_customtkinter_gui.py` (main app)
  - `credentials.example.json` (template)
  - `.env.example` (template)
  - `README.md`, `INSTALL.md`, `SUPPORT.md`
  - `requirements.txt`
  - All documentation

### 4. Pricing & Support

- **License Type**: Regular license (single purchase)
- **Price**: Recommended starting price $9-$19 (research competitors)
- **Support Policy**: Specify your response time (e.g., 24-48 hours)
- **Refund Policy**: 30 days (Envato default)

### 5. Copyright & Licensing

- **License**: Choose your preferred license:
  - Regular License (personal/commercial use)
  - Extended License (SaaS/redistributable)
- **Copyright Notice**: Add your copyright information
- **Third-Party Assets**: List all dependencies (see below)

---

## Third-Party Licenses

Include in your package:

```
THIRD-PARTY LICENSES

This product uses the following open-source libraries:

1. CustomTkinter
   - License: MIT
   - URL: https://github.com/TomSchimansky/CustomTkinter

2. Google Auth Libraries
   - google-auth
   - google-auth-oauthlib
   - google-api-python-client
   - License: Apache 2.0
   - URL: https://github.com/googleapis/google-auth-library-python

3. python-dotenv
   - License: MIT
   - URL: https://github.com/theskumar/python-dotenv

4. requests
   - License: Apache 2.0
   - URL: https://github.com/psf/requests

All licenses comply with commercial use and redistribution.
```

---

## File Checksums & Virus Scans

### Generate VirusTotal Report (Recommended)

1. Go to [VirusTotal](https://www.virustotal.com/)
2. Upload `email-summarizer-release.zip`
3. Wait for scan to complete
4. Screenshot the report showing "No threats detected"
5. Include in submission notes

### Verify SHA256

Users can verify package integrity:
```powershell
$hash = (Get-FileHash email-summarizer-release.zip -Algorithm SHA256).Hash
$hash  # Compare with SHA256SUMS.txt
```

---

## Package Contents Reference

```
email-summarizer-release.zip
├── source/
│   ├── email_customtkinter_gui.py   (main application)
│   ├── config.py                    (configuration)
│   ├── requirements.txt             (dependencies)
│   └── run_gui.bat                  (launcher)
│
├── credentials.example.json         (template for OAuth setup)
├── .env.example                     (template for API key)
├── .gitignore                       (version control)
│
├── docs/
│   ├── README.md                    (overview & features)
│   ├── INSTALL.md                   (setup instructions)
│   ├── SUPPORT.md                   (troubleshooting)
│   ├── CHANGELOG.md                 (version history)
│   ├── GET_CREDENTIALS.md           (OAuth setup)
│   ├── SETUP_GUIDE.md               (Windows setup)
│   └── LICENSE.txt                  (product license)
│
├── item_description.txt             (CodeCanyon listing)
└── THIRD-PARTY-LICENSES.txt         (open-source credits)
```

---

## Review Process

**Typical Timeline**: 3-7 business days

**Reviewers Check For:**
✓ Code quality and functionality
✓ Security (no exposed credentials, malware, etc.)
✓ Documentation completeness
✓ Third-party compliance
✓ Installation instructions clarity
✓ No copyright infringement

**Common Rejection Reasons:**
- ✗ Exposed credentials or API keys
- ✗ Missing installation documentation
- ✗ Unlicensed third-party assets
- ✗ Code doesn't work or has critical bugs
- ✗ Malware or suspicious behavior detected

**Response to Review Feedback:**
- Check reviewer notes carefully
- Fix any issues mentioned
- Resubmit with updated files
- Respond professionally and promptly

---

## Post-Launch Marketing

1. **Announce on social media** (Twitter, Reddit, ProductHunt)
2. **Share in relevant communities** (Python, automation, productivity)
3. **Request reviews** from beta testers
4. **Gather feedback** for version 2.0
5. **Plan updates** based on user requests

---

## Maintenance & Updates

After launch, consider:
- Bug fixes and patches
- Feature improvements
- Compatibility updates
- Documentation improvements
- User support responses

---

## Quick Reference

| Item | File/Location |
|------|--------------|
| Main App | `email_customtkinter_gui.py` |
| Installation Guide | `INSTALL.md` |
| Troubleshooting | `SUPPORT.md` |
| Setup Wizard | `setup.bat` |
| Launcher | `run_gui.bat` |
| Config Template | `credentials.example.json` |
| API Key Template | `.env.example` |
| Changelog | `CHANGELOG.md` |
| Listing Content | `item_description.txt` |

---

**Last Updated**: December 2025  
**Version**: 1.0.0 Release Guide
