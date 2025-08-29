from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from emergentintegrations.llm.chat import LlmChat, UserMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ContactStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"

class MessageChannel(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    INTERNAL = "internal"

# Models
class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: ContactStatus = ContactStatus.ACTIVE
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ContactStatus] = None
    notes: Optional[str] = None

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    contact_name: str
    title: str
    description: Optional[str] = None
    date: datetime
    duration_minutes: int = 60
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reminder_sent: bool = False
    # Extended fields from Google Sheets import
    patient_number: Optional[str] = None
    phone: Optional[str] = None
    doctor: Optional[str] = None
    treatment: Optional[str] = None
    time: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppointmentCreate(BaseModel):
    contact_id: str
    title: str
    description: Optional[str] = None
    date: datetime
    duration_minutes: int = 60

class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    contact_name: str
    channel: MessageChannel
    content: str
    is_from_contact: bool = False
    status: MessageStatus = MessageStatus.SENT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None

class MessageCreate(BaseModel):
    contact_id: str
    channel: MessageChannel
    content: str
    is_from_contact: bool = False

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    content: str
    channel: MessageChannel
    variables: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TemplateCreate(BaseModel):
    name: str
    content: str
    channel: MessageChannel
    variables: List[str] = Field(default_factory=list)

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    template_id: str
    channel: MessageChannel
    target_tags: List[str] = Field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    sent_count: int = 0
    total_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CampaignCreate(BaseModel):
    name: str
    template_id: str
    channel: MessageChannel
    target_tags: List[str] = Field(default_factory=list)
    scheduled_at: Optional[datetime] = None

# AI Training Models
class AITraining(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    practice_name: str = "RUBIO GARCÍA DENTAL"
    system_prompt: str
    specialties: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    working_hours: str = "Lunes a Viernes 9:00-18:00"
    emergency_contact: str = ""
    appointment_instructions: str = ""
    policies: str = ""
    personality: str = "profesional y amigable"
    language: str = "español"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AITrainingCreate(BaseModel):
    practice_name: str = "RUBIO GARCÍA DENTAL"
    system_prompt: str
    specialties: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    working_hours: str = "Lunes a Viernes 9:00-18:00"
    emergency_contact: str = ""
    appointment_instructions: str = ""
    policies: str = ""
    personality: str = "profesional y amigable"
    language: str = "español"

class AITrainingUpdate(BaseModel):
    practice_name: Optional[str] = None
    system_prompt: Optional[str] = None
    specialties: Optional[List[str]] = None
    services: Optional[List[str]] = None
    working_hours: Optional[str] = None
    emergency_contact: Optional[str] = None
    appointment_instructions: Optional[str] = None
    policies: Optional[str] = None
    personality: Optional[str] = None
    language: Optional[str] = None

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    contact_name: str
    contact_phone: str
    messages: List[dict] = Field(default_factory=list)
    is_active: bool = True
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    content: str
    is_from_patient: bool = True

class AIResponse(BaseModel):
    response: str
    should_schedule_appointment: bool = False
    extracted_info: dict = Field(default_factory=dict)

class DashboardStats(BaseModel):
    total_contacts: int
    active_contacts: int
    total_appointments: int
    today_appointments: int
    pending_messages: int
    active_campaigns: int
    ai_conversations: int
    whatsapp_connected: bool = False

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith(('_at', 'date')):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

# AI Chat Helper
async def get_ai_response(message: str, contact_id: str, training_config: dict) -> AIResponse:
    try:
        # Get AI training configuration
        ai_key = os.environ.get('EMERGENT_LLM_KEY')
        if not ai_key:
            return AIResponse(response="Lo siento, el sistema de IA no está configurado correctamente.")
        
        # Create system prompt based on training
        system_prompt = f"""
Eres un asistente virtual de {training_config.get('practice_name', 'RUBIO GARCÍA DENTAL')}.

INFORMACIÓN DE LA CLÍNICA:
- Especialidades: {', '.join(training_config.get('specialties', ['Implantología', 'Estética dental']))}
- Servicios: {', '.join(training_config.get('services', ['Consultas generales', 'Limpiezas', 'Implantes']))}
- Horarios: {training_config.get('working_hours', 'Lunes a Viernes 9:00-18:00')}
- Emergencias: {training_config.get('emergency_contact', 'Para emergencias llame al teléfono principal')}

INSTRUCCIONES PARA CITAS:
{training_config.get('appointment_instructions', 'Para agendar citas, proporcione su nombre, teléfono y preferencia de horario.')}

POLÍTICAS:
{training_config.get('policies', 'Recordamos confirmar las citas 24 horas antes.')}

PERSONALIDAD: {training_config.get('personality', 'profesional y amigable')}
IDIOMA: {training_config.get('language', 'español')}

Responde de manera {training_config.get('personality', 'profesional y amigable')} en {training_config.get('language', 'español')}. 
Si el paciente quiere agendar una cita, solicita todos los datos necesarios y confirma la disponibilidad.
Mantén las respuestas concisas pero completas.
"""
        
        # Initialize LLM chat
        chat = LlmChat(
            api_key=ai_key,
            session_id=f"dental_chat_{contact_id}",
            system_message=system_prompt
        ).with_model("openai", "gpt-4o-mini")
        
        # Send message to AI
        user_message = UserMessage(text=message)
        ai_response = await chat.send_message(user_message)
        
        # Check if appointment scheduling is needed
        appointment_keywords = ["cita", "agendar", "reservar", "turno", "consulta", "appointment"]
        should_schedule = any(keyword in message.lower() for keyword in appointment_keywords)
        
        return AIResponse(
            response=ai_response,
            should_schedule_appointment=should_schedule,
            extracted_info={}
        )
        
    except Exception as e:
        logging.error(f"AI response error: {str(e)}")
        return AIResponse(response="Lo siento, no pude procesar tu mensaje en este momento. Por favor intenta más tarde.")

# Contact Routes
@api_router.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactCreate):
    contact_dict = contact.dict()
    contact_obj = Contact(**contact_dict)
    contact_data = prepare_for_mongo(contact_obj.dict())
    await db.contacts.insert_one(contact_data)
    return contact_obj

@api_router.get("/contacts", response_model=List[Contact])
async def get_contacts(status: Optional[ContactStatus] = None, tag: Optional[str] = None):
    filter_query = {}
    if status:
        filter_query["status"] = status
    if tag:
        filter_query["tags"] = {"$in": [tag]}
    
    contacts = await db.contacts.find(filter_query).to_list(1000)
    return [Contact(**parse_from_mongo(contact)) for contact in contacts]

@api_router.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: str):
    contact = await db.contacts.find_one({"id": contact_id})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Contact(**parse_from_mongo(contact))

@api_router.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: str, updates: ContactUpdate):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data = prepare_for_mongo(update_data)
    
    result = await db.contacts.update_one(
        {"id": contact_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    updated_contact = await db.contacts.find_one({"id": contact_id})
    return Contact(**parse_from_mongo(updated_contact))

@api_router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    result = await db.contacts.delete_one({"id": contact_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

# Appointment Routes
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate):
    # Get contact info
    contact = await db.contacts.find_one({"id": appointment.contact_id})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    appointment_dict = appointment.dict()
    appointment_dict["contact_name"] = contact["name"]
    appointment_obj = Appointment(**appointment_dict)
    appointment_data = prepare_for_mongo(appointment_obj.dict())
    await db.appointments.insert_one(appointment_data)
    return appointment_obj

@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[AppointmentStatus] = None
):
    filter_query = {}
    if status:
        filter_query["status"] = status
    
    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to
        filter_query["date"] = date_filter
    
    appointments = await db.appointments.find(filter_query).sort("date", 1).to_list(1000)
    return [Appointment(**parse_from_mongo(appointment)) for appointment in appointments]

@api_router.get("/appointments/by-date")
async def get_appointments_by_date(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    """Get appointments for a specific date"""
    try:
        # Parse the date
        target_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Query appointments for the date
        filter_query = {
            "date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            }
        }
        
        appointments = await db.appointments.find(filter_query).sort("date", 1).to_list(1000)
        return [Appointment(**parse_from_mongo(appointment)) for appointment in appointments]
    except Exception as e:
        logger.error(f"Error fetching appointments by date: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching appointments")

@api_router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return Appointment(**parse_from_mongo(appointment))

@api_router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, updates: AppointmentUpdate):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data = prepare_for_mongo(update_data)
    
    result = await db.appointments.update_one(
        {"id": appointment_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    updated_appointment = await db.appointments.find_one({"id": appointment_id})
    return Appointment(**parse_from_mongo(updated_appointment))

# Message Routes
@api_router.post("/messages", response_model=Message)
async def create_message(message: MessageCreate):
    # Get contact info
    contact = await db.contacts.find_one({"id": message.contact_id})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    message_dict = message.dict()
    message_dict["contact_name"] = contact["name"]
    message_obj = Message(**message_dict)
    message_data = prepare_for_mongo(message_obj.dict())
    await db.messages.insert_one(message_data)
    return message_obj

@api_router.get("/messages", response_model=List[Message])
async def get_messages(contact_id: Optional[str] = None, channel: Optional[MessageChannel] = None):
    filter_query = {}
    if contact_id:
        filter_query["contact_id"] = contact_id
    if channel:
        filter_query["channel"] = channel
    
    messages = await db.messages.find(filter_query).sort("created_at", -1).to_list(1000)
    return [Message(**parse_from_mongo(message)) for message in messages]

# Template Routes
@api_router.post("/templates", response_model=Template)
async def create_template(template: TemplateCreate):
    template_obj = Template(**template.dict())
    template_data = prepare_for_mongo(template_obj.dict())
    await db.templates.insert_one(template_data)
    return template_obj

@api_router.get("/templates", response_model=List[Template])
async def get_templates(channel: Optional[MessageChannel] = None):
    filter_query = {}
    if channel:
        filter_query["channel"] = channel
    
    templates = await db.templates.find(filter_query).to_list(1000)
    return [Template(**parse_from_mongo(template)) for template in templates]

# Campaign Routes
@api_router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    # Calculate total count based on target tags
    filter_query = {}
    if campaign.target_tags:
        filter_query["tags"] = {"$in": campaign.target_tags}
    
    total_count = await db.contacts.count_documents(filter_query)
    
    campaign_dict = campaign.dict()
    campaign_dict["total_count"] = total_count
    campaign_obj = Campaign(**campaign_dict)
    campaign_data = prepare_for_mongo(campaign_obj.dict())
    await db.campaigns.insert_one(campaign_data)
    return campaign_obj

@api_router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns():
    campaigns = await db.campaigns.find().sort("created_at", -1).to_list(1000)
    return [Campaign(**parse_from_mongo(campaign)) for campaign in campaigns]

# AI Training Routes
@api_router.post("/ai/training", response_model=AITraining)
async def create_ai_training(training: AITrainingCreate):
    # Delete existing training (only one config allowed)
    await db.ai_training.delete_many({})
    
    training_obj = AITraining(**training.dict())
    training_data = prepare_for_mongo(training_obj.dict())
    await db.ai_training.insert_one(training_data)
    return training_obj

@api_router.get("/ai/training", response_model=Optional[AITraining])
async def get_ai_training():
    training = await db.ai_training.find_one()
    if not training:
        return None
    return AITraining(**parse_from_mongo(training))

@api_router.put("/ai/training", response_model=AITraining)
async def update_ai_training(updates: AITrainingUpdate):
    existing = await db.ai_training.find_one()
    if not existing:
        raise HTTPException(status_code=404, detail="AI training configuration not found")
    
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data = prepare_for_mongo(update_data)
    
    await db.ai_training.update_one({}, {"$set": update_data})
    updated_training = await db.ai_training.find_one()
    return AITraining(**parse_from_mongo(updated_training))

# Chat Routes
@api_router.post("/chat/sessions", response_model=ChatSession)
async def create_chat_session(contact_id: str, contact_name: str, contact_phone: str):
    # Check if active session exists
    existing = await db.chat_sessions.find_one({
        "contact_id": contact_id,
        "is_active": True
    })
    
    if existing:
        return ChatSession(**parse_from_mongo(existing))
    
    session_obj = ChatSession(
        contact_id=contact_id,
        contact_name=contact_name,
        contact_phone=contact_phone
    )
    session_data = prepare_for_mongo(session_obj.dict())
    await db.chat_sessions.insert_one(session_data)
    return session_obj

class ChatSessionCreate(BaseModel):
    contact_id: str
    contact_name: str
    contact_phone: str

@api_router.post("/chat/sessions/create", response_model=ChatSession)
async def create_chat_session_body(session_data: ChatSessionCreate):
    # Check if active session exists
    existing = await db.chat_sessions.find_one({
        "contact_id": session_data.contact_id,
        "is_active": True
    })
    
    if existing:
        return ChatSession(**parse_from_mongo(existing))
    
    session_obj = ChatSession(**session_data.dict())
    session_data_dict = prepare_for_mongo(session_obj.dict())
    await db.chat_sessions.insert_one(session_data_dict)
    return session_obj

@api_router.post("/chat/message")
async def send_chat_message(session_id: str, message: ChatMessage):
    # Get session
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Get AI training configuration
    training = await db.ai_training.find_one()
    training_config = training if training else {}
    
    # Get AI response
    ai_response = await get_ai_response(message.content, session["contact_id"], training_config)
    
    # Add messages to session
    new_messages = [
        {
            "content": message.content,
            "is_from_patient": message.is_from_patient,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "content": ai_response.response,
            "is_from_patient": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Update session
    await db.chat_sessions.update_one(
        {"id": session_id},
        {
            "$push": {"messages": {"$each": new_messages}},
            "$set": {"last_activity": datetime.now(timezone.utc)}
        }
    )
    
    return {
        "ai_response": ai_response.response,
        "should_schedule_appointment": ai_response.should_schedule_appointment,
        "extracted_info": ai_response.extracted_info
    }

@api_router.get("/chat/sessions", response_model=List[ChatSession])
async def get_chat_sessions(active_only: bool = True):
    filter_query = {"is_active": True} if active_only else {}
    sessions = await db.chat_sessions.find(filter_query).sort("last_activity", -1).to_list(1000)
    return [ChatSession(**parse_from_mongo(session)) for session in sessions]

@api_router.get("/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(session_id: str):
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return ChatSession(**parse_from_mongo(session))

# Dashboard Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    # Get all stats in parallel
    total_contacts = await db.contacts.count_documents({})
    active_contacts = await db.contacts.count_documents({"status": "active"})
    total_appointments = await db.appointments.count_documents({})
    
    # Today's appointments
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    today_appointments = await db.appointments.count_documents({
        "date": {"$gte": today_start.isoformat(), "$lte": today_end.isoformat()}
    })
    
    pending_messages = await db.messages.count_documents({
        "is_from_contact": True,
        "status": {"$ne": "read"}
    })
    
    active_campaigns = await db.campaigns.count_documents({
        "status": {"$in": ["scheduled", "sending"]}
    })
    
    ai_conversations = await db.chat_sessions.count_documents({"is_active": True})
    
    return DashboardStats(
        total_contacts=total_contacts,
        active_contacts=active_contacts,
        total_appointments=total_appointments,
        today_appointments=today_appointments,
        pending_messages=pending_messages,
        active_campaigns=active_campaigns,
        ai_conversations=ai_conversations,
        whatsapp_connected=False
    )

# Get available tags
@api_router.get("/tags")
async def get_available_tags():
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    tags = await db.contacts.aggregate(pipeline).to_list(1000)
    return [{"name": tag["_id"], "count": tag["count"]} for tag in tags]

# Authentication Models
class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

# Authentication Routes
@api_router.post("/auth/login", response_model=AuthResponse)
async def login(login_data: LoginRequest):
    """Authenticate user with username and password"""
    try:
        # Fixed credentials for admin user
        ADMIN_USERNAME = "JMD"
        ADMIN_PASSWORD = "190582"
        
        if login_data.username == ADMIN_USERNAME and login_data.password == ADMIN_PASSWORD:
            # Create session token (simple UUID for now)
            token = str(uuid.uuid4())
            
            # Store session in database
            session = {
                "id": str(uuid.uuid4()),
                "token": token,
                "username": ADMIN_USERNAME,
                "role": "admin",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                "active": True
            }
            
            await db.sessions.insert_one(session)
            
            return AuthResponse(
                success=True,
                message="Login successful",
                token=token,
                user={
                    "username": ADMIN_USERNAME,
                    "role": "admin",
                    "name": "Administrador JMD"
                }
            )
        else:
            return AuthResponse(
                success=False,
                message="Credenciales incorrectas"
            )
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during authentication")

@api_router.post("/auth/logout")
async def logout(token: str = None):
    """Logout user and invalidate session"""
    try:
        if token:
            await db.sessions.update_one(
                {"token": token},
                {"$set": {"active": False, "ended_at": datetime.now(timezone.utc).isoformat()}}
            )
        
        return {"success": True, "message": "Logout successful"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during logout")

@api_router.get("/auth/verify")
async def verify_token(token: str = None):
    """Verify if token is valid and active"""
    try:
        if not token:
            return {"valid": False, "message": "No token provided"}
        
        session = await db.sessions.find_one({
            "token": token,
            "active": True
        })
        
        if not session:
            return {"valid": False, "message": "Invalid or expired token"}
        
        # Check if session has expired
        expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_at:
            # Mark session as inactive
            await db.sessions.update_one(
                {"token": token},
                {"$set": {"active": False, "ended_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"valid": False, "message": "Token expired"}
        
        return {
            "valid": True,
            "user": {
                "username": session["username"],
                "role": session["role"],
                "name": "Administrador JMD"
            }
        }
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return {"valid": False, "message": "Error verifying token"}

# Template Management Routes
@api_router.get("/templates")
async def get_templates():
    """Get all message templates"""
    try:
        templates = await db.message_templates.find({}).to_list(100)
        
        # If no templates exist, create default ones
        if not templates:
            default_templates = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Recordatorio Cita",
                    "content": "Hola {nombre}, te recordamos tu cita el {fecha} a las {hora} con {doctor} para {tratamiento}. ¡Te esperamos!",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Confirmación Cita",
                    "content": "Estimado/a {nombre}, por favor confirma tu asistencia a la cita del {fecha} a las {hora} con {doctor}.",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Recordatorio Revisión",
                    "content": "Hola {nombre}, es momento de tu revisión anual. Contacta con nosotros para agendar tu cita.",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            await db.message_templates.insert_many(default_templates)
            return default_templates
        
        return [parse_from_mongo(template) for template in templates]
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching templates")

@api_router.post("/templates")
async def create_template(template_data: dict):
    """Create a new message template"""
    try:
        name = template_data.get("name", "").strip()
        content = template_data.get("content", "").strip()
        
        if not name or not content:
            raise HTTPException(status_code=400, detail="Name and content are required")
        
        # Check if template with same name exists
        existing = await db.message_templates.find_one({"name": name})
        if existing:
            raise HTTPException(status_code=400, detail="Template with this name already exists")
        
        new_template = {
            "id": str(uuid.uuid4()),
            "name": name,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.message_templates.insert_one(new_template)
        
        return parse_from_mongo(new_template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating template")

@api_router.put("/templates/{template_id}")
async def update_template(template_id: str, template_data: dict):
    """Update an existing message template"""
    try:
        name = template_data.get("name", "").strip()
        content = template_data.get("content", "").strip()
        
        if not name or not content:
            raise HTTPException(status_code=400, detail="Name and content are required")
        
        # Check if template exists
        template = await db.message_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if another template with same name exists
        existing = await db.message_templates.find_one({"name": name, "id": {"$ne": template_id}})
        if existing:
            raise HTTPException(status_code=400, detail="Template with this name already exists")
        
        update_data = {
            "name": name,
            "content": content,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.message_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )
        
        # Get updated template
        updated_template = await db.message_templates.find_one({"id": template_id})
        return parse_from_mongo(updated_template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating template")

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a message template"""
    try:
        # Check if template exists
        template = await db.message_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Delete template
        result = await db.message_templates.delete_one({"id": template_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting template")

@api_router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific message template"""
    try:
        template = await db.message_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return parse_from_mongo(template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching template")

# Reminder Templates Routes
@api_router.get("/reminders/templates")
async def get_reminder_templates():
    """Get available reminder templates"""
    try:
        templates = await db.reminder_templates.find({}).to_list(100)
        if not templates:
            # Default templates if none exist
            default_templates = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Recordatorio Cita",
                    "content": "Hola {nombre}, te recordamos tu cita el {fecha} a las {hora} con {doctor} para {tratamiento}. ¡Te esperamos!",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Confirmación Cita",
                    "content": "Estimado/a {nombre}, por favor confirma tu asistencia a la cita del {fecha} a las {hora} con {doctor}.",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Recordatorio Revisión",
                    "content": "Hola {nombre}, es momento de tu revisión anual. Contacta con nosotros para agendar tu cita.",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            await db.reminder_templates.insert_many(default_templates)
            return default_templates
        
        return [parse_from_mongo(template) for template in templates]
    except Exception as e:
        logger.error(f"Error fetching reminder templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching templates")

@api_router.post("/reminders/send-bulk")
async def send_bulk_appointment_reminders(reminder_data: dict):
    """Send reminders to selected appointments"""
    try:
        appointment_ids = reminder_data.get("appointment_ids", [])
        template_content = reminder_data.get("template_content", "")
        
        if not appointment_ids or not template_content:
            raise HTTPException(status_code=400, detail="appointment_ids and template_content are required")
        
        sent_count = 0
        for appointment_id in appointment_ids:
            appointment = await db.appointments.find_one({"id": appointment_id})
            if appointment and appointment.get("phone"):
                # Personalize message
                personalized_message = template_content
                personalized_message = personalized_message.replace("{nombre}", appointment.get("contact_name", ""))
                personalized_message = personalized_message.replace("{fecha}", appointment.get("date", "")[:10])
                personalized_message = personalized_message.replace("{hora}", appointment.get("time", ""))
                personalized_message = personalized_message.replace("{doctor}", appointment.get("doctor", ""))
                personalized_message = personalized_message.replace("{tratamiento}", appointment.get("treatment", ""))
                
                # Create message record
                message = {
                    "id": str(uuid.uuid4()),
                    "contact_id": appointment.get("contact_id"),
                    "message": personalized_message,
                    "type": "outbound",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "sent",
                    "ai_generated": False
                }
                
                await db.messages.insert_one(message)
                
                # Mark appointment as reminded
                await db.appointments.update_one(
                    {"id": appointment_id},
                    {"$set": {"reminder_sent": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                sent_count += 1
        
        return {"message": f"Reminders sent to {sent_count} appointments", "sent_count": sent_count}
        
    except Exception as e:
        logger.error(f"Error sending bulk reminders: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending reminders")

@api_router.post("/reminders/process-csv")
async def process_csv_reminders(csv_data: dict):
    """Process CSV data for bulk reminders"""
    try:
        records = csv_data.get("records", [])
        template_content = csv_data.get("template_content", "")
        
        if not records or not template_content:
            raise HTTPException(status_code=400, detail="records and template_content are required")
        
        processed_count = 0
        for record in records:
            if record.get("nombre") and record.get("telefono"):
                # Process CSV reminder
                personalized_message = template_content
                personalized_message = personalized_message.replace("{nombre}", record.get("nombre", ""))
                personalized_message = personalized_message.replace("{fecha}", record.get("fecha", ""))
                personalized_message = personalized_message.replace("{hora}", record.get("hora", ""))
                personalized_message = personalized_message.replace("{doctor}", record.get("doctor", ""))
                personalized_message = personalized_message.replace("{tratamiento}", record.get("tratamiento", ""))
                
                # Create message record (simulate sending)
                message = {
                    "id": str(uuid.uuid4()),
                    "contact_id": "csv_import",  # Special identifier for CSV imports
                    "phone": record.get("telefono"),
                    "message": personalized_message,
                    "type": "outbound",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "sent",
                    "ai_generated": False
                }
                
                await db.messages.insert_one(message)
                processed_count += 1
        
        return {"message": f"Processed {processed_count} CSV reminders", "processed_count": processed_count}
        
    except Exception as e:
        logger.error(f"Error processing CSV reminders: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing CSV reminders")

# Communication Routes
@api_router.post("/communications/send-message")
async def send_message(message_data: dict):
    """Send message to patient (placeholder for WhatsApp integration)"""
    try:
        # Create message record
        message = {
            "id": str(uuid.uuid4()),
            "contact_id": message_data.get("contact_id"),
            "message": message_data.get("message"),
            "type": "outbound",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
            "ai_generated": False
        }
        
        # Store message (you would integrate with WhatsApp API here)
        await db.messages.insert_one(message)
        
        return {"message": "Message sent successfully", "message_id": message["id"]}
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending message")

@api_router.post("/communications/bulk-reminders")
async def send_bulk_reminders(reminder_data: dict):
    """Send bulk appointment reminders"""
    try:
        template = reminder_data.get("template", "")
        target_date = reminder_data.get("target_date", "")
        
        if not template or not target_date:
            raise HTTPException(status_code=400, detail="Template and target_date are required")
        
        # Get appointments for target date
        target_datetime = datetime.fromisoformat(target_date).replace(tzinfo=timezone.utc)
        start_of_day = target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        filter_query = {
            "date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            }
        }
        
        appointments = await db.appointments.find(filter_query).to_list(1000)
        
        sent_count = 0
        for appointment in appointments:
            if appointment.get("phone"):
                # Personalize message
                personalized_message = template.replace("{nombre}", appointment.get("contact_name", ""))
                personalized_message = personalized_message.replace("{fecha}", target_date)
                personalized_message = personalized_message.replace("{hora}", appointment.get("time", ""))
                personalized_message = personalized_message.replace("{doctor}", appointment.get("doctor", ""))
                personalized_message = personalized_message.replace("{tratamiento}", appointment.get("treatment", ""))
                
                # Create message record
                message = {
                    "id": str(uuid.uuid4()),
                    "contact_id": appointment.get("contact_id"),
                    "message": personalized_message,
                    "type": "outbound",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "sent",
                    "ai_generated": False
                }
                
                await db.messages.insert_one(message)
                sent_count += 1
        
        return {"message": f"Bulk reminders sent to {sent_count} patients"}
        
    except Exception as e:
        logger.error(f"Error sending bulk reminders: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending bulk reminders")

@api_router.get("/communications/messages/{contact_id}")
async def get_contact_messages(contact_id: str):
    """Get message history for a specific contact"""
    try:
        messages = await db.messages.find(
            {"contact_id": contact_id}
        ).sort("timestamp", 1).to_list(100)
        
        return [parse_from_mongo(message) for message in messages]
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching messages")

@api_router.get("/communications/patient-history/{contact_id}")
async def get_patient_history(contact_id: str):
    """Get appointment history for a patient"""
    try:
        appointments = await db.appointments.find(
            {"contact_id": contact_id}
        ).sort("date", -1).to_list(20)  # Last 20 appointments
        
        return [Appointment(**parse_from_mongo(appointment)) for appointment in appointments]
    except Exception as e:
        logger.error(f"Error fetching patient history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching patient history")

# Appointment Sync Routes
@api_router.post("/appointments/sync")
async def sync_appointments():
    """Manually trigger appointment synchronization"""
    try:
        from import_data import import_appointments
        await import_appointments()
        return {"message": "Appointments synchronized successfully"}
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Scheduler for automatic sync
scheduler = None

async def sync_job():
    """Background job to sync appointments every 5 minutes"""
    try:
        from import_data import import_appointments
        await import_appointments()
        logger.info("✅ Automatic appointment sync completed")
    except Exception as e:
        logger.error(f"❌ Automatic sync failed: {str(e)}")

def start_scheduler():
    """Start the appointment sync scheduler"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            sync_job,
            trigger=IntervalTrigger(minutes=5),
            id='appointment_sync',
            replace_existing=True
        )
        scheduler.start()
        logger.info("🚀 Appointment sync scheduler started (every 5 minutes)")

def stop_scheduler():
    """Stop the appointment sync scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("⏹️ Appointment sync scheduler stopped")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_db_client():
    stop_scheduler()
    client.close()