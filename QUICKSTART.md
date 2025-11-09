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

✅ **See response with incident_id and classification**

---

## 3️⃣ Check Database

```bash
sqlite3 incidents.db "SELECT * FROM incidents;"
```

✅ **See your incident stored**

---

## Done! ✨

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

---

## All Endpoints

| What | URL |
|------|-----|
| 📝 Create incident | `POST /api/incidents` |
| 📖 Get incident | `GET /api/incidents/{id}` |
| 👤 Customer history | `GET /api/incidents/customer/{id}` |
| ✅ Resolve incident | `PUT /api/incidents/{id}/resolve` |
| 📧 View notifications | `GET /api/notifications/{id}` |
| 📊 Statistics | `GET /api/stats` |
| 💚 Health check | `GET /health` |

---

## What Happens (6 Steps)

1. **Receive** - Customer sends message
2. **Classify** - Google Gemini AI analyzes it
3. **Ticket** - Create support ticket (TKT-xxx)
4. **Store** - Save to database
5. **Email** - Send real email to customer
6. **Remind** - Schedule 24-hour reminder

**Total time:** ~2 seconds ⚡

---

## Test Different Scenarios

**Duplicate Payment:**
```json
{
  "customer_id": "1",
  "channel": "email",
  "message": "I was charged twice",
  "email": "user@example.com"
}
```

**Fraud:**
```json
{
  "customer_id": "2",
  "channel": "email",
  "message": "I see unauthorized transaction",
  "email": "user@example.com"
}
```

**Refund:**
```json
{
  "customer_id": "3",
  "channel": "email",
  "message": "I want a refund",
  "email": "user@example.com"
}
```

---

## View Results

```bash
# All incidents
curl http://localhost:8000/api/stats

# One customer
curl http://localhost:8000/api/incidents/customer/1

# One incident
curl http://localhost:8000/api/incidents/{incident_id}
```

---

## Next: Interview Prep

Read in this order:
1. **FASTAPI_GUIDE.md** - How to demo it
2. **PIPELINE_EXPLANATION.md** - How it works
3. **PROMPT_LOG.md** - Your decisions

---

## ✅ Success Checklist

- [ ] App running (`Uvicorn running...`)
- [ ] Swagger UI loads (http://localhost:8000/docs)
- [ ] Create incident works
- [ ] Data in database
- [ ] Email sent to recipient

**All 5 done = Ready for interview! 🚀**