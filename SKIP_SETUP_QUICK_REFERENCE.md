# Skip Setup - Quick Behavior Chart

## What User Enters vs What Prompt They See

```
┌─────────────────────────────────────────────────────────────────┐
│ Skip Setup Button - Smart Prompts                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬─────────────────────────────────┐
│ API Key      │ Credentials  │ Skip Button Shows               │
├──────────────┼──────────────┼─────────────────────────────────┤
│ ❌ (empty)   │ ❌ (none)    │ ⚠️ Generic warning              │
│              │              │ "You won't be able to..."       │
│              │              │ Options: Skip or go back        │
├──────────────┼──────────────┼─────────────────────────────────┤
│ ✅ (filled)  │ ❌ (none)    │ ⚠️ Specific warning             │
│              │              │ "API key but NO credentials"    │
│              │              │ Lists what won't work           │
│              │              │ Options: Skip or select file    │
├──────────────┼──────────────┼─────────────────────────────────┤
│ ❌ (empty)   │ ✅ (selected)│ ⚠️ Specific warning             │
│              │              │ "Credentials but NO API key"    │
│              │              │ Lists what won't work           │
│              │              │ Options: Skip or enter API key  │
├──────────────┼──────────────┼─────────────────────────────────┤
│ ✅ (filled)  │ ✅ (selected)│ ℹ️ Informational message        │
│              │              │ "Ready to Save"                 │
│              │              │ "Click Save & Continue instead" │
│              │              │ Only button: OK                 │
└──────────────┴──────────────┴─────────────────────────────────┘
```

---

## Decision Flow

```
User clicks "⊘ Skip Setup"
    ↓
Check: What did user enter?
    ↓
    ├─ Both empty → Show generic "won't be able to" warning
    │               Options: Yes (skip) / No (stay)
    │
    ├─ API key only → Show "missing credentials" warning
    │                  Options: Yes (skip) / No (select file)
    │
    ├─ Credentials only → Show "missing API key" warning
    │                      Options: Yes (skip) / No (enter API key)
    │
    └─ Both filled → Show "ready to save" info message
                     Options: OK (only button - tells them to save)
    ↓
User chooses:
    ├─ "Yes" → Close setup, nothing saved
    ├─ "No" → Go back to setup, data is still there
    └─ "OK" → Go back to setup (only option for "Both filled")
```

---

## Example Dialogs

### Dialog 1: Nothing Entered
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Skip Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Are you sure? Without credentials, 
you won't be able to:
• Log in to Gmail
• Summarize emails

You can set them up anytime using 
'Change Credentials'.

Skip setup anyway?

┌──────────┐  ┌──────────┐
│   Yes    │  │    No    │
└──────────┘  └──────────┘
```

### Dialog 2: API Key Only
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Skip Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You've entered your API key but 
haven't selected credentials.json

Without Gmail credentials, you 
won't be able to:
• Log in to Gmail
• Load or summarize emails

Options:
• Click 'No' to select credentials file
• Click 'Yes' to skip and add 
  credentials later

Skip and add credentials later?

┌──────────┐  ┌──────────┐
│   Yes    │  │    No    │
└──────────┘  └──────────┘
```

### Dialog 3: Credentials Only
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Skip Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You've selected credentials.json 
but haven't entered your API key

Without an API key, you won't be 
able to:
• Summarize emails using AI
• Use the smart summarization 
  feature

Options:
• Click 'No' to enter your API key
• Click 'Yes' to skip and add API 
  key later

Skip and add API key later?

┌──────────┐  ┌──────────┐
│   Yes    │  │    No    │
└──────────┘  └──────────┘
```

### Dialog 4: Both Filled
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️ Ready to Save
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You've entered both your API key 
and selected credentials.json!

Please click '✓ Save & Continue' 
to save your settings.

If you want to skip setup anyway, 
clear one of the fields first.

┌──────────┐
│    OK    │
└──────────┘
```

---

## Smart Features

✅ **Contextual Messages**
- Each dialog tells user exactly what they're missing
- Not generic "skip setup" message

✅ **Actionable Guidance**
- Tells user what won't work without each field
- Suggests next steps

✅ **Prevents Mistakes**
- If user has both fields filled, prevents accidental skip
- Suggests saving instead

✅ **User Control**
- User can choose to skip or go back
- Nothing is forced
- Can always use "Change Credentials" later

---

## Related Commands

### Skip Setup Without Saving Anything
```
User scenario: "I'll add credentials later"
1. Don't enter API key
2. Don't select credentials
3. Click Skip → Confirm yes
4. Setup closes, nothing saved
5. Next restart → Setup appears again
6. Can click "Change Credentials" when ready
```

### Save Only One Field (Not Possible)
```
Scenario: User enters API key but not credentials
1. Click Save & Continue
2. Gets error: "Missing Credentials"
3. Must select file to save
4. OR click Skip to skip for now
5. Can add credentials later with "Change Credentials"
```

### Change Mind About Skipping
```
User scenario: "Actually I want to go back"
1. Any Skip dialog appears
2. Click "No"
3. Back to setup screen
4. All entered data is still there
5. Can now click Save or Skip again
```

---

## Status: ✅ READY

Smart Skip Setup prompts are now fully implemented and tested!
