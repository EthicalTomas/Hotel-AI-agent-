# Your Part - Setup Instructions and Action Items

This document outlines the steps **you need to complete** to get the Hotel AI Agent fully operational. The code is ready, but you need to configure the external services and credentials.

## 📋 Required Actions Checklist

### ✅ 1. OpenAI API Setup

**What you need to do:**

1. Create an OpenAI account at https://platform.openai.com/
2. Go to the API section: https://platform.openai.com/api-keys
3. Click "Create new secret key"
4. Copy the API key (it starts with `sk-`)
5. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Important Notes:**
- You need to add payment method to your OpenAI account
- GPT-4 is recommended but you can use GPT-3.5-turbo to save costs (edit `ai_agent.py` line 82)
- Monitor your usage at https://platform.openai.com/usage
- Estimated cost: ~$0.01-0.10 per customer interaction (depending on length)

---

### ✅ 2. WhatsApp Business API Setup (via Twilio)

**What you need to do:**

#### Step 1: Create Twilio Account
1. Sign up at https://www.twilio.com/try-twilio
2. Verify your email and phone number
3. Complete the account setup

#### Step 2: Enable WhatsApp Sandbox (for testing)
1. Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Follow the instructions to join the sandbox:
   - Send a WhatsApp message to the Twilio sandbox number
   - Include the join code (e.g., "join <your-code>")
3. Note down the sandbox WhatsApp number (usually `whatsapp:+14155238886`)

#### Step 3: Get Your Credentials
1. From Twilio Console dashboard: https://console.twilio.com/
2. Copy your **Account SID**
3. Copy your **Auth Token**
4. Add them to your `.env` file:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

#### Step 4: Configure Webhook (after starting the app)
1. Start your Flask application (`python app.py`)
2. Expose it to the internet using ngrok:
   ```bash
   ngrok http 5000
   ```
3. Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
5. In the "When a message comes in" field, enter:
   ```
   https://your-ngrok-url.ngrok.io/webhook/whatsapp
   ```
6. Set method to **POST**
7. Click Save

#### Step 5: Upgrade to Production WhatsApp (for real business use)
For production use with your own business phone number:
1. Go to https://console.twilio.com/us1/develop/sms/whatsapp/senders
2. Click "Request Access" for WhatsApp Business
3. Follow the verification process (requires Facebook Business Manager)
4. Submit your business for approval (takes 1-3 days)
5. Once approved, you'll get your own WhatsApp business number

**Cost Estimate:**
- Sandbox: Free for testing
- Production: ~$0.005 per message sent, ~$0.01 per template message

---

### ✅ 3. Email Setup (Gmail Recommended)

**What you need to do:**

#### Step 1: Prepare Your Gmail Account
1. Log into the Gmail account you want to use for the hotel
2. Enable 2-Factor Authentication:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Follow the setup wizard

#### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "Hotel AI Agent"
4. Click "Generate"
5. Copy the 16-character password (remove spaces)

#### Step 3: Enable IMAP in Gmail
1. In Gmail, click Settings (gear icon) → See all settings
2. Go to "Forwarding and POP/IMAP" tab
3. Enable IMAP access
4. Click "Save Changes"

#### Step 4: Configure Environment Variables
Add to your `.env` file:
```
HOTEL_EMAIL_ADDRESS=your-hotel@gmail.com
HOTEL_EMAIL_PASSWORD=your-16-char-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Using Non-Gmail Email:**
If you're using a different email provider:
- Find their IMAP/SMTP server settings
- Update the server addresses and ports in `.env`
- Some providers (Outlook, Yahoo) also require app passwords

---

### ✅ 4. Customize Hotel Information

**What you need to do:**

1. Open `hotel_info.json` in a text editor
2. Replace ALL placeholder information with your actual hotel data:
   - Hotel name and location
   - Contact information (phone, email, website)
   - Room types, prices, and amenities
   - Facilities and services
   - Policies (cancellation, pets, smoking, etc.)
   - Dining options
   - FAQ items
   - Nearby attractions

**Example fields to update:**
```json
{
  "name": "YOUR ACTUAL HOTEL NAME",
  "location": "YOUR ACTUAL ADDRESS",
  "phone": "YOUR ACTUAL PHONE",
  "email": "YOUR ACTUAL EMAIL",
  "website": "YOUR ACTUAL WEBSITE",
  ...
}
```

**Important:** 
- Be accurate with pricing and policies
- Include seasonal pricing if applicable
- Keep information up-to-date
- The AI will use this data to answer customer questions

---

### ✅ 5. Install and Run the Application

**What you need to do:**

#### Step 1: Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Test the Configuration
```bash
# Make sure .env is configured
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key:', os.getenv('OPENAI_API_KEY')[:10]); print('Email:', os.getenv('HOTEL_EMAIL_ADDRESS'))"
```

#### Step 3: Start the Flask Server
```bash
python app.py
```

You should see:
```
Starting Hotel AI Agent server on port 5000
* Running on http://0.0.0.0:5000
```

#### Step 4: Start Email Monitor (in a new terminal)
```bash
# Activate virtual environment again
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run email monitor
python email_monitor.py
```

---

### ✅ 6. Testing

**What you need to do:**

#### Test 1: AI Agent (via API)
```bash
curl -X POST http://localhost:5000/test-ai \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your room rates?"}'
```

Expected: JSON response with AI-generated answer

#### Test 2: WhatsApp
1. Make sure ngrok is running and webhook is configured
2. Send a WhatsApp message to your Twilio sandbox number
3. Include your sandbox join code if required
4. Send: "Hello, do you have availability this weekend?"
5. You should receive an AI response within seconds

#### Test 3: Email
1. Send an email to your configured hotel email address
2. Wait for the check interval (default 5 minutes) or manually trigger:
   ```bash
   curl http://localhost:5000/check-emails
   ```
3. You should receive an AI-generated response email

---

### ✅ 7. Production Deployment

**What you need to do:**

When ready to go live, you need to:

#### Option A: Cloud Platform (Recommended)

**Heroku:**
1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Create a Heroku app:
   ```bash
   heroku create your-hotel-ai-agent
   ```
3. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set TWILIO_ACCOUNT_SID=your_sid
   # ... set all variables from .env
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```
5. Update Twilio webhook to your Heroku URL

**Other Options:**
- **AWS**: Deploy to EC2 or Elastic Beanstalk
- **Google Cloud**: Use Cloud Run or App Engine
- **DigitalOcean**: Use App Platform or Droplet

#### Option B: VPS/Dedicated Server

1. Rent a VPS (DigitalOcean, Linode, etc.)
2. Install Python 3.8+
3. Clone your repository
4. Set up the environment
5. Use **supervisor** or **systemd** to keep the app running:

**Example systemd service** (`/etc/systemd/system/hotel-ai.service`):
```ini
[Unit]
Description=Hotel AI Agent
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/Hotel-AI-agent-
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hotel-ai
sudo systemctl start hotel-ai
```

6. Set up **nginx** as reverse proxy
7. Get SSL certificate with **Let's Encrypt**

---

### ✅ 8. Set Up Monitoring (Optional but Recommended)

**What you need to do:**

1. **Set up log rotation** to prevent log files from growing too large:
   ```bash
   # Create logrotate config
   sudo nano /etc/logrotate.d/hotel-ai
   ```
   
   Add:
   ```
   /path/to/Hotel-AI-agent-/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

2. **Set up monitoring alerts:**
   - Use a service like UptimeRobot (free) to monitor your endpoint
   - Get alerts if the service goes down
   - Monitor at: `https://your-domain.com/`

3. **Monitor API Usage:**
   - Check OpenAI usage regularly: https://platform.openai.com/usage
   - Check Twilio usage: https://console.twilio.com/
   - Set up billing alerts

---

### ✅ 9. Security Checklist

**What you need to do:**

- [ ] Never commit `.env` file to Git (already in `.gitignore`)
- [ ] Use strong, unique passwords for all services
- [ ] Keep API keys secure and rotate them periodically
- [ ] Enable HTTPS in production (use Let's Encrypt)
- [ ] Set up firewall rules on your server
- [ ] Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Monitor logs for suspicious activity
- [ ] Implement rate limiting if needed
- [ ] Back up your configuration and hotel data

---

### ✅ 10. Ongoing Maintenance

**What you need to do regularly:**

**Weekly:**
- Check logs for errors
- Monitor API usage and costs
- Review customer interactions for quality

**Monthly:**
- Update hotel information (prices, availability, etc.)
- Review and improve AI responses
- Update dependencies if security patches are available

**As Needed:**
- Handle edge cases the AI doesn't understand
- Add new FAQ items based on common questions
- Adjust AI prompts for better responses

---

## 💰 Cost Estimate Summary

| Service | Cost |
|---------|------|
| OpenAI API (GPT-4) | ~$0.01-0.10 per interaction |
| Twilio WhatsApp (production) | ~$0.005 per message |
| Email (Gmail) | Free |
| Server Hosting | $5-50/month depending on platform |
| Domain name (optional) | ~$10/year |

**Estimated Monthly Cost for Small Hotel:**
- 100 WhatsApp messages: $0.50
- 50 email responses: Free
- 150 AI interactions: $5-15
- Hosting: $10
- **Total: ~$15-25/month**

---

## 🆘 Support and Troubleshooting

If you run into issues:

1. **Check the logs:**
   - `hotel_agent.log` for main application
   - `email_monitor.log` for email service

2. **Common Issues:**
   - **"OpenAI API error"**: Check your API key and billing
   - **"Twilio authentication failed"**: Verify Account SID and Auth Token
   - **"Email login failed"**: Make sure you're using app password, not regular password
   - **"Webhook not receiving messages"**: Check ngrok is running and URL is correct in Twilio

3. **Test each component separately:**
   - Test AI: `curl http://localhost:5000/test-ai ...`
   - Test email: `curl http://localhost:5000/check-emails`
   - Check health: `curl http://localhost:5000/`

4. **Get help:**
   - Check GitHub Issues
   - Review error messages in logs
   - Verify all credentials in `.env` are correct

---

## ✨ You're All Set!

Once you complete all the items above, your Hotel AI Agent will be ready to:
- ✅ Automatically respond to WhatsApp messages
- ✅ Monitor and reply to customer emails
- ✅ Provide accurate information about your hotel
- ✅ Handle multiple customers simultaneously
- ✅ Maintain conversation context

**Remember:** Start with the sandbox/test environment, verify everything works, then deploy to production!

Good luck! 🚀
