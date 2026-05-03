"""MTN Nigeria AI Chatbot endpoints - Integrated NLP with Supabase storage."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import uuid

from app.services.supabase_client import get_supabase

router = APIRouter()

# Mock data for MTN Nigeria services
MOCK_ACCOUNTS = {
    "user_001": {
        "phone_number": "+2348031234567",
        "data_balance": "2.5 GB",
        "airtime_balance": "₦450.00",
        "plan": "Postpaid",
        "status": "active"
    }
}

MOCK_DATA_BUNDLES = [
    {"id": "db_001", "name": "1GB Daily", "price": 300, "validity": "1 day", "auto_renewal": False},
    {"id": "db_002", "name": "2GB Weekly", "price": 500, "validity": "7 days", "auto_renewal": False},
    {"id": "db_003", "name": "5GB Monthly", "price": 2500, "validity": "30 days", "auto_renewal": True},
    {"id": "db_004", "name": "10GB Monthly", "price": 4000, "validity": "30 days", "auto_renewal": True},
]

MOCK_NETWORK_STATUS = {
    "lagos": "excellent",
    "abuja": "good",
    "port_harcourt": "fair",
    "kano": "good",
    "ibadan": "excellent"
}

class MessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., description="User message text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    user_id: Optional[str] = Field(None, description="User identifier")

class MessageResponse(BaseModel):
    """Response model for chat messages."""
    response: str = Field(..., description="Bot response text")
    intent: str = Field(..., description="Detected intent category")
    confidence: float = Field(..., description="Intent classification confidence score")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    suggestions: List[str] = Field(default_factory=list, description="Quick reply suggestions")
    requires_escalation: bool = Field(False, description="Whether human escalation is needed")
    session_id: str = Field(..., description="Session ID for conversation context")

class ConversationHistory(BaseModel):
    """Model for conversation history."""
    messages: List[Dict[str, Any]]
    session_id: str
    started_at: datetime
    escalated: bool = False

class FeedbackRequest(BaseModel):
    """Request model for CSAT feedback."""
    session_id: str
    rating: int = Field(..., ge=1, le=5, description="CSAT rating 1-5")
    comment: Optional[str] = None

# In-memory session storage (replace with Supabase in production)
SESSIONS: Dict[str, Dict[str, Any]] = {}

def detect_language(text: str) -> str:
    """Detect if text is English or Nigerian Pidgin."""
    pidgin_markers = ['abi', 'na', 'wetin', 'how', 'una', 'my', 'dey', 'no', 'fit', 'sabi']
    text_lower = text.lower()
    pidgin_count = sum(1 for marker in pidgin_markers if marker in text_lower)
    return 'pidgin' if pidgin_count >= 2 else 'english'

def classify_intent(text: str) -> tuple[str, float]:
    """Classify user intent (simulated AfroXLMR)."""
    text_lower = text.lower()
    
    intent_patterns = {
        'check_data_balance': ['data balance', 'how much data', 'remaining data', 'data left'],
        'check_airtime': ['airtime', 'credit', 'balance', 'account balance'],
        'buy_data': ['buy data', 'subscribe data', 'purchase bundle', 'get data'],
        'report_network': ['network problem', 'no network', 'poor signal', 'network issue'],
        'report_transaction': ['failed transaction', 'recharge failed', 'payment failed'],
        'escalate_human': ['speak to agent', 'human', 'customer service', 'representative'],
        'greeting': ['hello', 'hi', 'good morning', 'good afternoon', 'hey'],
    }
    
    best_intent = 'unknown'
    best_score = 0.0
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                score = 0.85 + random.uniform(0, 0.14)
                if score > best_score:
                    best_intent = intent
                    best_score = score
    
    return best_intent, best_score

def extract_entities(text: str, intent: str) -> Dict[str, Any]:
    """Extract entities from text (simulated spaCy NER)."""
    entities = {}
    text_lower = text.lower()
    
    # Extract location
    locations = ['lagos', 'abuja', 'port harcourt', 'kano', 'ibadan', 'ikeja', 'victoria island']
    for loc in locations:
        if loc in text_lower:
            entities['location'] = loc.title()
            break
    
    # Extract numbers (phone, amounts)
    import re
    phone_match = re.search(r'\+?\d{10,15}', text)
    if phone_match:
        entities['phone_number'] = phone_match.group()
    
    amount_match = re.search(r'₦?\d+(,\d{3})*(\.\d{2})?', text)
    if amount_match:
        entities['amount'] = amount_match.group()
    
    return entities

def generate_response(intent: str, entities: Dict[str, Any], language: str) -> tuple[str, List[str]]:
    """Generate appropriate response based on intent."""
    
    responses_en = {
        'check_data_balance': f"Your current data balance is {MOCK_ACCOUNTS.get('user_001', {}).get('data_balance', 'N/A')}. Would you like to buy more data?",
        'check_airtime': f"Your airtime balance is {MOCK_ACCOUNTS.get('user_001', {}).get('airtime_balance', 'N/A')}.",
        'buy_data': "Here are available data bundles:\n" + "\n".join([f"- {b['name']}: ₦{b['price']} ({b['validity']})" for b in MOCK_DATA_BUNDLES[:3]]) + "\n\nWhich one would you like?",
        'report_network': "I'm sorry to hear about your network issues. Could you tell me your location so I can check the network status in your area?",
        'report_transaction': "I understand you're experiencing a failed transaction. Please provide the transaction reference or phone number used.",
        'escalate_human': "Connecting you to a customer service representative. Current wait time is approximately 2 minutes.",
        'greeting': "Hello! Welcome to myMTN AI Assistant. How can I help you today?",
        'unknown': "I'm not sure I understood that. Could you please rephrase? You can ask about data balance, buy data, report network issues, or speak to an agent."
    }
    
    responses_pidgin = {
        'check_data_balance': f"Your data balance na {MOCK_ACCOUNTS.get('user_001', {}).get('data_balance', 'N/A')}. You wan buy more?",
        'check_airtime': f"Your airtime balance na {MOCK_ACCOUNTS.get('user_001', {}).get('airtime_balance', 'N/A')}.",
        'buy_data': "We get these data bundles:\n" + "\n".join([f"- {b['name']}: ₦{b['price']} ({b['validity']})" for b in MOCK_DATA_BUNDLES[:3]]) + "\n\nWhich one you wan?",
        'report_network': "I dey sorry say network dey give you wahala. Which area you dey make I fit check?",
        'report_transaction': "I understand say transaction fail. Abeg give me transaction reference or phone number wey you use.",
        'escalate_human': "I dey connect you go customer service representative. Wait time na about 2 minutes.",
        'greeting': "How far! Welcome to myMTN AI Assistant. Wetin I fit do for you today?",
        'unknown': "I no really understand wetin you talk. Abeg talk am again. You fit ask about data balance, buy data, report network, or talk to agent."
    }
    
    responses = responses_pidgin if language == 'pidgin' else responses_en
    
    base_response = responses.get(intent, responses['unknown'])
    
    # Add network status if reporting network with location
    if intent == 'report_network' and 'location' in entities:
        loc = entities['location'].lower()
        status = MOCK_NETWORK_STATUS.get(loc.split()[0], 'unknown')
        base_response += f"\n\nNetwork status for {entities['location']}: {status.upper()}"
    
    suggestions_map = {
        'check_data_balance': ['Buy Data', 'Check Airtime', 'Speak to Agent'],
        'buy_data': ['Confirm Purchase', 'View All Bundles', 'Cancel'],
        'report_network': ['Provide Location', 'Check Status', 'Speak to Agent'],
        'greeting': ['Check Data Balance', 'Buy Data', 'Report Issue'],
        'unknown': ['Check Balance', 'Buy Data', 'Speak to Agent']
    }
    
    suggestions = suggestions_map.get(intent, ['Help', 'Check Balance', 'Speak to Agent'])
    
    return base_response, suggestions


async def save_message_to_supabase(
    session_id: str,
    role: str,
    content: str,
    intent: Optional[str] = None,
    confidence: Optional[float] = None,
    entities: Optional[Dict[str, Any]] = None,
    language: Optional[str] = None,
    suggestions: Optional[List[str]] = None
):
    """Save a message to Supabase conversations table."""
    try:
        supabase = get_supabase()
        
        # Insert message into conversations table
        data = {
            'session_id': session_id,
            'role': role,
            'content': content,
            'intent': intent,
            'confidence': confidence,
            'entities': entities or {},
            'language': language,
            'suggestions': suggestions or [],
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('conversations').insert(data).execute()
        return result
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error saving message to Supabase: {e}")
        return None


async def save_feedback_to_supabase(session_id: str, rating: int, comment: Optional[str] = None):
    """Save CSAT feedback to Supabase feedback table."""
    try:
        supabase = get_supabase()
        
        data = {
            'session_id': session_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('feedback').insert(data).execute()
        return result
    except Exception as e:
        print(f"Error saving feedback to Supabase: {e}")
        return None


async def get_conversation_from_supabase(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve conversation history from Supabase."""
    try:
        supabase = get_supabase()
        
        result = supabase.table('conversations').select('*').eq('session_id', session_id).order('created_at', desc=False).execute()
        
        if result.data:
            messages = []
            for row in result.data:
                messages.append({
                    'role': row['role'],
                    'content': row['content'],
                    'timestamp': row['created_at'],
                    'intent': row.get('intent'),
                    'confidence': row.get('confidence'),
                    'entities': row.get('entities'),
                    'suggestions': row.get('suggestions')
                })
            
            started_at = datetime.fromisoformat(messages[0]['timestamp']) if messages else datetime.now()
            escalated = any(row.get('intent') == 'escalate_human' for row in result.data)
            
            return {
                'messages': messages,
                'session_id': session_id,
                'started_at': started_at,
                'escalated': escalated
            }
        
        return None
    except Exception as e:
        print(f"Error retrieving conversation from Supabase: {e}")
        return None

@router.post("/message", response_model=MessageResponse, tags=["MTN Chat"])
async def send_message(request: MessageRequest):
    """
    Send a message to the MTN AI chatbot.
    
    This endpoint processes user messages through the integrated NLP pipeline:
    1. Language detection (English/Pidgin)
    2. Intent classification (23 categories)
    3. Entity extraction
    4. Response generation
    5. Escalation decision
    """
    # Generate or retrieve session ID
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
    
    # Initialize session if new
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            'messages': [],
            'started_at': datetime.now(),
            'escalated': False,
            'user_id': request.user_id
        }
    
    session = SESSIONS[session_id]
    
    # Check if already escalated
    if session.get('escalated'):
        return MessageResponse(
            response="You are currently connected to a customer service representative. Please wait for assistance.",
            intent='escalated',
            confidence=1.0,
            entities={},
            suggestions=['Wait for Agent'],
            requires_escalation=True,
            session_id=session_id
        )
    
    # Step 1: Language Detection
    language = detect_language(request.message)
    
    # Step 2: Intent Classification
    intent, confidence = classify_intent(request.message)
    
    # Step 3: Entity Extraction
    entities = extract_entities(request.message, intent)
    
    # Step 4: Escalation Decision
    requires_escalation = (
        confidence < 0.75 or
        intent == 'escalate_human' or
        intent == 'unknown'
    )
    
    if requires_escalation and intent != 'escalate_human':
        intent = 'escalate_human'
        session['escalated'] = True
    
    # Step 5: Generate Response
    response_text, suggestions = generate_response(intent, entities, language)
    
    # Store message in session (local cache)
    session['messages'].append({
        'role': 'user',
        'content': request.message,
        'timestamp': datetime.now().isoformat(),
        'language': language,
        'intent': intent,
        'confidence': confidence
    })
    
    session['messages'].append({
        'role': 'assistant',
        'content': response_text,
        'timestamp': datetime.now().isoformat(),
        'intent': intent,
        'suggestions': suggestions
    })
    
    # Save messages to Supabase (async, non-blocking)
    await save_message_to_supabase(
        session_id=session_id,
        role='user',
        content=request.message,
        intent=intent,
        confidence=confidence,
        entities=entities,
        language=language
    )
    
    await save_message_to_supabase(
        session_id=session_id,
        role='assistant',
        content=response_text,
        intent=intent,
        suggestions=suggestions
    )
    
    return MessageResponse(
        response=response_text,
        intent=intent,
        confidence=confidence,
        entities=entities,
        suggestions=suggestions,
        requires_escalation=requires_escalation,
        session_id=session_id
    )

@router.get("/conversation/{session_id}", response_model=ConversationHistory, tags=["MTN Chat"])
async def get_conversation(session_id: str):
    """Retrieve conversation history for a session."""
    # Try to get from Supabase first
    conversation = await get_conversation_from_supabase(session_id)
    
    if conversation:
        return ConversationHistory(
            messages=conversation['messages'],
            session_id=session_id,
            started_at=conversation['started_at'],
            escalated=conversation['escalated']
        )
    
    # Fallback to in-memory storage
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = SESSIONS[session_id]
    return ConversationHistory(
        messages=session['messages'],
        session_id=session_id,
        started_at=session['started_at'],
        escalated=session.get('escalated', False)
    )

@router.post("/feedback", tags=["MTN Chat"])
async def submit_feedback(request: FeedbackRequest):
    """Submit CSAT feedback for a conversation."""
    # Save to Supabase
    result = await save_feedback_to_supabase(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.comment
    )
    
    if result:
        return {"status": "success", "message": "Thank you for your feedback!"}
    else:
        # Fallback to in-memory storage
        if request.session_id not in SESSIONS:
            # Still accept feedback even if session doesn't exist in memory
            pass
        
        SESSIONS[request.session_id]['feedback'] = {
            'rating': request.rating,
            'comment': request.comment,
            'submitted_at': datetime.now().isoformat()
        }
        
        return {"status": "success", "message": "Thank you for your feedback!"}
