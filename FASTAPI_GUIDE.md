# FastAPI Guide - Incident Automation

## What is FastAPI?

FastAPI is a modern Python web framework that automatically creates interactive API documentation (Swagger UI). It's perfect for building microservices.

---

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-key"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"

# Run the server
python app.py
```

Server starts at: **http://localhost:8000**

---

## Interactive Swagger UI

Open your browser to: **http://localhost:8000/docs**

You'll see all API endpoints with a "Try it out" button to test them directly!

---

## Testing Your API

### **Option 1: Use Swagger UI (Easiest)**

1. Open **http://localhost:8000/docs**
2. Click on **"POST /api/incidents"**
3. Click **"Try it out"** button
4. Enter this JSON:

```json
{
  "customer_id": "99876",
  "channel": "email",
  "message": "My credit card payment was deducted twice.",
  "email": "your-email@gmail.com"
}
```

5. Click **"Execute"**
6. See the response with incident_id, classification, AND **sentiment**

---

### **Option 2: Use cURL (Command Line)**

```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "99876",
    "channel": "email",
    "message": "My credit card payment was deducted twice.",
    "email": "your-email@gmail.com"
  }'
```

---

## API Endpoints

### Create Incident (Main Endpoint)
**POST** `/api/incidents`
- Send customer issue
- Analyzes sentiment + classifies with AI
- Receives: incident_id, ticket_id, classification, confidence, **sentiment**

### Get Incident Details
**GET** `/api/incidents/{incident_id}`
- Fetch specific incident with all details including **sentiment & polarity**

### Get Customer's Incidents
**GET** `/api/incidents/customer/{customer_id}`
- View all incidents for a customer with sentiment data

### Resolve Incident
**PUT** `/api/incidents/{incident_id}/resolve`
- Mark incident as resolved

### Get Notifications
**GET** `/api/notifications/{incident_id}`
- View all notifications sent for incident

### Get Statistics
**GET** `/api/stats`
- Total incidents, open incidents, resolved incidents, breakdown by category

### Health Check
**GET** `/health`
- Check if service is running

---

## Example Responses

### Create Incident Response (201 Created)
```json
{
  "incident_id": "e5ec9684-ca72-4115-bcad-8c3f833f3a34",
  "ticket_id": "TKT-98042a72",
  "status": "open",
  "classification": "duplicate_payment",
  "confidence": 0.98,
  "message": "Incident received and ticket created. Sentiment: negative. Acknowledgments sent via email and SMS."
}
```

### Get Incident Response (with Sentiment & Polarity)
```json
{
  "id": "e5ec9684-ca72-4115-bcad-8c3f833f3a34",
  "customer_id": "99876",
  "channel": "email",
  "message": "My credit card payment was deducted twice.",
  "classification": "duplicate_payment",
  "confidence": 0.98,
  "sentiment": "negative",
  "polarity": -0.57,
  "ticket_id": "TKT-98042a72",
  "status": "open",
  "created_at": "2025-11-09 08:00:00",
  "resolved_at": null,
  "reminder_sent": 0
}
```

### Get Statistics Response
```json
{
  "total_incidents": 5,
  "open_incidents": 2,
  "resolved_incidents": 3,
  "by_classification": [
    {"category": "duplicate_payment", "count": 2},
    {"category": "fraud_report", "count": 1},
    {"category": "refund_request", "count": 2}
  ]
}
```

---

## What Happens Behind the Scenes

When you POST to `/api/incidents`:

1. **Validate** - Check all required fields are present
2. **Analyze Sentiment** - VADER sentiment analysis (positive/negative/neutral)
3. **Classify** - Google Gemini AI analyzes the message
4. **Create Ticket** - Generate ticket ID
5. **Store** - Save incident + sentiment in SQLite database
6. **Notify** - Send email + SMS notifications
7. **Schedule Reminder** - Set 24-hour follow-up (configurable for testing)

---

## Console Output

Watch the terminal for detailed logs:

```
======================================================================
[INCIDENT RECEIVED] ID: e5ec9684-ca72-4115-bcad-8c3f833f3a34
Customer: 99876 | Channel: email
Message: My credit card payment was deducted twice.
======================================================================

[STEP 1] Analyzing customer sentiment...
✓ Sentiment: negative (polarity: -0.57)

[STEP 2] Classifying incident with Google Gemini...
✓ Category: duplicate_payment
✓ Confidence: 0.98
✓ Reason: Charged twice

[STEP 3] Creating ticket...
✓ Ticket created: TKT-98042a72

[STEP 4] Storing incident in database...
✓ Incident stored

[STEP 5] Sending multi-channel notifications...
✅ Email sent successfully to your-email@gmail.com
📱 SMS (Mock): Thank you for reporting...

[STEP 6] Scheduling 24-hour reminder...
✓ Reminder scheduled

[SUCCESS] Response: {...}
```

---

## Testing Flow

### **Test 1: Angry Customer (Negative Sentiment)**
```json
{
  "customer_id": "99876",
  "channel": "email",
  "message": "I'm FURIOUS! I was charged twice! This is absolutely ridiculous!",
  "email": "test@example.com"
}
```
Expected: 
- Classification: `duplicate_payment` (0.98 confidence)
- Sentiment: `negative` 
- Polarity: -0.85

### **Test 2: Professional Customer (Neutral Sentiment)**
```json
{
  "customer_id": "55555",
  "channel": "email",
  "message": "I noticed duplicate charges in my account. Please investigate.",
  "email": "test@example.com"
}
```
Expected: 
- Classification: `duplicate_payment` (0.97 confidence)
- Sentiment: `neutral` 
- Polarity: 0.0

### **Test 3: Fraud Report (Negative Sentiment)**
```json
{
  "customer_id": "77777",
  "channel": "email",
  "message": "I see unauthorized transaction I didn't make",
  "email": "test@example.com"
}
```
Expected: 
- Classification: `fraud_report` (0.95+ confidence)
- Sentiment: `negative`
- Polarity: -0.65

### **Test 4: Grateful Customer (Positive Sentiment)**
```json
{
  "customer_id": "88888",
  "channel": "email",
  "message": "Thank you for fixing my duplicate charge so quickly! Excellent service!",
  "email": "test@example.com"
}
```
Expected: 
- Classification: `refund_request` or `other` (context dependent)
- Sentiment: `positive`
- Polarity: 0.75

---

## Database Queries

After creating incidents, check the database:

```bash
sqlite3 incidents.db

# View all incidents with sentiment
sqlite> SELECT customer_id, sentiment, polarity, classification FROM incidents;

# View negative sentiment incidents
sqlite> SELECT customer_id, sentiment, polarity FROM incidents WHERE sentiment = 'negative';

# View notifications
sqlite> SELECT channel, status FROM notifications;

# Exit
sqlite> .quit
```

---

## Sentiment Interpretation

| Sentiment | Polarity Range | Meaning | Example |
|-----------|--------|---------|---------|
| **Negative** | -1.0 to -0.1 | Angry, frustrated customer | "FURIOUS!", "disgusted" |
| **Neutral** | -0.1 to 0.1 | Factual, professional tone | "Please investigate this" |
| **Positive** | 0.1 to 1.0 | Happy, grateful customer | "Thank you!", "excellent" |

---

## Common Issues

### Issue: Email not sending
**Solution:** Check `.env` file has `SENDER_EMAIL` and `SENDER_PASSWORD`

### Issue: "Google Gemini API Error"
**Solution:** Verify `GOOGLE_API_KEY` in `.env`

### Issue: Sentiment shows "neutral" for everything
**Solution:** That's normal for mixed messages. Try very negative or positive text to see the difference.

### Issue: Port 8000 already in use
**Solution:** 
```bash
lsof -i :8000
kill -9 <PID>
```

Or edit `app.py` last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## Why FastAPI?

✅ **Auto Swagger Docs** - No manual setup needed
✅ **Type Safety** - Pydantic validates all inputs
✅ **Fast** - One of the fastest Python frameworks
✅ **Easy Testing** - Built-in "Try it out" buttons
✅ **Production Ready** - Used by top companies

---

## Features Demonstrated

✅ **AI Classification** - Google Gemini integration
✅ **Sentiment Analysis** - VADER NLP for customer emotion detection
✅ **Real Email** - Gmail SMTP integration
✅ **Database Design** - SQLite with normalized schema
✅ **Async Operations** - Background threads for reminders
✅ **Multi-Channel** - Email, SMS, WhatsApp ready
✅ **Error Handling** - Graceful degradation
✅ **Production Patterns** - Scalable architecture

---

## Next Steps

1. ✅ Run `python app.py`
2. ✅ Open http://localhost:8000/docs
3. ✅ Test endpoints via Swagger UI (Try different sentiment messages)
4. ✅ Check console for detailed logs showing sentiment analysis
5. ✅ View database with: `sqlite3 incidents.db`

---

**Happy Testing!** 🎉

**Note:** Sentiment analysis uses VADER (Valence Aware Dictionary and sEntiment Reasoner), which is excellent for social media and customer messages. Polarity ranges from -1.0 (very negative) to +1.0 (very positive).