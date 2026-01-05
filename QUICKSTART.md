# Quick Start Guide

Get your Hotel AI Agent running in 10 minutes! ⚡

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] A text editor (VS Code, Sublime, etc.)
- [ ] OpenAI API account (sign up at platform.openai.com)
- [ ] Twilio account for WhatsApp (sign up at twilio.com)
- [ ] Gmail account for email (or other email provider)

## Quick Setup (Development Mode)

### Step 1: Install Dependencies (2 minutes)

```bash
# Clone the repo (if you haven't already)
git clone https://github.com/EthicalTomas/Hotel-AI-agent-.git
cd Hotel-AI-agent-

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables (3 minutes)

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

**Minimum required variables to start:**

```env
# OpenAI (Required)
OPENAI_API_KEY=sk-your-actual-key-here

# Twilio WhatsApp (for WhatsApp features)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Email (for email features)
HOTEL_EMAIL_ADDRESS=your-email@gmail.com
HOTEL_EMAIL_PASSWORD=your-gmail-app-password

# Flask (use defaults for now)
FLASK_SECRET_KEY=dev-secret-key-change-in-production
FLASK_PORT=5000
```

### Step 3: Customize Hotel Information (2 minutes)

Edit `hotel_info.json` with your hotel's details:

```bash
nano hotel_info.json
```

At minimum, update:
- Hotel name
- Location
- Contact information (phone, email)
- Room types and prices

### Step 4: Test the Setup (1 minute)

```bash
# Run the structure test
python test_setup.py
```

You should see: `✓ All structural tests passed!`

### Step 5: Start the Server (2 minutes)

```bash
# Start the Flask app
python app.py
```

You should see:
```
Starting Hotel AI Agent server on port 5000
* Running on http://0.0.0.0:5000
```

### Step 6: Test the AI (1 minute)

In a new terminal:

```bash
curl -X POST http://localhost:5000/test-ai \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your room rates?"}'
```

You should get a JSON response with the AI's answer!

## Testing WhatsApp (Optional - 10 extra minutes)

### Step 1: Set up ngrok

```bash
# Download ngrok from ngrok.com
# Then run:
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 2: Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to: Messaging → Try it out → Send a WhatsApp message
3. Under "When a message comes in", paste: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
4. Set method to **POST**
5. Click Save

### Step 3: Test WhatsApp

1. Join Twilio sandbox (send "join [code]" to the Twilio number)
2. Send a message: "Hello, do you have rooms available?"
3. Get an AI response! 🎉

## Testing Email (Optional - 5 extra minutes)

### Option 1: Manual Check

```bash
curl http://localhost:5000/check-emails
```

### Option 2: Automatic Monitoring

In a new terminal:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python email_monitor.py
```

Now send an email to your configured hotel email address and wait for the response!

## Common Quick Fixes

### "OpenAI API error"
- Check your API key is correct
- Verify you have credits: https://platform.openai.com/usage
- Make sure API key starts with `sk-`

### "Twilio authentication failed"
- Double-check Account SID and Auth Token
- Ensure no extra spaces in .env file
- Verify credentials at: https://console.twilio.com/

### "Email login failed"
- For Gmail, use an App Password, not your regular password
- Enable 2FA first, then create app password
- Check IMAP is enabled in Gmail settings

### "ModuleNotFoundError"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "Port already in use"
- Change FLASK_PORT in .env
- Or kill the process using port 5000

## What's Next?

Now that it's running:

1. **Customize Responses**: Edit the system prompt in `ai_agent.py`
2. **Add More Hotel Info**: Update `hotel_info.json` with detailed information
3. **Deploy to Production**: See `your-part.md` for deployment instructions
4. **Monitor Usage**: Check logs in `hotel_agent.log`

## Need Help?

- 📖 Read the full [README.md](README.md)
- 🛠️ Follow detailed setup in [your-part.md](your-part.md)
- 🏗️ Understand the architecture in [ARCHITECTURE.md](ARCHITECTURE.md)
- 🐛 Check logs: `tail -f hotel_agent.log`
- 💬 Open an issue on GitHub

## Development Tips

### Useful Commands

```bash
# View logs in real-time
tail -f hotel_agent.log

# Test AI without running server
python -c "from ai_agent import HotelAIAgent; agent = HotelAIAgent('hotel_info.json'); print(agent.generate_response('Do you have WiFi?'))"

# Check what's running
ps aux | grep python

# Validate JSON
python -m json.tool hotel_info.json

# Check dependencies
pip list
```

### Debugging Mode

Add this to your .env:
```
FLASK_DEBUG=True
```

Then restart the app for detailed error messages.

### Testing Different Models

To use GPT-3.5 instead of GPT-4 (cheaper):

Edit `ai_agent.py`, line ~82:
```python
model="gpt-3.5-turbo",  # Change from "gpt-4"
```

## Congratulations! 🎉

Your Hotel AI Agent is now running and ready to handle customer inquiries!

**Remember:** 
- This is development mode - don't use for production yet
- Keep your API keys secret
- Monitor your usage and costs
- Test thoroughly before going live

Happy automating! 🤖🏨
