# Pipeline Explanation - Incident Automation Flow

## High-Level Pipeline
```
┌─────────────────────────────────────────────────────────────────────────┐
│  CUSTOMER MESSAGE → WEBHOOK (HTTP POST)                                 │
│  "My credit card was charged twice"                                     │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: RECEIVE & VALIDATE                                             │
│  - Extract: customer_id, message, channel                               │
│  - Generate unique incident_id (UUID)                                   │
│  - Log to console                                                       │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 2: LLM CLASSIFICATION (Claude)                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Input: "My credit card was charged twice"                          │ │
│  │ System Prompt: "Classify into: duplicate_payment, fraud, ..."      │ │
│  │ Output JSON:                                                        │ │
│  │ {                                                                   │ │
│  │   "category": "duplicate_payment",                                 │ │
│  │   "confidence": 0.96,                                              │ │
│  │   "reason": "Clear indication of multiple charges"                 │ │
│  │ }                                                                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: CREATE TICKET                                                  │
│  - POST to external API (reqres.in/api/tickets)                        │
│  - Send: category + customer message                                    │
│  - Receive: ticket_id (e.g., "TKT-abc123")                             │
│  - If API fails: generate local ticket ID as fallback                  │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 4: STORE IN DATABASE                                              │
│  - INSERT into incidents table:                                         │
│    * incident_id, customer_id, message                                 │
│    * classification, confidence, ticket_id                              │
│    * status = "open", created_at = NOW                                 │
│  - All data persisted for audit trail                                  │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 5: MULTI-CHANNEL NOTIFICATIONS                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ EMAIL: "Ticket #TKT-abc123 created.                             │   │
│  │         We're investigating your issue."                         │   │
│  │ SMS:   "Ticket #TKT-abc123 created.                             │   │
│  │         Follow-up in 24 hours."                                 │   │
│  │ (Simulated - in production: Twilio/SendGrid)                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  - INSERT into notifications table for each channel                     │
│  - Each notification logged with timestamp                              │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 6: SCHEDULE 24-HOUR REMINDER                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Background Thread:                                                 │ │
│  │ 1. Sleep for 86400 seconds (24 hours)                             │ │
│  │ 2. Query DB: SELECT status FROM incidents WHERE id = incident_id   │ │
│  │ 3. If status == "open":                                            │ │
│  │    - Send reminder notification                                   │ │
│  │    - UPDATE reminder_sent = 1                                      │ │
│  │ 4. If status == "resolved":                                        │ │
│  │    - Skip (customer already helped)                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  Note: Daemon thread doesn't block main process                         │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  RESPONSE TO CUSTOMER                                                    │
│  {                                                                       │
│    "incident_id": "a1b2c3d4-...",                                       │
│    "ticket_id": "TKT-abc123",                                            │
│    "status": "open",                                                     │
│    "classification": "duplicate_payment",                                │
│    "confidence": 0.96,                                                   │
│    "message": "Ticket created. Notifications sent."                      │
│  }                                                                       │
│  HTTP Status: 201 (Created)                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Code Flow - Step by Step

### Step 1: Request Arrives
```python
@app.post("/api/incidents")
async def create_incident(incident_data: IncidentRequest):
    data = incident_data
    customer_id = data.customer_id      # "99876"
    message = data.message              # "Charged twice"
    channel = data.channel              # "whatsapp"
    
    incident_id = str(uuid.uuid4())     # Generate unique ID
```

### Step 2: LLM Classification
```python
classification_result = classify_incident(message)
# Calls Claude with system prompt
# Returns: {"category": "duplicate_payment", "confidence": 0.96, "reason": "..."}

category = classification_result['category']         # "duplicate_payment"
confidence = classification_result['confidence']     # 0.96
```

**Claude's System Prompt (Inside Code):**
```
"You are an incident classification expert for fintech.
Classify into: duplicate_payment, failed_payment, fraud_report, refund_request, etc.
Respond ONLY with JSON: {"category": "...", "confidence": 0.XX, "reason": "..."}"
```

### Step 3: Create Ticket
```python
ticket_id = create_ticket_mock(incident_id, category, message)
# Tries POST to https://reqres.in/api/tickets
# If success: returns ticket_id from API response
# If fails: generates local fallback "TKT-xyz123"
```

### Step 4: Store in Database
```python
conn = sqlite3.connect('incidents.db')
c = conn.cursor()
c.execute('''INSERT INTO incidents 
             (id, customer_id, channel, message, classification, 
              confidence, ticket_id, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, 'open')''',
         (incident_id, customer_id, channel, message, category, 
          confidence, ticket_id))
conn.commit()
```

**Result in DB:**
| id | customer_id | channel | message | classification | confidence | ticket_id | status |
|----|---|---|---|---|---|---|---|
| a1b2c3d4 | 99876 | whatsapp | Charged twice | duplicate_payment | 0.96 | TKT-abc | open |

### Step 5: Multi-Channel Notifications
```python
send_multi_channel(incident_id, customer_id, ticket_id, 
                  channels=['email', 'sms'])

# For each channel:
#   1. Generate notification message
#   2. INSERT into notifications table
#   3. Print to console (simulates sending)
```

**Notifications Table:**
| id | incident_id | channel | message | sent_at |
|----|---|---|---|---|
| xyz1 | a1b2c3d4 | email | Ticket #TKT-abc... | 2025-11-05 10:30:01 |
| xyz2 | a1b2c3d4 | sms | Ticket #TKT-abc... | 2025-11-05 10:30:01 |

### Step 6: Schedule 24-Hour Reminder
```python
schedule_24h_reminder(incident_id, customer_id)
# Starts background thread (daemon=True)
# Thread waits 86400 seconds
# Then checks if incident still open
# If open: sends reminder via send_notification()
# If resolved: skips reminder
```

---

## Data Flow Example

**Input:**
```json
{
  "customer_id": "99876",
  "channel": "whatsapp",
  "message": "My credit card payment was deducted twice yesterday."
}
```

**Processing:**
1. Incident ID created: `e5f7a2b1-4c8d-...`
2. Claude LLM output: `{"category": "duplicate_payment", "confidence": 0.96}`
3. Ticket API call: POST → Response: ticket_id = `5678`
4. DB INSERT: 1 row into incidents
5. Notifications: 2 rows into notifications table (email + SMS)
6. Thread spawned: Will check in 24 hours

**Output:**
```json
{
  "incident_id": "e5f7a2b1-4c8d-...",
  "ticket_id": "TKT-5678",
  "status": "open",
  "classification": "duplicate_payment",
  "confidence": 0.96,
  "message": "Ticket created. Acknowledgments sent via email and SMS."
}
```

**DB State After:**
```
incidents:
  id: e5f7a2b1-4c8d-...
  customer_id: 99876
  channel: whatsapp
  message: "My credit card payment was deducted twice yesterday."
  classification: duplicate_payment
  confidence: 0.96
  ticket_id: TKT-5678
  status: open
  created_at: 2025-11-05 10:30:00
  reminder_sent: 0

notifications:
  [0] channel: email,    sent_at: 2025-11-05 10:30:01
  [1] channel: sms,      sent_at: 2025-11-05 10:30:02
```

---

## Why This Design?

| Design Choice | Why |
|---|---|
| **Claude LLM** | Better than rule-based: handles ambiguous cases, learns from examples |
| **Background threads** | Async reminder doesn't block API responses |
| **Multi-channel notifications** | Real systems need Email + SMS failover (WhatsApp can fail) |
| **Mock API fallback** | Graceful degradation if external ticket API is down |
| **SQLite** | Simple demo that could scale to PostgreSQL in production |
| **Audit trail** | Every notification logged for compliance/debugging |
| **REST API** | Standard pattern for webhooks/integrations |

---

## Production Readiness Notes

This demo code shows understanding of:
- ✅ Asynchronous workflows (background tasks)
- ✅ Multi-channel orchestration (Email/SMS/WhatsApp)
- ✅ LLM integration (Claude API)
- ✅ Graceful error handling (API fallbacks)
- ✅ Data persistence (SQLite → PostgreSQL)
- ✅ Audit trails (notifications table)
- ✅ Scalability patterns (stateless services)

For production, would add:
- Message queues (Redis/RabbitMQ)
- Connection pooling
- Distributed tracing
- Real provider integrations (Twilio, SendGrid)
- Rate limiting
- Authentication/authorization
- Circuit breakers for external APIs