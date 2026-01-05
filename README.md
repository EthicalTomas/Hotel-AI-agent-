# Hotel AI Agent 🏨🤖

An intelligent AI-powered customer service agent for hotels that automatically responds to customer inquiries via WhatsApp Business and Email. The agent uses OpenAI's GPT models to provide accurate, helpful, and professional responses based on your hotel's information.

## Features

- 🤖 **AI-Powered Responses**: Uses OpenAI GPT-4 to understand and respond to customer queries
- 💬 **WhatsApp Business Integration**: Automatically responds to WhatsApp messages via Twilio
- 📧 **Email Automation**: Monitors and responds to customer emails via IMAP/SMTP
- 📚 **Hotel Knowledge Base**: Customizable hotel information including rooms, pricing, amenities, and policies
- 🔄 **Conversation History**: Maintains context across multiple messages with the same customer
- 📝 **Professional Formatting**: Properly formatted responses for both WhatsApp and email
- 🚀 **Easy Deployment**: Flask-based web server with webhook support

## System Architecture

```
┌─────────────────┐          ┌──────────────────┐
│  WhatsApp User  │ ────────▶│  Twilio API      │
└─────────────────┘          └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  Flask Webhook   │
                             │   (app.py)       │
                             └──────────────────┘
                                      │
                                      ▼
┌─────────────────┐          ┌──────────────────┐
│  Email User     │ ◀───────▶│  Email Handler   │
└─────────────────┘          │  (IMAP/SMTP)     │
                             └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   AI Agent       │
                             │  (OpenAI GPT-4)  │
                             └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │ Hotel Info DB    │
                             │ (hotel_info.json)│
                             └──────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Twilio account with WhatsApp Business API access
- Email account with IMAP/SMTP access (Gmail recommended)
- Public URL for webhook (ngrok, production server, or cloud service)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EthicalTomas/Hotel-AI-agent-.git
   cd Hotel-AI-agent-
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials (see Configuration section below).

5. **Customize hotel information**
   
   Edit `hotel_info.json` with your hotel's specific details including:
   - Hotel name, location, and contact information
   - Room types, prices, and amenities
   - Facilities and services
   - Policies (cancellation, pets, etc.)
   - FAQ and nearby attractions

## Configuration

### Environment Variables

Edit the `.env` file with your actual credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
HOTEL_WHATSAPP_NUMBER=whatsapp:+1234567890

# Email Configuration
HOTEL_EMAIL_ADDRESS=your-hotel@gmail.com
HOTEL_EMAIL_PASSWORD=your-app-specific-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Flask Configuration
FLASK_SECRET_KEY=generate-a-random-secret-key
FLASK_PORT=5000
FLASK_DEBUG=False

# Hotel Information File
HOTEL_INFO_FILE=hotel_info.json

# Email Monitor (optional)
EMAIL_CHECK_INTERVAL=300
```

### Setting Up External Services

#### 1. OpenAI API Key
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create an API key from the API Keys section
- Copy the key to your `.env` file

#### 2. Twilio WhatsApp Business API
- Sign up at [Twilio](https://www.twilio.com/)
- Enable WhatsApp Business API in your console
- Get your Account SID and Auth Token
- Configure your WhatsApp numbers
- See `your-part.md` for detailed setup instructions

#### 3. Email Configuration (Gmail)
- Enable 2-Factor Authentication on your Gmail account
- Generate an App Password (Google Account → Security → App Passwords)
- Use the app password in your `.env` file
- Enable IMAP in Gmail settings

## Usage

### Running the Application

#### 1. Start the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000` (or your configured port).

#### 2. Set Up Webhook for WhatsApp

For development, use ngrok to expose your local server:
```bash
ngrok http 5000
```

Configure the ngrok URL in your Twilio console:
- Webhook URL: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
- Method: POST

#### 3. Start Email Monitoring

Run the email monitor in a separate terminal:
```bash
python email_monitor.py
```

Or set up a cron job to periodically check emails:
```bash
# Check emails every 5 minutes
*/5 * * * * cd /path/to/Hotel-AI-agent- && /path/to/venv/bin/python email_monitor.py
```

### API Endpoints

- `GET /` - Health check and service information
- `POST /webhook/whatsapp` - WhatsApp webhook (called by Twilio)
- `GET /check-emails` - Manually trigger email checking
- `POST /test-ai` - Test AI responses (development only)

### Testing the AI Agent

Test the AI responses directly:

```bash
curl -X POST http://localhost:5000/test-ai \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your room rates?"}'
```

### Example Customer Interactions

**WhatsApp Conversation:**
```
Customer: Hi, do you have rooms available this weekend?
AI Agent: Hello! Thank you for your interest in Grand Hotel Paradise. 
I'd be happy to help you with room availability...
```

**Email Example:**
```
From: customer@example.com
Subject: Room Booking Inquiry

Customer: I need a room for 2 adults and 1 child from Dec 15-17.

AI Response: Dear Customer,

Thank you for contacting Grand Hotel Paradise.

I'd be delighted to help you with your booking inquiry...
```

## Project Structure

```
Hotel-AI-agent-/
├── app.py                  # Main Flask application
├── ai_agent.py            # AI agent with OpenAI integration
├── whatsapp_handler.py    # WhatsApp Business API handler
├── email_handler.py       # Email IMAP/SMTP handler
├── email_monitor.py       # Background email monitoring service
├── hotel_info.json        # Hotel information database
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── your-part.md          # User action items and setup instructions
└── README.md             # This file
```

## Customization

### Modifying AI Behavior

Edit the system prompt in `ai_agent.py` to change how the AI responds:

```python
def _create_system_prompt(self) -> str:
    # Customize the prompt here
    prompt = f"""You are a professional assistant for {self.hotel_info['name']}..."""
```

### Adding New Features

- **Database Integration**: Replace the in-memory conversation history with a database (Redis, PostgreSQL, etc.)
- **Booking System**: Integrate with a booking engine for real reservations
- **Multi-language Support**: Add language detection and translation
- **Analytics**: Track common queries and customer satisfaction
- **Payment Integration**: Add payment processing for bookings

## Deployment

### Production Deployment Options

1. **Cloud Platforms**
   - Heroku: Easy deployment with add-ons
   - AWS EC2/Elastic Beanstalk: Full control
   - Google Cloud Run: Serverless containers
   - DigitalOcean App Platform: Simple deployment

2. **Using Docker** (create Dockerfile):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "app.py"]
   ```

3. **Using Process Manager** (e.g., Supervisor, systemd)

See `your-part.md` for detailed deployment instructions.

## Monitoring and Logs

- Application logs: `hotel_agent.log`
- Email monitor logs: `email_monitor.log`
- Console output for real-time monitoring

## Troubleshooting

### Common Issues

1. **WhatsApp messages not received**
   - Check Twilio webhook configuration
   - Verify ngrok/public URL is accessible
   - Check Twilio account status and credits

2. **Email not working**
   - Verify IMAP/SMTP settings
   - For Gmail, ensure app password is used (not regular password)
   - Check if 2FA is enabled
   - Verify firewall allows IMAP/SMTP connections

3. **AI responses not generated**
   - Check OpenAI API key is valid
   - Verify you have API credits
   - Check `hotel_info.json` is properly formatted

4. **Rate limiting**
   - Implement rate limiting for production
   - Monitor OpenAI API usage
   - Cache common responses

## Security Considerations

- Never commit `.env` file to version control
- Use environment variables for all secrets
- Implement rate limiting in production
- Validate and sanitize all user inputs
- Use HTTPS in production
- Regularly rotate API keys and passwords
- Monitor for unusual activity

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check the `your-part.md` file for setup instructions
- Review logs for error messages

## Acknowledgments

- OpenAI for GPT-4 API
- Twilio for WhatsApp Business API
- Flask framework
- Python community

---

**Note**: This is a template system. Please customize `hotel_info.json` with your actual hotel information and configure all required API credentials before deployment.
