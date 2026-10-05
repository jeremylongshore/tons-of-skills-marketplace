# Creator Studio Pack - Installation Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-11

---

## Prerequisites

### Required

- **Claude Code** 1.0.0 or higher
- **FFmpeg** for video processing
- **Git** for build logging

### Optional (for full functionality)

- **DaVinci Resolve** 18+ for professional editing
- **Node.js** 18+ for YouTube/Twitter/LinkedIn APIs
- **YouTube API credentials** for automated uploads
- **Twitter API credentials** for thread distribution
- **LinkedIn API credentials** for professional content

---

## Quick Installation (5 Minutes)

### Step 1: Install the Pack

```bash
/plugin install creator-studio-pack@claude-code-plugins-plus
```

### Step 2: Verify Installation

```bash
/plugin list | grep creator-studio
```

You should see:

```
creator-studio-pack v1.0.0 (20 plugins)
├── 5 Project Documentation plugins
├── 5 Video Production plugins
├── 5 Content Strategy plugins
└── 5 Workflow Optimization plugins
```

### Step 3: Install FFmpeg

**macOS:**

```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**

```bash
choco install ffmpeg
```

**Verify:**

```bash
ffmpeg -version
```

### Step 4: Test Your First Recording

```bash
/record start test-recording
# Code or do something for 30 seconds
/record stop
```

You should see:

```
✅ Recording saved: ~/Videos/test-recording/raw/2025-10-11-14-30-test-recording.mp4
Duration: 0:32
Ready for editing
```

---

## Full Installation (Optional Integrations)

### DaVinci Resolve Setup

1. **Install DaVinci Resolve**
   - Download from: https://www.blackmagicdesign.com/products/davinciresolve
   - Free version is sufficient

2. **Enable Scripting API**

   ```bash
   # macOS/Linux
   export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"

   # Windows
   set RESOLVE_SCRIPT_API="C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\"
   ```

3. **Test Integration**
   - Open DaVinci Resolve
   - Talk to video-editor-ai agent: "Connect to DaVinci Resolve"
   - Should see: "✅ Connected to DaVinci Resolve 18.x"

### YouTube API Setup

1. **Create Google Cloud Project**
   - Go to: https://console.cloud.google.com
   - Create new project: "Creator Studio"

2. **Enable YouTube Data API v3**
   - APIs & Services → Library
   - Search "YouTube Data API v3"
   - Click "Enable"

3. **Create OAuth Credentials**
   - APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Application type: Desktop app
   - Download JSON credentials

4. **Configure Creator Studio**

   ```bash
   mkdir -p ~/.creator-studio
   cp ~/Downloads/client_secret_*.json ~/.creator-studio/youtube-credentials.json
   ```

5. **Authorize**
   - Talk to distribution-automator: "Connect YouTube"
   - Follow OAuth flow in browser
   - Grant permissions

### Twitter API Setup

1. **Apply for Developer Account**
   - Go to: https://developer.twitter.com
   - Apply for elevated access (free)

2. **Create App**
   - Projects & Apps → Create App
   - Name: "Creator Studio Bot"
   - Get API keys and tokens

3. **Configure Creator Studio**

   ```bash
   cat > ~/.creator-studio/twitter-credentials.json << EOF
   {
     "apiKey": "your_api_key",
     "apiSecret": "your_api_secret",
     "accessToken": "your_access_token",
     "accessSecret": "your_access_secret"
   }
   EOF
   ```

4. **Test**
   - Talk to distribution-automator: "Test Twitter connection"
   - Should see: "✅ Connected to Twitter API"

### LinkedIn API Setup

1. **Create LinkedIn App**
   - Go to: https://www.linkedin.com/developers/apps
   - Create app with your company page

2. **Request API Access**
   - Products → "Share on LinkedIn"
   - Wait for approval (usually instant)

3. **Get Credentials**
   - Auth → Copy Client ID and Client Secret

4. **Configure Creator Studio**

   ```bash
   cat > ~/.creator-studio/linkedin-credentials.json << EOF
   {
     "clientId": "your_client_id",
     "clientSecret": "your_client_secret"
   }
   EOF
   ```

5. **Authorize**
   - Talk to distribution-automator: "Connect LinkedIn"
   - Complete OAuth flow

---

## Configuration

### Default Settings

Creator Studio creates a config file at `~/.creator-studio/config.json`:

```json
{
  "recordingDefaults": {
    "resolution": "1920x1080",
    "fps": 30,
    "codec": "h264",
    "audioEnabled": true,
    "outputDirectory": "~/Videos"
  },
  "editingDefaults": {
    "autoRemoveSilence": true,
    "silenceThreshold": 2.0,
    "autoAddSubtitles": true,
    "subtitleStyle": "mr-beast"
  },
  "distributionDefaults": {
    "platforms": ["youtube", "twitter", "linkedin"],
    "scheduleEnabled": false,
    "crossPromote": true
  },
  "contentStrategy": {
    "targetLength": 600,
    "targetAudience": "developers",
    "contentFrequency": "weekly"
  }
}
```

### Customization

Edit the config file to match your workflow:

```bash
# Edit config
nano ~/.creator-studio/config.json

# Or use command
/template config
```

---

## Verification Checklist

After installation, verify everything works:

- [ ] FFmpeg installed and in PATH
- [ ] Can start/stop recordings with `/record`
- [ ] Build logger tracks git commits
- [ ] Can generate video scripts from code
- [ ] Can create thumbnails with `/thumbnail`
- [ ] Can optimize titles with `/optimize-title`
- [ ] DaVinci Resolve connected (optional)
- [ ] YouTube API configured (optional)
- [ ] Twitter API configured (optional)
- [ ] LinkedIn API configured (optional)

---

## Troubleshooting

### FFmpeg not found

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows
choco install ffmpeg

# Verify
which ffmpeg  # Should show path
```

### Recording fails to start

```bash
# Check permissions (macOS)
System Preferences → Security & Privacy → Screen Recording
→ Add Terminal or your terminal app

# Check disk space
df -h ~/Videos

# Check FFmpeg
ffmpeg -version
```

### DaVinci Resolve connection fails

```bash
# Verify Resolve is running
ps aux | grep Resolve

# Check scripting API path
echo $RESOLVE_SCRIPT_API

# Try manual connection
python3 -c "import DaVinciResolveScript as dvr; resolve = dvr.scriptapp('Resolve'); print(resolve.GetVersion())"
```

### API credentials not working

```bash
# Check file exists
ls -la ~/.creator-studio/*-credentials.json

# Validate JSON format
cat ~/.creator-studio/youtube-credentials.json | jq .

# Re-authorize
rm ~/.creator-studio/youtube-token.json
# Then reconnect via distribution-automator
```

---

## Uninstallation

To remove Creator Studio Pack:

```bash
# Uninstall plugin
/plugin uninstall creator-studio-pack

# Remove configuration (optional)
rm -rf ~/.creator-studio

# Remove videos (optional, be careful!)
# rm -rf ~/Videos
```

---

## Next Steps

Once installed, see:

- [Quick Start Guide](QUICK_START.md) - Create your first video in 30 minutes
- [Complete Workflows](WORKFLOWS.md) - End-to-end production flows
- [50+ Examples](EXAMPLES.md) - Real-world use cases

---

## Support

- **Documentation**: `/documentation` folder
- **Issues**: [GitHub Issues](https://github.com/jeremylongshore/claude-code-plugins/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)

---

**Installation complete! Ready to build AND create content.** 🎬🚀
