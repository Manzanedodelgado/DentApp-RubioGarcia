from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
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