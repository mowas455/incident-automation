# Incident Automation API

Microservice that classifies customer support issues with AI, creates tickets, sends emails, and schedules reminders.

---

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open: **http://localhost:8000/docs**

---

## What It Does

```
Customer Message
    ↓
Google Gemini AI (Classification)
    ↓
Create Ticket (TKT-xxx)
    ↓
Send Email to Customer
    ↓
Database Storage
    ↓
24-Hour Reminder (If Still Open)
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/incidents` | Create incident |
| GET | `/api/incidents/{id}` | Fetch incident |
| GET | `/api/incidents/customer/{id}` | Customer history |
| PUT | `/api/incidents/{id}/resolve` | Resolve |
| GET | `/api/notifications/{id}` | View notifications |
| GET | `/api/stats` | Statistics |
| GET | `/health` | Health check |

---

## Test It

```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "99876",
    "channel": "email",
    "message": "I was charged twice",
    "email": "test@example.com"
  }'
```

Response:
```json
{
  "incident_id": "abc123...",
  "ticket_id": "TKT-xyz",
  "classification": "duplicate_payment",
  "confidence": 0.98,
  "status": "open"
}
```

---

## Setup

### 1. Environment Variables

Create `.env`:
```
GOOGLE_API_KEY=your-key
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Get Google API Key:** https://makersuite.google.com/app/apikey

**Get Gmail App Password:**
1. https://myaccount.google.com/apppasswords
2. Select Mail + Mac
3. Copy 16-char password

### 2. Database

SQLite auto-creates on first run: `incidents.db`

Check data:
```bash
sqlite3 incidents.db "SELECT * FROM incidents;"
```

---

## Classification Categories

- `duplicate_payment` - Charged 2+ times
- `failed_payment` - Failed but charged
- `fraud_report` - Unauthorized
- `refund_request` - Wants money back
- `account_locked` - Can't log in
- `statement_error` - Balance wrong
- `other` - Doesn't fit above

---

## Key Features

✅ Real email notifications (Gmail SMTP)
✅ AI classification (Google Gemini)
✅ 24-hour reminders (background threads)
✅ Complete audit trail (database)
✅ Multi-channel support (Email/SMS/WhatsApp)
✅ Interactive Swagger UI (http://localhost:8000/docs)

---

## File Structure

```
incident-automation/
├── app.py              Main application
├── requirements.txt    Dependencies
├── .env               Environment variables
├── incidents.db       Database (auto-created)
├── README.md          This file
├── QUICKSTART.md      5-minute setup
├── FASTAPI_GUIDE.md   How to test API
├── PIPELINE_EXPLANATION.md   How it works
├── PROMPT_LOG_UPDATED.md     Your decisions
└── sample_data.json   Test examples
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Classification fails | Check GOOGLE_API_KEY in .env |
| Email not sending | Check SENDER_EMAIL and SENDER_PASSWORD |
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database error | `rm incidents.db && python app.py` |

---

## Production Ready

Shows understanding of:
- Microservice architecture
- AI/LLM integration
- Real email implementation
- Async patterns (background tasks)
- Database design (normalized schema)
- Error handling & resilience
- REST API best practices

---

## For Interview

1. **Open http://localhost:8000/docs** - Show Swagger UI
2. **Test an endpoint** - Create incident live
3. **Show database** - `sqlite3 incidents.db`
4. **Walk through code** - app.py create_incident() function
5. **Discuss decisions** - Read PROMPT_LOG.md

---

**Questions?** Check PIPELINE_EXPLANATION.md for details.