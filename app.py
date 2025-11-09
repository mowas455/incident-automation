from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
import json
import threading
import time
from datetime import datetime
import uuid
import uvicorn
from dotenv import load_dotenv
import os
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Load .env file
load_dotenv()

# Set Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize FastAPI app
app = FastAPI(
    title="Incident Automation Flow API",
    description="Automates customer support incidents across Email, SMS, WhatsApp channels",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC MODELS (for API validation & Swagger docs)
# ============================================================================

class IncidentRequest(BaseModel):
    """Customer incident submission"""
    customer_id: str = Field(..., description="Unique customer identifier", example="99876")
    message: str = Field(..., description="Customer's issue description", example="My credit card payment was deducted twice yesterday.")
    channel: str = Field(default="email", description="Communication channel", example="whatsapp")
    email: str = Field(default=None, description="Customer email address", example="customer@example.com")  # ← ADD THIS


class ClassificationResult(BaseModel):
    """LLM classification output"""
    category: str = Field(..., description="Classified incident category")
    confidence: float = Field(..., description="Confidence score 0.0-1.0")
    reason: str = Field(..., description="Classification reasoning")


class IncidentResponse(BaseModel):
    """Incident creation response"""
    incident_id: str = Field(..., description="Unique incident ID")
    ticket_id: str = Field(..., description="External ticket ID")
    status: str = Field(..., description="Current incident status")
    classification: str = Field(..., description="Incident category")
    confidence: float = Field(..., description="Classification confidence")
    message: str = Field(..., description="Response message")


class IncidentDetail(BaseModel):
    """Incident details"""
    id: str
    customer_id: str
    channel: str
    message: str
    classification: str
    confidence: float
    ticket_id: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None
    reminder_sent: int


class NotificationRecord(BaseModel):
    """Notification record"""
    id: str
    incident_id: str
    channel: str
    message: str
    status: str
    sent_at: str


# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        channel TEXT NOT NULL,
        message TEXT NOT NULL,
        classification TEXT NOT NULL,
        confidence REAL NOT NULL,
        ticket_id TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        reminder_sent BOOLEAN DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        channel TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'sent',
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(incident_id) REFERENCES incidents(id)
    )''')

    conn.commit()
    conn.close()


init_db()


# ============================================================================
# MOCK NOTIFICATION SYSTEM
# ============================================================================

def send_notification(incident_id: str, channel: str, message: str, customer_email: str = None) -> str:
    """Send notifications across different channels"""
    notification_id = str(uuid.uuid4())

    # Store in database
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('''INSERT INTO notifications (id, incident_id, channel, message, status)
                 VALUES (?, ?, ?, ?, 'sent')''',
              (notification_id, incident_id, channel, message))
    conn.commit()
    conn.close()

    # Send actual notification based on channel
    if channel.lower() == 'email' and customer_email:
        send_email(customer_email, incident_id, message)
    elif channel.lower() == 'sms':
        send_sms_mock(message)
    elif channel.lower() == 'whatsapp':
        send_whatsapp_mock(message)

    print(f"[{channel.upper()}] Sent to customer: {message[:50]}...")
    return notification_id


def send_email(recipient_email: str, incident_id: str, message: str) -> bool:
    """Send actual email to customer"""
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            print(f"⚠️  Email credentials not configured in .env")
            return False

        # Create email
        subject = f"Incident Update - Ticket {incident_id}"

        body = f"""
        Hello,

        Thank you for reporting this issue to us.

        Incident ID: {incident_id}
        Status: Your ticket has been created and is being investigated.

        Message:
        {message}

        We will follow up with you within 24 hours.

        Best regards,
        Customer Support Team
        """

        # Setup email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email via Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent successfully to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"❌ Email Auth Error: Check SENDER_EMAIL and SENDER_PASSWORD in .env")
        return False
    except Exception as e:
        print(f"❌ Email Error: {e}")
        return False


def send_sms_mock(message: str) -> bool:
    """Mock SMS sending (for production, use Twilio)"""
    print(f"📱 SMS (Mock): {message[:50]}...")
    return True


def send_whatsapp_mock(message: str) -> bool:
    """Mock WhatsApp sending (for production, use Twilio)"""
    print(f"💬 WhatsApp (Mock): {message[:50]}...")
    return True


def send_multi_channel(incident_id: str, customer_id: str,
                       ticket_id: str,
                       customer_email: str = None,
                       channels: List[str] = None):
    """Send acknowledgment across multiple channels"""
    if channels is None:
        channels = ['email', 'sms']

    message = f"""
    Thank you for reporting this issue.

    We've created ticket #{ticket_id} and our team is investigating.
    We'll follow up within 24 hours.

    Reference: Incident {incident_id}
    """

    for channel in channels:
        send_notification(incident_id, channel, message, customer_email=customer_email)


# ============================================================================
# LLM CLASSIFICATION (MAIN INTELLIGENCE)
# ============================================================================
def classify_incident(message: str) -> dict:
    """Use Google Gemini to classify the incident and extract details"""

    prompt = f"""You are an incident classification expert for a fintech customer service team.

Classify the following customer message into ONE category and provide a confidence score between 0.0 and 1.0.

Customer Message: "{message}"

CLASSIFICATION TASK:
Analyze the customer message and classify it into ONE of these categories:

1. duplicate_payment - Customer was charged multiple times for the same transaction/service
   Examples: "charged twice", "double billed", "money deducted twice"

2. failed_payment - Payment transaction failed but money was still deducted from account
   Examples: "payment failed but still charged", "transaction declined but money gone"

3. fraud_report - Customer suspects unauthorized or fraudulent activity
   Examples: "unauthorized transaction", "I didn't make this purchase", "suspicious activity"

4. refund_request - Customer explicitly requests a refund or money back
   Examples: "I want a refund", "please reverse the charge", "return my money"

5. account_locked - Customer cannot access their account
   Examples: "can't log in", "account locked", "password not working"

6. statement_error - Discrepancy in account balance or statement
   Examples: "balance is wrong", "statement doesn't match", "missing transaction"

7. other - Message doesn't fit any of the above categories

Respond with ONLY valid JSON, no markdown, no extra text:
{{"category": "one_of_the_categories_above", "confidence": 0.95, "reason": "2-3 word explanation"}}"""

    try:
        # Use the free gemini-2.0-flash model
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=200,
            )
        )

        # Check if response is empty
        if not response or not response.candidates or len(response.candidates) == 0:
            print(f"❌ Empty response from Gemini")
            return {
                "category": "other",
                "confidence": 0.3,
                "reason": "Empty response"
            }

        # Get text safely
        if not response.candidates[0].content or not response.candidates[0].content.parts:
            print(f"❌ No content in response")
            return {
                "category": "other",
                "confidence": 0.3,
                "reason": "No content"
            }

        response_text = response.candidates[0].content.parts[0].text.strip()
        print(f"[DEBUG] Google Gemini Response: {response_text}")

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            # Remove ```json or ``` at start
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        print(f"[DEBUG] Cleaned Response: {response_text}")

        # Try to parse JSON
        result = json.loads(response_text)

        # Validate response
        if "category" in result and "confidence" in result:
            return result
        else:
            return {
                "category": "other",
                "confidence": 0.3,
                "reason": "Invalid response format"
            }

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"   Response was: {response_text if 'response_text' in locals() else 'N/A'}")
        return {
            "category": "other",
            "confidence": 0.3,
            "reason": "Parse failed"
        }
    except IndexError as e:
        print(f"❌ Index Error (Empty Response): {e}")
        return {
            "category": "other",
            "confidence": 0.3,
            "reason": "Empty response from API"
        }
    except Exception as e:
        print(f"❌ Google Gemini API Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return {
            "category": "other",
            "confidence": 0.3,
            "reason": "API error"
        }
# ============================================================================
# MOCK TICKET CREATION
# ============================================================================

def create_ticket_mock(incident_id: str, classification: str, message: str) -> str:
    """Simulate ticket creation (in real world, POST to external API)"""
    import requests

    payload = {
        "name": f"Incident {incident_id}: {classification}",
        "description": message,
        "status": "open"
    }

    try:
        response = requests.post('https://reqres.in/api/tickets', json=payload, timeout=5)
        if response.status_code == 201:
            ticket_data = response.json()
            ticket_id = str(ticket_data.get('id', str(uuid.uuid4())))
            print(f"✓ Ticket created: {ticket_id}")
            return ticket_id
    except Exception as e:
        print(f"Ticket API error: {e}")

    ticket_id = f"TKT-{str(uuid.uuid4())[:8]}"
    return ticket_id


# ============================================================================
# 24-HOUR REMINDER SYSTEM
# ============================================================================

reminder_threads = {}


def schedule_24h_reminder(incident_id: str, c_email: str, channel: str):
    """Schedule a reminder after 24 hours if ticket remains open"""

    def check_and_remind():
        time.sleep(86400)  # Wait 24 hours

        conn = sqlite3.connect('incidents.db')
        c = conn.cursor()
        c.execute('SELECT status FROM incidents WHERE id = ?', (incident_id,))
        row = c.fetchone()
        conn.close()

        if row and row[0] == 'open':
            reminder_msg = f"""
            Reminder: Your support ticket {incident_id} is still open.
            We're working on resolving your issue. Thank you for your patience.
            """
            send_notification(incident_id, channel, reminder_msg, customer_email=c_email)

            conn = sqlite3.connect('incidents.db')
            c = conn.cursor()
            c.execute('UPDATE incidents SET reminder_sent = 1 WHERE id = ?', (incident_id,))
            conn.commit()
            conn.close()

    thread = threading.Thread(target=check_and_remind, daemon=True)
    thread.start()
    reminder_threads[incident_id] = thread


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Check if service is running"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# MAIN API ENDPOINTS
# ============================================================================

@app.post("/api/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, tags=["Incidents"])
async def create_incident(incident_data: IncidentRequest):
    """
    Create and process a new incident.

    This endpoint:
    1. Receives customer incident via webhook
    2. Classifies using OpenAI LLM
    3. Creates ticket in external system
    4. Sends multi-channel notifications
    5. Schedules 24-hour reminder

    **Example Request:**
```json
    {
      "customer_id": "99876",
      "channel": "whatsapp",
      "message": "My credit card payment was deducted twice yesterday."
      "email": "customer@example.com"
    }
```
    """

    # Validate input
    if not incident_data.customer_id or not incident_data.message:
        raise HTTPException(status_code=400, detail="Missing customer_id or message")

    customer_id = incident_data.customer_id
    message = incident_data.message
    channel = incident_data.channel

    incident_id = str(uuid.uuid4())

    print(f"\n{'=' * 70}")
    print(f"[INCIDENT RECEIVED] ID: {incident_id}")
    print(f"Customer: {customer_id} | Channel: {channel}")
    print(f"Message: {message}")
    print(f"{'=' * 70}")

    # Step 1: Classify with LLM
    print("\n[STEP 1] Classifying incident with Google Gemini...")
    classification_result = classify_incident(message)

    category = classification_result['category']
    confidence = classification_result['confidence']
    reason = classification_result['reason']

    print(f"✓ Category: {category}")
    print(f"✓ Confidence: {confidence}")
    print(f"✓ Reason: {reason}")

    # Step 2: Create ticket
    print("\n[STEP 2] Creating ticket...")
    ticket_id = create_ticket_mock(incident_id, category, message)

    # Step 3: Store in database
    print("\n[STEP 3] Storing incident in database...")
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('''INSERT INTO incidents 
                 (id, customer_id, channel, message, classification, confidence, ticket_id, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, 'open')''',
              (incident_id, customer_id, channel, message, category, confidence, ticket_id))
    conn.commit()
    conn.close()
    print("✓ Incident stored")

    # Step 4: Send multi-channel notifications
    print("\n[STEP 4] Sending multi-channel notifications...")
    send_multi_channel(incident_id, customer_id, ticket_id,
                       customer_email=incident_data.email,
                       channels=['email', 'sms'])

    # Step 5: Schedule 24-hour reminder
    print("\n[STEP 5] Scheduling 24-hour reminder...")
    schedule_24h_reminder(incident_id, incident_data.email, channel)
    print("✓ Reminder scheduled")

    response = {
        "incident_id": incident_id,
        "ticket_id": ticket_id,
        "status": "open",
        "classification": category,
        "confidence": confidence,
        "message": "Incident received and ticket created. Acknowledgments sent via email and SMS."
    }

    print(f"\n[SUCCESS] Response: {json.dumps(response, indent=2)}")
    return response


@app.get("/api/incidents/{incident_id}", response_model=IncidentDetail, tags=["Incidents"])
async def get_incident(incident_id: str):
    """Fetch incident details by ID"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('SELECT * FROM incidents WHERE id = ?', (incident_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")

    columns = ['id', 'customer_id', 'channel', 'message', 'classification',
               'confidence', 'ticket_id', 'status', 'created_at', 'resolved_at', 'reminder_sent']
    incident = dict(zip(columns, row))

    return incident


@app.get("/api/incidents/customer/{customer_id}", response_model=List[IncidentDetail], tags=["Incidents"])
async def get_customer_incidents(customer_id: str):
    """Fetch all incidents for a specific customer"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('SELECT * FROM incidents WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
    rows = c.fetchall()
    conn.close()

    columns = ['id', 'customer_id', 'channel', 'message', 'classification',
               'confidence', 'ticket_id', 'status', 'created_at', 'resolved_at', 'reminder_sent']
    incidents = [dict(zip(columns, row)) for row in rows]

    return incidents


@app.put("/api/incidents/{incident_id}/resolve", tags=["Incidents"])
async def resolve_incident(incident_id: str):
    """Mark an incident as resolved"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('''UPDATE incidents SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP 
                 WHERE id = ?''', (incident_id,))
    rows_updated = c.rowcount
    conn.commit()
    conn.close()

    if rows_updated == 0:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"message": "Incident resolved", "incident_id": incident_id}


@app.get("/api/notifications/{incident_id}", response_model=List[NotificationRecord], tags=["Notifications"])
async def get_incident_notifications(incident_id: str):
    """Fetch all notifications for an incident"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('SELECT * FROM notifications WHERE incident_id = ? ORDER BY sent_at DESC', (incident_id,))
    rows = c.fetchall()
    conn.close()

    columns = ['id', 'incident_id', 'channel', 'message', 'status', 'sent_at']
    notifications = [dict(zip(columns, row)) for row in rows]

    return notifications


@app.get("/api/stats", tags=["Statistics"])
async def get_stats():
    """Get incident statistics"""
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM incidents')
    total_incidents = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM incidents WHERE status = "open"')
    open_incidents = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM incidents WHERE status = "resolved"')
    resolved_incidents = c.fetchone()[0]

    c.execute('''SELECT classification, COUNT(*) as count FROM incidents 
                 GROUP BY classification ORDER BY count DESC''')
    classification_stats = [{"category": row[0], "count": row[1]} for row in c.fetchall()]

    conn.close()

    return {
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "resolved_incidents": resolved_incidents,
        "by_classification": classification_stats
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
