# Support & Troubleshooting

## Getting Help

### Common Issues

**Problem: "Cannot find credentials.json"**
- Ensure `credentials.json` is in the same folder as the application
- Or place it at: `C:\Users\YourUsername\AppData\Roaming\email-summarizer\credentials.json`
- See [INSTALL.md](INSTALL.md) for detailed setup

**Problem: Login not working**
- Verify Gmail API is enabled in Google Cloud Console
- Re-download `credentials.json` from Google Cloud
- Try logging out and back in
- Clear your browser cache

**Problem: "Gemini API Error"**
- Check that `.env` file has correct `GEMINI_API_KEY=...`
- Verify API key is active in [Google AI Studio](https://aistudio.google.com/app/apikey)
- Check your API quota and billing

**Problem: No emails showing**
- Ensure Gmail account has unread emails
- Check Gmail API quota in Google Cloud Console
- Verify OAuth scopes include `https://www.googleapis.com/auth/gmail.readonly`

---

## Performance Tips

1. **Use lazy summarization**: Only summarize emails you need (saves API credits)
2. **Load fewer emails**: Start with 3-5, then load more if needed
3. **Batch processing**: Load multiple emails, then summarize together
4. **Check API quota**: Monitor usage in Google Cloud Console

---

## Security & Privacy

- **Local storage only**: Credentials and tokens stored on your machine
- **No data collection**: App doesn't collect or send personal data
- **OAuth 2.0**: Uses industry-standard authentication
- **To revoke**: Visit [Google Account Permissions](https://myaccount.google.com/permissions)

---

## Uninstall

**Windows Installer**: Settings → Apps → Email Summarizer Pro → Uninstall

**Portable**: Delete the folder

**Python**: Delete project folder + `C:\Users\YourUsername\AppData\Roaming\email-summarizer\`

---

## Contact & Updates

For bug reports or feature requests, please provide:
- Windows/Python version
- Error message (screenshot)
- Steps to reproduce

---

**Support Email**: [Your Email]  
**Last Updated**: December 2025
