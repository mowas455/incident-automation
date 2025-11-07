# Incident Automation Flow - HaiIntel Task B

## Overview

A microservice that automates customer support workflows across multiple channels (Email, SMS, WhatsApp). The system receives incidents, classifies them intelligently using Claude LLM, creates tickets, and orchestrates multi-channel notifications with automatic reminders.

## Pipeline Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                        INCIDENT FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

1. WEBHOOK RECEIVES MESSAGE
   ├─ Input: customer_id, message, channel (WhatsApp/Email/SMS)
   ├─ Generate unique incident_id
   └─ Log incoming data

2. LLM CLASSIFICATION (Claude)
   ├─ Send message to Claude with predefined categories
   ├─ Categories: duplicate_payment, failed_payment, fraud, refund, etc.
   ├─ Receive: category, confidence score, reasoning
   └─ Store classification in database

3. TICKET CREATION
   ├─ POST incident to mock API (reqres.in)
   ├─ Receive ticket_id
   └─ Store ticket_id with incident

4. MULTI-CHANNEL NOTIFICATIONS
   ├─ Email: "Ticket #XXX created, investigating"
   ├─ SMS: Same message
   └─ Log all notifications

5. 24-HOUR REMINDER TIMER
   ├─ Background thread waits 24 hours
   ├─ Check if incident still "open"
   ├─ If open: send reminder notification
   └─ Mark reminder_sent = true

Database stores: incidents, notifications, reminders
```

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment (Optional)
```bash
export ANTHROPIC_API_KEY="your-api-key"  # Claude will auto-detect from env
```

### 3. Run the Server
```bash
python app.py
```
Server starts at `http://localhost:8000`

## API Endpoints

### 1. Create Incident (Main Webhook)
**POST** `/api/incidents`

**Request:**
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "99876",
    "channel": "whatsapp",
    "message": "My credit card payment was deducted twice yesterday."
  }'
```

**Response:**
```json
{
  "incident_id": "a1b2c3d4-e5f6-...",
  "ticket_id": "TKT-xyz123",
  "status": "open",
  "classification": "duplicate_payment",
  "confidence": 0.95,
  "message": "Incident received and ticket created. Acknowledgments sent via email and SMS."
}
```

### 2. Get Incident Details
**GET** `/api/incidents/<incident_id>`
```bash
curl http://localhost:8000/api/incidents/a1b2c3d4-e5f6-...
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-...",
  "customer_id": "99876",
  "channel": "whatsapp",
  "message": "My credit card payment was deducted twice yesterday.",
  "classification": "duplicate_payment",
  "confidence": 0.95,
  "ticket_id": "TKT-xyz123",
  "status": "open",
  "created_at": "2025-11-05 10:30:00",
  "reminder_sent": 0
}
```

### 3. Resolve Incident
**PUT** `/api/incidents/<incident_id>/resolve`
```bash
curl -X PUT http://localhost:8000/api/incidents/a1b2c3d4-e5f6-.../resolve
```

### 4. Get Customer's All Incidents
**GET** `/api/incidents/customer/<customer_id>`
```bash
curl http://localhost:8000/api/incidents/customer/99876
```

### 5. Get Notifications
**GET** `/api/notifications/<incident_id>`
```bash
curl http://localhost:8000/api/notifications/a1b2c3d4-e5f6-...
```

### 6. Get Statistics
**GET** `/api/stats`
```bash
curl http://localhost:8000/api/stats
```

### 7. Health Check
**GET** `/health`
```bash
curl http://localhost:8000/health
```

## Database Schema

### incidents table
```
id              TEXT PRIMARY KEY     (UUID)
customer_id     TEXT                 (customer reference)
channel         TEXT                 (whatsapp, email, sms)
message         TEXT                 (original customer message)
classification  TEXT                 (category assigned by LLM)
confidence      REAL                 (0.0-1.0 confidence score)
ticket_id       TEXT                 (external ticket reference)
status          TEXT                 (open/resolved)
created_at      TIMESTAMP            (auto)
resolved_at     TIMESTAMP            (when marked resolved)
reminder_sent   BOOLEAN              (1 if 24h reminder sent)
```

### notifications table
```
id              TEXT PRIMARY KEY     (UUID)
incident_id     TEXT FOREIGN KEY     (links to incidents)
channel         TEXT                 (email, sms, whatsapp)
message         TEXT                 (notification text)
status          TEXT                 (sent)
sent_at         TIMESTAMP            (auto)
```

## Key Features

✅ **LLM-Powered Classification**: Claude intelligently categorizes issues (duplicate_payment, fraud, refund, etc.)

✅ **Multi-Channel Delivery**: Email + SMS acknowledgments (simulated, extensible to real providers)

✅ **Automatic Reminders**: 24-hour timer auto-sends reminders for unresolved tickets

✅ **Audit Trail**: Full notification history stored in database

✅ **Mock API Integration**: Posts to reqres.in for realistic ticket creation flow

✅ **Stateless Scalability**: Can be deployed across multiple instances with shared DB

## Testing Examples

### Test 1: Duplicate Payment
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "12345",
    "channel": "email",
    "message": "I was charged twice for my subscription renewal"
  }'
```

### Test 2: Fraud Report
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "67890",
    "channel": "sms",
    "message": "I see a transaction for $500 I didn't authorize"
  }'
```

### Test 3: Failed Payment
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "11111",
    "channel": "whatsapp",
    "message": "Payment failed but money was deducted from my account"
  }'
```

## Logs & Debugging

The application prints detailed logs to console:
- Incident received with ID
- LLM classification result
- Ticket creation status
- Notification sent confirmations
- Reminder scheduling

**Check SQLite directly:**
```bash
sqlite3 incidents.db "SELECT * FROM incidents;"
sqlite3 incidents.db "SELECT * FROM notifications;"
```

## Creative Extensions (For Interview)

### Already Implemented:
- Multi-channel notification system
- 24-hour auto-reminder
- LLM-powered classification

### Possible Add-ons You Can Mention:
1. **Sentiment Analysis**: Detect angry/urgent customers and escalate
2. **Slack Notifications**: Alert support team on critical issues
3. **Analytics Dashboard**: Track issue distribution by type
4. **Auto-Resolution**: Refund duplicate payments automatically
5. **Escalation Logic**: Route fraud cases to priority queue
6. **Real Email/SMS**: Integrate Twilio or SendGrid

## Files Included
```
incident-automation/
├── app.py                  (Main FastAPI application)
├── requirements.txt        (Dependencies)
├── README.md              (This file)
├── PROMPT_LOG.md          (AI interaction history)
├── incidents.db           (SQLite database, created on first run)
└── sample_data.json       (Test data examples)
```

## Production Considerations

- Use connection pooling for database
- Add API authentication (JWT tokens)
- Implement rate limiting
- Use message queues (Redis/RabbitMQ) for async notifications
- Add comprehensive error handling & retry logic
- Store sensitive data encrypted
- Add request validation & sanitization
- Deploy with production WSGI server (gunicorn)

## Author Notes

This solution demonstrates:
1. **AI integration**: Effective use of Claude for intelligent classification
2. **Async workflows**: Background threads for 24h reminders
3. **System design**: Clean separation of concerns, modular functions
4. **Database design**: Normalized schema for incidents & notifications
5. **API design**: RESTful endpoints with proper status codes
6. **Real-world patterns**: Multi-channel orchestration like production systems

The code prioritizes **clarity and extensibility** for interview discussion.