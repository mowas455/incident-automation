# Quick Start - 5 Minutes

## 1️⃣ Install & Run

```bash
cd incident-automation
pip install -r requirements.txt
python app.py
```

**✅ See:** `Uvicorn running on http://0.0.0.0:8000`

---

## 2️⃣ Test It

Open: **http://localhost:8000/docs**

Click **"POST /api/incidents"** → **"Try it out"**

Enter:
```json
{
  "customer_id": "99876",
  "channel": "email",
  "message": "I was charged twice",
  "email": "test@example.com"
}
```

Click **"Execute"**

✅ **See response with:**
- `incident_id`
- `classification` (e.g., "duplicate_payment")
- **`sentiment` (e.g., "negative")** ← NEW

---

## 3️⃣ Check Database

```bash
sqlite3 incidents.db "SELECT customer_id, sentiment, polarity, classification FROM incidents;"
```

✅ **See your incident with sentiment analysis stored**

---

## 4️⃣ Done! ✨

Your API is working. All 7 endpoints are live at: **http://localhost:8000/docs**

---

## Common Fixes

**Port in use?**
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Dependencies missing?**
```bash
pip install -r requirements.txt
```

**Database broken?**
```bash
rm incidents.db
python app.py
```

**Environment variables?**
```bash
export GOOGLE_API_KEY="your-key"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
```

---

## All 7 Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/incidents` | Create incident (main) |
| GET | `/api/incidents/{id}` | Get with sentiment & polarity |
| GET | `/api/incidents/customer/{id}` | Customer history |
| PUT | `/api/incidents/{id}/resolve` | Mark resolved |
| GET | `/api/notifications/{id}` | View notifications sent |
| GET | `/api/stats` | Statistics & breakdown |
| GET | `/health` | Health check |

---

## What Happens (7 Steps)

1. **Receive** - Customer sends message
2. **Analyze Sentiment** - VADER detects emotion (negative/neutral/positive)
3. **Classify** - Google Gemini AI categorizes issue
4. **Create Ticket** - Generate support ticket (TKT-xxx)
5. **Store** - Save to database with sentiment + classification
6. **Email** - Send real email to customer
7. **Remind** - Schedule 24-hour reminder (40s for testing)

**Total time:** ~2-4 seconds ⚡

---

## Test Different Scenarios

### Test 1: Angry Customer (Negative Sentiment)
```json
{
  "customer_id": "1",
  "channel": "email",
  "message": "I'm FURIOUS! I was charged TWICE! This is absolutely ridiculous!",
  "email": "user@example.com"
}
```

Expected Response:
- Classification: `duplicate_payment`
- Sentiment: **`negative`**
- Polarity: **`-0.85`** (very negative)

---

### Test 2: Professional Customer (Neutral Sentiment)
```json
{
  "customer_id": "2",
  "channel": "email",
  "message": "I noticed duplicate charges in my account. Please investigate.",
  "email": "user@example.com"
}
```

Expected Response:
- Classification: `duplicate_payment`
- Sentiment: **`neutral`**
- Polarity: **`-0.1 to 0.1`** (factual tone)

---

### Test 3: Fraud Report (Negative Sentiment)
```json
{
  "customer_id": "3",
  "channel": "email",
  "message": "I see unauthorized transaction I didn't make",
  "email": "user@example.com"
}
```

Expected Response:
- Classification: `fraud_report`
- Sentiment: **`negative`**
- Polarity: **`-0.65`** (frustrated)

---

### Test 4: Grateful Customer (Positive Sentiment)
```json
{
  "customer_id": "4",
  "channel": "email",
  "message": "Thank you for fixing my duplicate charge so quickly! Excellent service!",
  "email": "user@example.com"
}
```

Expected Response:
- Sentiment: **`positive`**
- Polarity: **`0.75`** (very positive)

---

## View Results

```bash
# All incidents with sentiment
curl http://localhost:8000/api/stats

# One customer's history
curl http://localhost:8000/api/incidents/customer/1

# One incident (with sentiment & polarity)
curl http://localhost:8000/api/incidents/{incident_id}

# All notifications
curl http://localhost:8000/api/notifications/{incident_id}
```

---

## Sentiment Scores Explained

| Sentiment | Polarity | Meaning |
|-----------|----------|---------|
| **negative** | -1.0 to -0.1 | Angry, frustrated → Consider escalation |
| **neutral** | -0.1 to +0.1 | Professional, factual → Standard handling |
| **positive** | +0.1 to +1.0 | Happy, grateful → Satisfaction response |

---

## Console Output Example

```
======================================================================
[INCIDENT RECEIVED] ID: e5f7a2b1-4c8d-...
Customer: 99876 | Channel: email
Message: I was charged twice!
======================================================================

[STEP 1] Analyzing customer sentiment...
✓ Sentiment: negative (polarity: -0.57)

[STEP 2] Classifying incident with Google Gemini...
✓ Category: duplicate_payment
✓ Confidence: 0.98
✓ Reason: deducted twice

[STEP 3] Creating ticket...
✓ Ticket created: TKT-98042a72

[STEP 4] Storing incident in database...
✓ Incident stored

[STEP 5] Sending multi-channel notifications...
✅ Email sent successfully to test@example.com
[EMAIL] Sent to customer: Payment issue reported...
📱 SMS (Mock): Payment issue reported...

[STEP 6] Scheduling 24-hour reminder...
✓ Reminder scheduled

[SUCCESS] Response: {...}
```

---

## Database Schema (What Gets Stored)

```sql
incidents table:
┌─────────────────┬──────────────────────────────────────┐
│ Column          │ Example                              │
├─────────────────┼──────────────────────────────────────┤
│ id              │ e5f7a2b1-4c8d-...                    │
│ customer_id     │ 99876                                │
│ message         │ I was charged twice                  │
│ sentiment       │ negative                             │
│ polarity        │ -0.57                                │
│ classification  │ duplicate_payment                    │
│ confidence      │ 0.98                                 │
│ ticket_id       │ TKT-98042a72                         │
│ status          │ open                                 │
│ created_at      │ 2025-11-09 10:30:00                  │
│ reminder_sent   │ 0                                    │
└─────────────────┴──────────────────────────────────────┘
```

---

## ✅ Success Checklist

- [ ] App running (`Uvicorn running...`)
- [ ] Swagger UI loads (http://localhost:8000/docs)
- [ ] Create incident works
- [ ] Response includes **sentiment** field
- [ ] Data in database with **sentiment & polarity**
- [ ] Email sent to recipient
- [ ] Reminder triggers after 40 seconds

**All 7 done = Ready for HaiIntel interview! 🚀**

---

## Key Features to Highlight

| Feature | What It Shows |
|---------|--------------|
| **Sentiment Analysis** | NLP understanding, emotion detection |
| **AI Classification** | LLM integration, prompt engineering |
| **Real Email** | Production integration, SMTP knowledge |
| **Database Design** | Normalization, ACID principles |
| **Async Reminders** | Concurrency patterns, threading |
| **Error Handling** | Graceful degradation, resilience |
| **Swagger UI** | FastAPI modern patterns |

---

## Troubleshooting

**Issue:** Sentiment shows "neutral" for everything
- Solution: Try very negative or positive messages (see Test 1 & 4)

**Issue:** Email not sending
- Solution: Check `.env` has SENDER_EMAIL and SENDER_PASSWORD

**Issue:** "Google Gemini API Error"
- Solution: Verify GOOGLE_API_KEY in `.env`

**Issue:** Classification not working
- Solution: Ensure message is detailed enough (not just "help")

---

## Production Notes

This demo shows:
- ✅ Sentiment analysis (VADER)
- ✅ AI classification (Google Gemini)
- ✅ Real emails (Gmail SMTP)
- ✅ Database design (SQLite)
- ✅ Async operations (threading)

For production, add:
- PostgreSQL (instead of SQLite)
- Redis message queue
- Twilio for real SMS/WhatsApp
- JWT authentication
- Rate limiting
- Monitoring & alerting

---

**Ready to impress? Open http://localhost:8000/docs and start testing! 🎉**