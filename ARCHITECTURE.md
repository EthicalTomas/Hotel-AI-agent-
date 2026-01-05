# Hotel AI Agent - Architecture Overview

## System Components

### 1. AI Agent Core (`ai_agent.py`)
- **Purpose**: Central intelligence module that generates responses using OpenAI's GPT-4
- **Key Features**:
  - Loads hotel information from JSON file
  - Creates context-aware system prompts
  - Maintains conversation history
  - Handles fallback responses for errors
- **Dependencies**: OpenAI API

### 2. WhatsApp Handler (`whatsapp_handler.py`)
- **Purpose**: Manages WhatsApp Business API integration via Twilio
- **Key Features**:
  - Sends messages to customers
  - Parses incoming webhook requests
  - Validates Twilio webhooks
  - Formats responses for WhatsApp
- **Dependencies**: Twilio API

### 3. Email Handler (`email_handler.py`)
- **Purpose**: Handles email communication via IMAP and SMTP
- **Key Features**:
  - Fetches unread emails via IMAP
  - Parses email content and metadata
  - Sends responses via SMTP
  - Marks emails as read after processing
  - Maintains email threading
- **Dependencies**: IMAP/SMTP servers (Gmail recommended)

### 4. Main Application (`app.py`)
- **Purpose**: Flask web server that orchestrates all components
- **Key Features**:
  - Webhook endpoint for WhatsApp messages
  - Email checking endpoint
  - Health check endpoint
  - Test endpoint for AI responses
  - Conversation history management
  - Comprehensive logging
- **Dependencies**: Flask, all other modules

### 5. Email Monitor Service (`email_monitor.py`)
- **Purpose**: Background service for continuous email monitoring
- **Key Features**:
  - Runs independently as a daemon/cron job
  - Periodically checks for new emails
  - Automatically responds to inquiries
  - Configurable check interval
- **Dependencies**: AI Agent, Email Handler

## Data Flow

### WhatsApp Message Flow
```
Customer → WhatsApp → Twilio API → Webhook (/webhook/whatsapp)
                                        ↓
                                   Parse Message
                                        ↓
                                   AI Agent (Generate Response)
                                        ↓
                                   WhatsApp Handler
                                        ↓
Customer ← WhatsApp ← Twilio API ← Send Message
```

### Email Message Flow
```
Customer → Email Server → IMAP → Email Handler (Fetch)
                                        ↓
                                   Parse Email
                                        ↓
                                   AI Agent (Generate Response)
                                        ↓
                                   Email Handler (Send via SMTP)
                                        ↓
Customer ← Email Server ← SMTP ← Send Response
```

## Key Design Decisions

### 1. Stateless with In-Memory History
- **Decision**: Store conversation history in memory (dictionary)
- **Rationale**: Simple for MVP, easy to understand
- **Production Recommendation**: Use Redis or database for persistence

### 2. Synchronous Email Processing
- **Decision**: Process emails sequentially
- **Rationale**: Hotels don't typically get thousands of emails per minute
- **Production Recommendation**: Can add async processing if needed

### 3. Separate Email Monitor
- **Decision**: Email monitoring as separate script
- **Rationale**: Flexibility in deployment (cron, systemd, etc.)
- **Alternative**: Could integrate into main app with background thread

### 4. Flask for Web Framework
- **Decision**: Use Flask instead of FastAPI or Django
- **Rationale**: 
  - Simple webhook handling
  - Easy to deploy
  - Minimal boilerplate
  - Well-documented
- **Alternative**: FastAPI for better async support

### 5. JSON for Hotel Data
- **Decision**: Store hotel information in JSON file
- **Rationale**: 
  - Easy to edit without code changes
  - Human-readable
  - Version control friendly
  - No database setup required
- **Production Recommendation**: Consider CMS or database for frequent updates

## Security Considerations

### Implemented
- ✅ Environment variables for all secrets
- ✅ .gitignore prevents committing secrets
- ✅ Input validation on webhooks
- ✅ Logging for audit trails
- ✅ Error handling to prevent information leakage

### Recommended for Production
- 🔒 Rate limiting on webhooks
- 🔒 Request signature validation (Twilio)
- 🔒 HTTPS only (TLS/SSL)
- 🔒 Input sanitization
- 🔒 API key rotation policy
- 🔒 Monitoring and alerting
- 🔒 WAF (Web Application Firewall)

## Scalability Considerations

### Current Capacity
- **WhatsApp**: Can handle ~100-1000 concurrent conversations
- **Email**: Limited by check interval (default: 5 minutes)
- **AI Processing**: Limited by OpenAI API rate limits

### Scaling Strategies

#### Horizontal Scaling
1. Load balancer in front of multiple app instances
2. Shared Redis for conversation history
3. Database for persistent data

#### Vertical Scaling
1. Increase server resources
2. Optimize AI prompts to reduce tokens
3. Cache common responses

#### Service Separation
1. Separate services for WhatsApp and Email
2. Queue-based architecture (RabbitMQ, AWS SQS)
3. Microservices pattern

## Deployment Architecture

### Development
```
Local Machine
├── Flask App (port 5000)
├── Email Monitor (background)
└── ngrok (tunnel for Twilio)
```

### Production (Simple)
```
VPS/Cloud Server
├── Nginx (reverse proxy, SSL)
├── Flask App (systemd service)
└── Email Monitor (systemd service)
```

### Production (Advanced)
```
Cloud Platform (AWS/GCP)
├── Load Balancer
├── App Servers (auto-scaling)
├── Redis (conversation history)
├── RDS/PostgreSQL (persistent data)
├── CloudWatch/Logging
└── S3 (backups)
```

## Monitoring and Observability

### Logs
- `hotel_agent.log` - Main application events
- `email_monitor.log` - Email processing events
- Console output - Real-time debugging

### Metrics to Monitor
- Response time (AI generation)
- Message throughput
- Error rates
- API costs (OpenAI, Twilio)
- Email processing lag

### Recommended Tools
- **Application**: New Relic, DataDog, or Sentry
- **Infrastructure**: CloudWatch, Prometheus + Grafana
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: ELK Stack, CloudWatch Logs

## Cost Optimization

### OpenAI API
- Use GPT-3.5-turbo instead of GPT-4 (~10x cheaper)
- Reduce max_tokens in responses
- Cache responses for common questions
- Use embeddings for semantic search before GPT call

### Twilio
- Optimize message lengths
- Use templates for common responses
- Consider alternative providers for high volume

### Infrastructure
- Use serverless (AWS Lambda, Cloud Run) for variable load
- Auto-scaling based on traffic
- CDN for static content
- Optimize database queries

## Error Handling Strategy

### Graceful Degradation
1. If AI fails → Use fallback response with contact info
2. If WhatsApp fails → Log error, alert admin
3. If Email fails → Retry mechanism with exponential backoff
4. If Hotel info missing → Generic response + admin alert

### Error Categories
- **Transient**: Retry (network issues, API timeouts)
- **Configuration**: Alert admin (invalid credentials)
- **Logic**: Log and use fallback (unexpected data format)
- **External**: Degrade gracefully (API down)

## Future Enhancements

### Short Term (1-3 months)
- [ ] Add database for conversation history
- [ ] Implement rate limiting
- [ ] Add analytics dashboard
- [ ] Multi-language support
- [ ] Voice message handling (WhatsApp)

### Medium Term (3-6 months)
- [ ] Direct booking integration
- [ ] Payment processing
- [ ] Calendar integration
- [ ] Customer segmentation
- [ ] A/B testing for responses
- [ ] Sentiment analysis

### Long Term (6+ months)
- [ ] Multi-channel support (Facebook, Instagram, Telegram)
- [ ] Video call scheduling
- [ ] Advanced analytics and ML insights
- [ ] Integration with PMS (Property Management System)
- [ ] Mobile app for staff
- [ ] Real-time dashboard

## Testing Strategy

### Unit Tests
- Test each handler independently
- Mock external APIs
- Test error handling

### Integration Tests
- Test end-to-end flows
- Use test accounts (Twilio sandbox)
- Verify AI responses

### Load Tests
- Simulate high message volume
- Test rate limits
- Measure response times

### Recommended Tools
- `pytest` for unit tests
- `pytest-mock` for mocking
- `locust` for load testing
- `postman` for API testing

## Documentation

### User Documentation
- ✅ `README.md` - Overview and quick start
- ✅ `your-part.md` - Setup instructions for users
- ✅ `ARCHITECTURE.md` - This file

### Code Documentation
- ✅ Docstrings in all modules
- ✅ Inline comments for complex logic
- ✅ Type hints where applicable

### Operational Documentation
- [ ] Runbook for common issues
- [ ] Deployment procedures
- [ ] Backup and recovery procedures
- [ ] Incident response plan

## Conclusion

This architecture provides a solid foundation for a hotel AI agent system that can:
- Handle customer inquiries automatically
- Scale to meet demand
- Be maintained and extended easily
- Integrate with existing hotel systems

The modular design allows for easy enhancement and replacement of components as needs evolve.
