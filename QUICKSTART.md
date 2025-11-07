# Quick Start Guide

## Installation & Setup (2 minutes)
```bash
# Navigate to project directory
cd incident-automation

# Install dependencies
pip install -r requirements.txt

# Set API key (Claude auto-detects from env)
export ANTHROPIC_API_KEY="sk-ant-..."

# Run server (FastAPI + Uvicorn)
python app.py
```

Server starts at: `http://localhost:8000`

**🎉 Open Swagger UI: http://localhost:8000/docs** for interactive testing!

---

## Testing (5 minutes)

### Test 1: Create Incident via Swagger (Recommended)
1. Open http://localhost:8000/docs
2. Click "POST /api/incidents"
3. Click "Try it out"
4. Enter JSON and click "Execute"

### Test 1b: Create Incident via cURL
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "99876",
    "channel": "whatsapp",
    "message": "My credit card payment was deducted twice yesterday."
  }'
```

**Expected Output:**
```json
{
  "incident_id": "a1b2c3d4-e5f6-...",
  "ticket_id": "TKT-xyz123",
  "status": "open",
  "classification": "duplicate_payment",
  "confidence": 0.96,
  "message": "Incident received and ticket created. Acknowledgments sent via email and SMS."
}
```

### Test 2: Get Incident Details
```bash
curl http://localhost:8000/api/incidents/a1b2c3d4-e5f6-...
```

### Test 3: Get Customer's All Incidents
```bash
curl http://localhost:8000/api/incidents/customer/99876
```

### Test 4: Get Statistics
```bash
curl http://localhost:8000/api/stats
```

### Test 5: Resolve Incident
```bash
curl -X PUT http://localhost:8000/api/incidents/a1b2c3d4-e5f6-.../resolve
```

### Test 6: Health Check
```bash
curl http://localhost:8000/health
```

---

## Database

SQLite database is created automatically on first run: `incidents.db`

**View data:**
```bash
sqlite3 incidents.db
> SELECT * FROM incidents;
> SELECT * FROM notifications;
> .quit
```

---

## Logs & Debugging

The application prints detailed logs to console:
```
======================================================================
[INCIDENT RECEIVED] ID: a1b2c3d4-e5f6-...
Customer: 99876 | Channel: whatsapp
Message: My credit card payment was deducted twice yesterday.
======================================================================

[STEP 1] Classifying incident with LLM...
✓ Category: duplicate_payment
✓ Confidence: 0.96
✓ Reason: Clear indication of duplicate charge

[STEP 2] Creating ticket...
✓ Ticket created: TKT-xyz123

[STEP 3] Storing incident in database...
✓ Incident stored

[STEP 4] Sending multi-channel notifications...
[EMAIL] Sent to customer: Thank you...
[SMS] Sent to customer: Thank you...

[STEP 5] Scheduling 24-hour reminder...
✓ Reminder scheduled

[SUCCESS] Response: {...}
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:**
```bash
pip install fastapi uvicorn pydantic anthropic requests
```

### Issue: "ANTHROPIC_API_KEY not found"
**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
echo $ANTHROPIC_API_KEY  # Verify it's set
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
lsof -i :8000
kill -9 <PID>
```

Or run on different port by editing app.py last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Issue: "Database error"
**Solution:**
```bash
rm incidents.db
python app.py  # Recreates it
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/incidents | Create incident |
| GET | /api/incidents/{id} | Fetch incident |
| GET | /api/incidents/customer/{id} | Customer history |
| PUT | /api/incidents/{id}/resolve | Mark resolved |
| GET | /api/notifications/{id} | View notifications |
| GET | /api/stats | Statistics |
| GET | /health | Health check |

---

## Classification Categories

The LLM classifies incidents into these categories:

- `duplicate_payment` - Charged 2+ times
- `failed_payment` - Failed but charged
- `fraud_report` - Unauthorized transaction
- `refund_request` - Customer wants money back
- `account_locked` - Can't access account
- `statement_error` - Balance discrepancy
- `other` - Doesn't fit above

---

## Next Steps

1. ✅ Run `python app.py`
2. ✅ Open http://localhost:8000/docs
3. ✅ Test endpoints via Swagger UI
4. ✅ Check database: `sqlite3 incidents.db`
5. ✅ Read PROMPT_LOG.md for interview prep
6. ✅ Review PIPELINE_EXPLANATION.md to understand flow

---

## For Interview

When evaluators ask "Walk me through your code":

1. Show app.py and explain create_incident() function
2. Walk through each step (classify → ticket → notify → remind)
3. Demonstrate Swagger UI
4. Explain why you chose FastAPI (see FASTAPI_VS_FLASK.md)
5. Discuss how you used Claude (see PROMPT_LOG.md)

---

## Success Indicator

When everything works, you'll see:

✅ Terminal: "Uvicorn running on http://0.0.0.0:8000"
✅ Browser: Swagger UI loads at localhost:8000/docs
✅ Swagger: All 7 endpoints listed with descriptions
✅ Test: POST endpoint executes and returns incident_id

If all 4 work → **Everything is running correctly!**