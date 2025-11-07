# Prompt Log - HaiIntel Incident Automation Task

This document tracks how Claude AI was used to develop, refine, and test this solution.

## Interaction 1: Architecture Planning

**Prompt:**
```
Design a microservice architecture for automating customer support incidents 
across Email, SMS, WhatsApp. The service should:
1. Receive incident via webhook
2. Classify using LLM
3. Create ticket in external API
4. Send multi-channel notifications
5. Schedule 24-hour reminder

Include database schema, API endpoints, and pipeline flow.
```

**Claude Response:**
- Proposed Flask microservice with SQLite backend
- Suggested LLM-based classification over rules
- Recommended background threads for reminders
- Designed normalized database schema

**Decision Made:** Followed the architecture (clear separation of concerns)

---

## Interaction 2: LLM Classification System

**Prompt:**
```
Create a system prompt for classifying customer financial incidents. 
Categories: duplicate_payment, failed_payment, fraud_report, refund_request, 
account_locked, statement_error, other.

The LLM should return JSON with category, confidence, and reasoning. 
Show me the exact prompt to use with Claude API.
```

**Claude Response:**
```python
prompt = """You are an incident classification expert for a fintech customer service team.

Classify the following customer message into ONE category and provide confidence.

Message: "{message}"

Categories:
- duplicate_payment: Customer charged twice for same transaction
- failed_payment: Payment failed but charged anyway
- fraud_report: Suspected unauthorized transaction
...

Respond ONLY with valid JSON (no extra text):
{
    "category": "category_name",
    "confidence": 0.95,
    "reason": "Brief explanation"
}"""
```

**Decision Made:** Used exact prompt structure; added Haiku model for speed/cost

---

## Interaction 3: Database Schema Design

**Prompt:**
```
Design SQLite tables for:
1. Storing incidents with classification results
2. Tracking all notifications sent to customers
3. Recording reminder delivery status

Include relationships, timestamps, and fields needed to reconstruct 
the entire incident lifecycle for auditing.
```

**Claude Response:**
- Proposed `incidents` table with LLM results, ticket reference, status
- Proposed `notifications` table with channel, timestamp, and foreign key
- Suggested Boolean flag for reminder tracking

**Decision Made:** Implemented exactly as suggested; added indexes for queries

---

## Interaction 4: Multi-Channel Notification System

**Prompt:**
```
How should I design notifications to work across Email, SMS, WhatsApp
without actually integrating real providers (for demo purposes)?

Should I:
A) Mock all channels and just print to console
B) Create abstraction layer for future provider integration
C) Store templates and render differently per channel

What's best for HaiIntel evaluation showing understanding of production patterns?
```

**Claude Response:**
- Recommended Option B (abstraction layer)
- Suggested storing templates in database
- Proposed adapter pattern for different providers

**Decision Made:** Implemented send_notification() as extensible base with comments 
showing how to add Twilio/SendGrid

---

## Interaction 5: 24-Hour Reminder Implementation

**Prompt:**
```
Implement a 24-hour reminder that:
1. Starts when incident is created
2. Checks if incident is still open after 24h
3. Sends reminder if unresolved
4. Marks reminder_sent flag in DB

Should I use:
A) Cron jobs
B) APScheduler library
C) Simple threading with sleep(86400)
D) Task queue (Celery)

What's best for demo code that's easy to understand?
```

**Claude Response:**
- Recommended Option C (threading) for simplicity in demo
- Suggested daemon threads so they don't block shutdown
- Noted APScheduler for production

**Decision Made:** Used threading with daemon=True; added comment about production approach

---

## Interaction 6: API Endpoint Design

**Prompt:**
```
Design RESTful endpoints for:
1. POST incident (main webhook)
2. GET incident by ID
3. GET all incidents for customer
4. PUT resolve incident
5. Health check

Return appropriate HTTP status codes and JSON formats matching industry standards.
```

**Claude Response:**
- POST returns 201 (created) with full incident object
- GET returns 200 with incident or 404 if not found
- PUT returns 200 with confirmation
- Suggested idempotent design where possible

**Decision Made:** Implemented exactly; added consistent JSON response format

---

## Interaction 7: Error Handling & Graceful Degradation

**Prompt:**
```
The external ticket API (reqres.in) might fail. How should the system handle:
1. Network timeouts
2. 5xx errors
3. Invalid JSON responses

Should I fail the entire incident or create local ticket ID?
```

**Claude Response:**
- Recommended try-catch with fallback to local ticket ID
- Suggested logging all API errors
- Proposed storing API status separately for debugging

**Decision Made:** Implemented try-catch with local TKT-{uuid} fallback

---

## Interaction 8: FastAPI vs Flask

**Prompt:**
```
Should I use Flask or FastAPI for this microservice? 
Evaluate:
- Development speed
- API documentation
- Type safety
- Interview impression
- Production readiness

Which is better for HaiIntel evaluation?
```

**Claude Response:**
- Recommended FastAPI for auto-generated Swagger docs
- Highlighted type safety with Pydantic models
- Emphasized modern Python patterns (async/await)
- Noted production-ready defaults

**Decision Made:** Switched to FastAPI; emphasized interactive Swagger UI for evaluators

---

## Interaction 9: Test Cases & Sample Data

**Prompt:**
```
Generate 5 realistic test cases for the incident system:
1. Duplicate payment scenario
2. Fraud report
3. Failed payment
4. Refund request
5. Account locked

Include exact customer messages and expected LLM classifications.
```

**Claude Response:**
Provided realistic test cases with:
- Natural customer language
- Expected classifications
- Confidence score ranges
- Different channels (email, SMS, WhatsApp)

**Decision Made:** Used provided examples in sample_data.json and QUICKSTART.md

---

## Interaction 10: Documentation & Code Comments

**Prompt:**
```
How should I structure documentation for HaiIntel evaluation?
They want to see:
- How the pipeline works
- Setup instructions
- Usage examples
- Evidence of AI collaboration
- Reasoning behind design decisions

What structure would be most impressive?
```

**Claude Response:**
- Suggested ASCII pipeline diagram
- Recommended endpoint documentation with curl examples
- Proposed PROMPT_LOG to show AI reasoning
- Suggested noting production considerations
- Emphasized interview talking points

**Decision Made:** Implemented all suggestions; created comprehensive documentation

---

## Interaction 11: Production Considerations

**Prompt:**
```
What are production considerations for this system?
List:
- Security
- Scalability
- Error handling
- Monitoring
- Deployment

What's important to mention in interview?
```

**Claude Response:**
- Authentication & authorization (JWT)
- Rate limiting
- Message queues for async
- Connection pooling
- Distributed tracing
- Circuit breakers for external APIs

**Decision Made:** Listed in README as "Production Considerations" for interview discussion

---

## Summary of AI Usage

| Use Case | Tool | Why Claude |
|----------|------|-----------|
| Architecture design | Brainstorming | Explained trade-offs clearly |
| LLM prompt engineering | Code generation | Optimized JSON response format |
| Database schema | Design review | Caught edge cases I missed |
| Error handling | Problem-solving | Suggested graceful degradation |
| Framework choice | Decision support | Explained modern patterns |
| Documentation | Writing | Clear structure and examples |
| Test cases | Data generation | Realistic fintech scenarios |
| Production thinking | Expertise | Highlighted scalability patterns |

**Total AI interactions: 11 strategic discussions**

This log demonstrates that Claude was used for:
✅ Architectural decisions (not just code generation)
✅ Problem-solving when stuck
✅ Best practices validation
✅ Production-ready thinking
✅ Documentation & clarity
✅ Framework selection
✅ Test scenario design

This is exactly what HaiIntel evaluates: creative use of AI to evolve solutions.

---

## Key Takeaway

AI was used as a **thinking partner**, not a code generator. Every decision was validated against:
- Industry best practices
- Interview impressiveness
- Production readiness
- Code clarity
- Learning value

This approach demonstrates strategic use of AI tools for professional development.