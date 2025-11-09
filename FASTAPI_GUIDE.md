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
6. See the response with incident_id and classification

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
- Receives: incident_id, ticket_id, classification, confidence

### Get Incident Details
**GET** `/api/incidents/{incident_id}`
- Fetch specific incident

### Get Customer's Incidents
**GET** `/api/incidents/customer/{customer_id}`
- View all incidents for a customer

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
  "message": "Incident received and ticket created. Acknowledgments sent via email and SMS."
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
2. **Classify** - Google Gemini AI analyzes the message
3. **Create Ticket** - Generate ticket ID
4. **Store** - Save incident in SQLite database
5. **Notify** - Send email + SMS notifications
6. **Schedule Reminder** - Set 24-hour follow-up (configurable for testing)

---

## Console Output

Watch the terminal for detailed logs:

```
======================================================================
[INCIDENT RECEIVED] ID: e5ec9684-ca72-4115-bcad-8c3f833f3a34
Customer: 99876 | Channel: email
Message: My credit card payment was deducted twice.
======================================================================

[STEP 1] Classifying incident with Google Gemini...
✓ Category: duplicate_payment
✓ Confidence: 0.98
✓ Reason: Charged twice

[STEP 2] Creating ticket...
✓ Ticket created: TKT-98042a72

[STEP 3] Storing incident in database...
✓ Incident stored

[STEP 4] Sending multi-channel notifications...
✅ Email sent successfully to your-email@gmail.com
📱 SMS (Mock): Thank you for reporting...

[STEP 5] Scheduling 24-hour reminder...
✓ Reminder scheduled

[SUCCESS] Response: {...}
```

---

## Testing Flow

### **Test 1: Duplicate Payment**
```json
{
  "customer_id": "99876",
  "channel": "email",
  "message": "I was charged twice for my subscription",
  "email": "test@example.com"
}
```
Expected: `duplicate_payment` with high confidence (0.9+)

### **Test 2: Fraud Report**
```json
{
  "customer_id": "55555",
  "channel": "email",
  "message": "I see unauthorized transaction I didn't make",
  "email": "test@example.com"
}
```
Expected: `fraud_report` with high confidence (0.9+)

### **Test 3: Refund Request**
```json
{
  "customer_id": "77777",
  "channel": "sms",
  "message": "I want a refund for this charge",
  "email": "test@example.com"
}
```
Expected: `refund_request` with high confidence (0.85+)

---

## Database Queries

After creating incidents, check the database:

```bash
sqlite3 incidents.db

# View all incidents
sqlite> SELECT customer_id, classification, confidence FROM incidents;

# View notifications
sqlite> SELECT channel, status FROM notifications;

# Exit
sqlite> .quit
```

---

## Common Issues

### Issue: Email not sending
**Solution:** Check `.env` file has `SENDER_EMAIL` and `SENDER_PASSWORD`

### Issue: "Google Gemini API Error"
**Solution:** Verify `GOOGLE_API_KEY` in `.env`

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

## Next Steps

1. ✅ Run `python app.py`
2. ✅ Open http://localhost:8000/docs
3. ✅ Test endpoints via Swagger UI
4. ✅ Check console for detailed logs
5. ✅ View database with DB Browser or SQLite

---

**Happy Testing!** 🎉