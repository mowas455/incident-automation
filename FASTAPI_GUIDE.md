# FastAPI Version - Incident Automation

## Key Differences from Flask

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Documentation | Manual | Automatic Swagger/OpenAPI |
| Type Hints | Optional | Required (Pydantic) |
| Server | `flask run` | `uvicorn app:app --reload` |
| API Docs | Need to add separately | Built-in at `/docs` |
| Validation | Manual | Automatic (Pydantic models) |
| Performance | Moderate | Faster (async support) |
| Error Handling | Manual | Automatic with proper status codes |

## Setup & Run
```bash
# Install dependencies
pip install fastapi uvicorn anthropic requests pydantic

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run server
python app.py
# OR
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server starts at: `http://localhost:8000`

## Swagger UI (Try It Out!)

Open browser to: **http://localhost:8000/docs**

You'll see:
- All endpoints listed with descriptions
- Input/output models
- "Try it out" button to test endpoints
- Request/response examples
- Parameter documentation

## Test Endpoints via Swagger

### 1. Create Incident
1. Click "POST /api/incidents"
2. Click "Try it out"
3. Enter JSON:
```json
{
  "customer_id": "99876",
  "channel": "whatsapp",
  "message": "My credit card payment was deducted twice yesterday."
}
```
4. Click "Execute"
5. See response with incident_id, ticket_id, classification

### 2. Get Incident Details
1. Click "GET /api/incidents/{incident_id}"
2. Click "Try it out"
3. Paste incident_id from previous response
4. Click "Execute"

### 3. Get Customer's Incidents
1. Click "GET /api/incidents/customer/{customer_id}"
2. Click "Try it out"
3. Enter customer_id: "99876"
4. Click "Execute"

### 4. Get Statistics
1. Click "GET /api/stats"
2. Click "Try it out"
3. Click "Execute"
4. See total_incidents, open_incidents, resolved_incidents, by_classification

### 5. Resolve Incident
1. Click "PUT /api/incidents/{incident_id}/resolve"
2. Click "Try it out"
3. Paste incident_id
4. Click "Execute"

## Command Line (Alternative to Swagger)
```bash
# Create incident
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "99876",
    "channel": "whatsapp",
    "message": "My credit card payment was deducted twice yesterday."
  }'

# Get incident
curl http://localhost:8000/api/incidents/{incident_id}

# Get customer incidents
curl http://localhost:8000/api/incidents/customer/99876

# Resolve incident
curl -X PUT http://localhost:8000/api/incidents/{incident_id}/resolve

# Get stats
curl http://localhost:8000/api/stats

# Health check
curl http://localhost:8000/health
```

## API Endpoints

### Incidents
- `POST /api/incidents` - Create incident (Swagger: "Try it out")
- `GET /api/incidents/{incident_id}` - Fetch incident
- `GET /api/incidents/customer/{customer_id}` - Customer's incidents
- `PUT /api/incidents/{incident_id}/resolve` - Mark resolved

### Notifications
- `GET /api/notifications/{incident_id}` - Incident notifications

### Statistics
- `GET /api/stats` - Incident statistics

### Health
- `GET /health` - Service health check

## Swagger Features

**Request/Response Models:**
- Click any endpoint → see input/output structure
- Hover over fields → see descriptions and examples
- Pydantic auto-validates before sending

**Try It Out:**
- Pre-fill example data
- Execute and see live responses
- View curl command equivalent
- See response status codes

**Documentation:**
- Every endpoint has description
- Every parameter documented
- Example values shown

## FastAPI Advantages

✅ **Auto Documentation** - No manual OpenAPI/Swagger setup
✅ **Type Safety** - Pydantic validates all inputs
✅ **Async Support** - Can use `async def` for better performance
✅ **Better Errors** - Auto 400/422 with validation details
✅ **Faster** - Uvicorn + async = better throughput
✅ **Modern** - Built for modern Python (3.7+)

## For Interview

"I switched from Flask to FastAPI because:
- Auto-generated Swagger docs (no manual setup)
- Built-in data validation with Pydantic
- Async support for better concurrency
- Better developer experience with type hints
- Automatic proper HTTP status codes"

## ReDoc (Alternative Documentation)

Open: **http://localhost:8000/redoc**

Same documentation, different UI. Choose whichever you prefer.

## Next Steps

1. Run `python app.py`
2. Open http://localhost:8000/docs
3. Try endpoints via Swagger UI
4. Watch console for detailed logs
5. Check database with `sqlite3 incidents.db`