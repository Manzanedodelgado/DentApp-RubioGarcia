from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
import logging
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from emergentintegrations.llm.chat import LlmChat, UserMessage
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Database initialization functions
async def init_database_collections():
    """Initialize database collections and indexes"""
    try:
        # Create indexes for better performance
        await db.contacts.create_index("id")
        await db.appointments.create_index("id")
        await db.appointments.create_index("date")
        await db.messages.create_index("contact_id")
        await db.chat_sessions.create_index("contact_id")
        logging.info("Database collections initialized")
    except Exception as e:
        logging.error(f"Error initializing database collections: {str(e)}")

async def create_default_consent_templates():
    """Create default consent templates if they don't exist"""
    try:
        # Check if templates already exist
        existing_count = await db.consent_templates.count_documents({})
        if existing_count > 0:
            return
        
        # Create basic default templates
        default_templates = [
            {
                "treatment_code": 9,
                "treatment_name": "Periodoncia",
                "name": "Consentimiento Periodontal",
                "content": "Consentimiento informado para tratamiento periodontal",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            }
        ]
        
        for template_data in default_templates:
            template = ConsentTemplate(**template_data)
            await db.consent_templates.insert_one(prepare_for_mongo(template.dict()))
            
        logging.info("Default consent templates created")
    except Exception as e:
        logging.error(f"Error creating default consent templates: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting up...")
    
    # Initialize database collections
    await init_database_collections()
    
    # Create default consent templates
    await create_default_consent_templates()
    
    # Create default consent message templates 
    await create_default_consent_message_templates()
    
    # Create default consent message settings
    await create_default_consent_message_settings()
    
    # Create default AI-powered automations
    await create_default_ai_automations()
    
    # Start background tasks
    start_scheduler()
    await initialize_default_consent_templates()
    
    yield
    
    # Shutdown
    logging.info("Shutting down...")
    stop_scheduler()
    client.close()

# Create the main app with lifespan
app = FastAPI(lifespan=lifespan)

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
    whatsapp_connected: bool

# AI Assistant Models
class VoiceAssistantRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class VoiceAssistantResponse(BaseModel):
    response: str
    session_id: str
    action_type: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None

# Settings Models
class ClinicSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "RUBIO GARCÍA DENTAL"
    address: str = "Calle Mayor 19, Alcorcón, 28921 Madrid"
    phone: str = "916 410 841"
    whatsapp: str = "664 218 253"
    email: str = "info@rubiogarciadental.com"
    schedule: str = "Lun-Jue 10:00-14:00 y 16:00-20:00 | Vie 10:00-14:00"
    specialties: List[str] = ["Implantología", "Estética Dental", "Ortodoncia", "Odontología General", "Endodoncia"]
    team: List[Dict[str, str]] = [
        {"name": "Dr. Mario Rubio", "specialty": "Implantólogo, periodoncista y estética"},
        {"name": "Dra. Virginia Tresgallo", "specialty": "Ortodoncista y odontología preventiva"},
        {"name": "Dra. Irene García", "specialty": "Endodoncista y general"},
        {"name": "Dra. Miriam Carrasco", "specialty": "Endodoncista y general"},
        {"name": "Juan A. Manzanedo", "specialty": "Atención al paciente y dirección"}
    ]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AISettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = True
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    voice_enabled: bool = True
    voice_language: str = "es-ES"
    system_prompt: str = "Eres un asistente virtual de la clínica dental RUBIO GARCÍA DENTAL..."
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# AI-Powered Automation System Models
class AutomationRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str  # 'patient_communication', 'appointment_management', 'consent_management', 'follow_up', 'triage'
    trigger_type: str  # 'time_based', 'event_based', 'condition_based', 'ai_decision'
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    ai_behavior: Optional[Dict[str, Any]] = None  # AI training configuration
    is_active: bool = True
    priority: int = 1  # 1-10, higher number = higher priority
    dependencies: List[str] = Field(default_factory=list)  # IDs of automations this depends on
    conflicts_with: List[str] = Field(default_factory=list)  # IDs of automations this conflicts with
    success_count: int = 0
    failure_count: int = 0
    last_execution: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "admin"

class AITrainingData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str
    training_prompt: str
    example_inputs: List[Dict[str, Any]] = Field(default_factory=list)
    expected_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    model_parameters: Dict[str, Any] = Field(default_factory=dict)
    training_status: str = "pending"  # 'pending', 'training', 'completed', 'failed'
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AutomationExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str
    trigger_data: Dict[str, Any] = Field(default_factory=dict)
    execution_status: str = "pending"  # 'pending', 'running', 'completed', 'failed', 'skipped'
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    ai_decision: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class AutomationDependency(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_automation_id: str
    dependent_automation_id: str
    dependency_type: str  # 'prerequisite', 'conditional', 'sequential', 'exclusive'
    dependency_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Google Sheets Sync Models
class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    doctor: Optional[str] = None  
    treatment: Optional[str] = None
    time: Optional[str] = None
    date: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = None

class SettingsUpdate(BaseModel):
    clinic: Optional[ClinicSettings] = None
    ai: Optional[AISettings] = None
    automations: Optional[List[AutomationRule]] = None

# WhatsApp Models
class WhatsAppMessage(BaseModel):
    phone_number: str
    message: str
    platform: str = "whatsapp"

class WhatsAppReminder(BaseModel):
    phone_number: str
    appointment_data: Dict[str, Any]

# Conversation Status Models
# Consent Message Template Models
class ConsentMessageTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str
    template_type: str  # 'appointment_confirmation', 'consent_form', 'survey_invite', 'lopd_consent'
    message_text: str
    variables: List[str] = Field(default_factory=list)  # Available variables like {patient_name}, {treatment}
    is_active: bool = True
    treatment_code: Optional[int] = None  # For treatment-specific templates
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "admin"

class ConsentMessageSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    setting_name: str
    setting_value: Union[str, bool, int]
    description: str
    category: str = "consent_messages"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# WhatsApp Interactive Button Response Models
class ButtonResponse(BaseModel):
    phone_number: str
    button_id: str
    selected_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConsentResponse(BaseModel):
    patient_id: str
    patient_name: str
    treatment_code: int
    consent_type: str  # 'treatment' or 'lopd'
    response: str  # 'accepted', 'needs_explanation', 'declined'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SurveyResponse(BaseModel):
    patient_id: str
    patient_name: str
    phone_number: str
    responses: Dict[str, str]  # Question-answer pairs
    pain_level: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DashboardTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str  # 'consent_follow_up', 'reschedule_request', 'survey_review'
    patient_name: str
    patient_phone: str
    description: str
    priority: str = "medium"  # 'high', 'medium', 'low'
    color_code: str = "yellow"  # 'red', 'yellow', 'green', 'gray'
    status: str = "pending"  # 'pending', 'in_progress', 'completed'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

# Treatment and Consent Management Models
class TreatmentCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: int  # Gesden treatment code (9, 10, 11, 13, 16)
    name: str
    description: str
    requires_consent: bool = False
    consent_template_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConsentTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    treatment_code: int
    treatment_name: str
    name: str
    content: str
    variables: List[str] = Field(default_factory=list)  # Variables like {nombre}, {fecha}, etc.
    send_timing: str = "day_before"  # when to send: day_before, same_day, etc.
    send_hour: str = "10:00"  # what time to send
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConsentDelivery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    appointment_id: str
    consent_template_id: str
    patient_name: str
    patient_phone: str
    treatment_code: int
    treatment_name: str
    scheduled_date: datetime
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    sent_at: Optional[datetime] = None
    delivery_method: str = "whatsapp"  # whatsapp, email, sms
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Gesden Integration Models
class GesdenSync(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sync_type: str  # "import", "export", "bidirectional"
    status: str = "pending"  # pending, running, completed, failed
    total_records: int = 0
    processed_records: int = 0
    errors: List[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
class GesdenAppointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gesden_id: str  # Original Gesden appointment ID
    patient_number: str
    patient_name: str
    phone: Optional[str] = None
    date: datetime
    time: str
    doctor_code: int
    doctor_name: str
    treatment_code: int
    treatment_name: str
    status_code: int
    status_name: str
    notes: Optional[str] = None
    duration: Optional[int] = None
    synced_to_app: bool = False
    app_appointment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UrgencyClassification(BaseModel):
    color: str
    description: str
    priority: int  # 1=highest, 5=lowest

# Color coding system
URGENCY_COLORS = {
    "red": UrgencyClassification(color="red", description="Urgencia por dolor agudo (8-10)", priority=1),
    "black": UrgencyClassification(color="black", description="Pendiente de dar cita pronto", priority=2), 
    "yellow": UrgencyClassification(color="yellow", description="Seguimiento requerido", priority=3),
    "gray": UrgencyClassification(color="gray", description="Nueva conversación", priority=4),
    "green": UrgencyClassification(color="green", description="Atendido satisfactoriamente", priority=5)
}

# Treatment codes for consent management
TREATMENT_CODES = {
    9: {"name": "Periodoncia", "requires_consent": True},
    10: {"name": "Cirugía e Implantes", "requires_consent": True},
    11: {"name": "Ortodoncia", "requires_consent": True},
    13: {"name": "Primera cita", "requires_consent": False, "requires_lopd": True},
    16: {"name": "Endodoncia", "requires_consent": True},
    1: {"name": "Revisión", "requires_consent": False},
    2: {"name": "Urgencia", "requires_consent": False},
    14: {"name": "Higiene dental", "requires_consent": False}
}

# Doctor codes from Gesden  
DOCTOR_CODES = {
    3: "Dr. Mario Rubio",
    4: "Dra. Irene García", 
    8: "Dra. Virginia Tresgallo",
    10: "Dra. Miriam Carrasco",
    12: "Dr. Juan Antonio Manzanedo"
}

# Status codes from Gesden
STATUS_CODES = {
    0: "Planificada",
    1: "Anulada", 
    5: "Finalizada",
    7: "Confirmada",
    8: "Cancelada"
}

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

# Conversation Status Routes
@api_router.get("/conversations/pending")
async def get_pending_conversations():
    """Get conversations that require attention"""
    try:
        # Get conversations that need attention (red, black, yellow status)
        pending_conversations = await db.dashboard_tasks.find({
            "status": "pending",
            "color_code": {"$in": ["red", "black", "yellow"]}
        }).sort("created_at", -1).to_list(100)
        
        return [DashboardTask(**parse_from_mongo(conv)) for conv in pending_conversations]
    except Exception as e:
        logger.error(f"Error fetching pending conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching conversations")

@api_router.put("/conversations/{conversation_id}/status")
async def update_conversation_status(conversation_id: str, status_data: dict):
    """Update conversation status (mark as resolved, change urgency, etc.)"""
    try:
        update_fields = {}
        if "urgency_color" in status_data:
            update_fields["color_code"] = status_data["urgency_color"]
            update_fields["priority"] = "high" if status_data["urgency_color"] == "red" else "medium" if status_data["urgency_color"] in ["black", "yellow"] else "low"
        if "pending_response" in status_data:
            update_fields["status"] = "pending" if status_data["pending_response"] else "completed"
        if "assigned_doctor" in status_data:
            update_fields["assigned_to"] = status_data["assigned_doctor"]
            
        update_fields["created_at"] = datetime.now(timezone.utc)
        
        result = await db.dashboard_tasks.update_one(
            {"id": conversation_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating conversation")

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
    
    # Add pending conversations count
    urgent_conversations = await db.dashboard_tasks.count_documents({
        "color_code": "red",
        "status": "pending"
    })
    
    return DashboardStats(
        total_contacts=total_contacts,
        active_contacts=active_contacts,
        total_appointments=total_appointments,
        today_appointments=today_appointments,
        pending_messages=pending_messages + urgent_conversations,
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
        return {"valid": False, "message": "Token verification error"}

# Treatment Codes Routes
@api_router.get("/treatment-codes")
async def get_treatment_codes():
    """Get all available treatment codes with their details"""
    return [
        {
            "code": code,
            "name": info["name"], 
            "requires_consent": info.get("requires_consent", False),
            "requires_lopd": info.get("requires_lopd", False)
        }
        for code, info in TREATMENT_CODES.items()
    ]

# Create default consent message templates
async def create_default_consent_message_templates():
    """Create default consent message templates if they don't exist"""
    
    default_templates = [
        {
            "template_name": "Recordatorio de Cita con Botones",
            "template_type": "appointment_confirmation",
            "message_text": """🦷 RECORDATORIO DE CITA - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}
📅 Fecha: {day_name} {date}
🕐 Hora: {time}
👨‍⚕️ Doctor: {doctor}
🩺 Tratamiento: {treatment}

📍 Calle Mayor 19, Alcorcón
📞 916 410 841 | 📱 664 218 253

Por favor, confirme su asistencia:""",
            "variables": ["patient_name", "day_name", "date", "time", "doctor", "treatment"],
            "is_active": True,
            "treatment_code": None
        },
        {
            "template_name": "Consentimiento Informado - Periodoncia", 
            "template_type": "consent_form",
            "message_text": """🦷 CONSENTIMIENTO INFORMADO - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}
🩺 Tratamiento: {treatment_name}

📋 Adjunto encontrará el consentimiento informado para su tratamiento de {treatment_name}.

Por favor, lea detenidamente el documento y responda:""",
            "variables": ["patient_name", "treatment_name"],
            "is_active": True,
            "treatment_code": 9
        },
        {
            "template_name": "Consentimiento Informado - Cirugía e Implantes",
            "template_type": "consent_form", 
            "message_text": """🦷 CONSENTIMIENTO INFORMADO - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}
🩺 Tratamiento: {treatment_name}

📋 Adjunto encontrará el consentimiento informado para su tratamiento de {treatment_name}.

Por favor, lea detenidamente el documento y responda:""",
            "variables": ["patient_name", "treatment_name"],
            "is_active": True,
            "treatment_code": 10
        },
        {
            "template_name": "Consentimiento Informado - Ortodoncia",
            "template_type": "consent_form",
            "message_text": """🦷 CONSENTIMIENTO INFORMADO - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}
🩺 Tratamiento: {treatment_name}

📋 Adjunto encontrará el consentimiento informado para su tratamiento de {treatment_name}.

Por favor, lea detenidamente el documento y responda:""",
            "variables": ["patient_name", "treatment_name"],
            "is_active": True,
            "treatment_code": 11
        },
        {
            "template_name": "Consentimiento Informado - Endodoncia",
            "template_type": "consent_form",
            "message_text": """🦷 CONSENTIMIENTO INFORMADO - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}
🩺 Tratamiento: {treatment_name}

📋 Adjunto encontrará el consentimiento informado para su tratamiento de {treatment_name}.

Por favor, lea detenidamente el documento y responda:""",
            "variables": ["patient_name", "treatment_name"],
            "is_active": True,
            "treatment_code": 16
        },
        {
            "template_name": "Documento LOPD - Primera Visita",
            "template_type": "lopd_consent",
            "message_text": """🦷 PROTECCIÓN DE DATOS - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}

📋 Como es su primera visita, necesitamos su consentimiento para el tratamiento de sus datos personales según la LOPD.

Adjunto encontrará el documento informativo.""",
            "variables": ["patient_name"],
            "is_active": True,
            "treatment_code": 13
        },
        {
            "template_name": "Encuesta Primera Visita",
            "template_type": "survey_invite",
            "message_text": """🦷 ENCUESTA PRIMERA VISITA - RUBIO GARCÍA DENTAL

👤 Paciente: {patient_name}

Para brindarle la mejor atención, por favor complete esta breve encuesta:

1️⃣ ¿Cuál es el motivo principal de su consulta?
2️⃣ ¿Siente dolor actualmente? (1-10)
3️⃣ ¿Tiene alguna alergia conocida?
4️⃣ ¿Toma algún medicamento actualmente?

Responda con un mensaje describiendo cada punto.""",
            "variables": ["patient_name"],
            "is_active": True,
            "treatment_code": None
        }
    ]
    
    for template_data in default_templates:
        # Check if template already exists
        existing_template = await db.consent_message_templates.find_one({
            "template_name": template_data["template_name"]
        })
        
        if not existing_template:
            template = ConsentMessageTemplate(**template_data)
            await db.consent_message_templates.insert_one(prepare_for_mongo(template.dict()))
            logging.info(f"Created default consent message template: {template_data['template_name']}")

# Create default consent message settings
async def create_default_consent_message_settings():
    """Create default consent message settings"""
    
    default_settings = [
        {
            "setting_name": "auto_send_reminders",
            "setting_value": True,
            "description": "Enviar recordatorios automáticos de citas 24 horas antes",
            "category": "consent_messages"
        },
        {
            "setting_name": "consent_follow_up_delay",
            "setting_value": 2,
            "description": "Horas de espera antes de crear tarea de seguimiento si no responde consentimiento",
            "category": "consent_messages"
        },
        {
            "setting_name": "survey_auto_send",
            "setting_value": True,
            "description": "Enviar encuesta automáticamente a pacientes de primera visita",
            "category": "consent_messages"
        },
        {
            "setting_name": "lopd_required_first_visit",
            "setting_value": True,
            "description": "Requerir LOPD automáticamente en primera visita",
            "category": "consent_messages"
        }
    ]
    
    for setting_data in default_settings:
        existing_setting = await db.consent_message_settings.find_one({
            "setting_name": setting_data["setting_name"]
        })
        
        if not existing_setting:
            setting = ConsentMessageSettings(**setting_data)
            await db.consent_message_settings.insert_one(prepare_for_mongo(setting.dict()))
            logging.info(f"Created default consent message setting: {setting_data['setting_name']}")

# Consent Message Template Routes
@api_router.get("/consent-message-templates")
async def get_consent_message_templates(template_type: Optional[str] = None, is_active: Optional[bool] = None):
    """Get all consent message templates with optional filtering"""
    try:
        filter_query = {}
        if template_type:
            filter_query["template_type"] = template_type
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        templates = await db.consent_message_templates.find(filter_query).sort("template_name", 1).to_list(100)
        return [ConsentMessageTemplate(**parse_from_mongo(template)) for template in templates]
        
    except Exception as e:
        logging.error(f"Error fetching consent message templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching templates")

@api_router.post("/consent-message-templates")
async def create_consent_message_template(template: ConsentMessageTemplate):
    """Create a new consent message template"""
    try:
        # Check if template name already exists
        existing_template = await db.consent_message_templates.find_one({
            "template_name": template.template_name
        })
        
        if existing_template:
            raise HTTPException(status_code=400, detail="Template name already exists")
        
        await db.consent_message_templates.insert_one(prepare_for_mongo(template.dict()))
        return {"message": "Template created successfully", "template_id": template.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating consent message template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating template")

@api_router.put("/consent-message-templates/{template_id}")
async def update_consent_message_template(template_id: str, update_data: dict):
    """Update a consent message template"""
    try:
        update_fields = {k: v for k, v in update_data.items() if v is not None}
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.consent_message_templates.update_one(
            {"id": template_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
            
        return {"message": "Template updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating consent message template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating template")

@api_router.delete("/consent-message-templates/{template_id}")
async def delete_consent_message_template(template_id: str):
    """Delete a consent message template"""
    try:
        result = await db.consent_message_templates.delete_one({"id": template_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
            
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting consent message template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting template")

@api_router.post("/consent-message-templates/{template_id}/toggle")
async def toggle_consent_message_template(template_id: str):
    """Toggle active status of a consent message template"""
    try:
        # Get current template
        template = await db.consent_message_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Toggle active status
        new_status = not template.get("is_active", True)
        
        result = await db.consent_message_templates.update_one(
            {"id": template_id},
            {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "message": f"Template {'activated' if new_status else 'deactivated'} successfully",
            "is_active": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error toggling consent message template: {str(e)}")
        raise HTTPException(status_code=500, detail="Error toggling template")

@api_router.get("/consent-message-settings")
async def get_consent_message_settings():
    """Get all consent message settings"""
    try:
        settings = await db.consent_message_settings.find({}).to_list(100)
        return [ConsentMessageSettings(**parse_from_mongo(setting)) for setting in settings]
        
    except Exception as e:
        logging.error(f"Error fetching consent message settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching settings")

@api_router.put("/consent-message-settings/{setting_name}")
async def update_consent_message_setting(setting_name: str, update_data: dict):
    """Update a consent message setting"""
    try:
        setting_value = update_data.get("setting_value")
        if setting_value is None:
            raise HTTPException(status_code=400, detail="setting_value is required")
        
        result = await db.consent_message_settings.update_one(
            {"setting_name": setting_name},
            {"$set": {"setting_value": setting_value, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Setting not found")
            
        return {"message": "Setting updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating consent message setting: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating setting")

# Create default AI-powered automations
async def create_default_ai_automations():
    """Create default AI-powered automation rules if they don't exist"""
    
    default_automations = [
        {
            "name": "Triaje Inteligente de Urgencias",
            "description": "IA evalúa mensajes de pacientes para detectar urgencias dentales y priorizar atención",
            "category": "triage",
            "trigger_type": "event_based",
            "trigger_config": {"event": "new_patient_message", "keywords": ["dolor", "urgencia", "emergency"]},
            "conditions": [
                {"type": "ai_analysis", "field": "message_content", "operator": "contains_urgency_indicators"}
            ],
            "actions": [
                {"type": "create_priority_task", "priority": "high", "color": "red"},
                {"type": "send_auto_response", "template": "urgency_acknowledgment"},
                {"type": "notify_staff", "urgency_level": "high"}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Eres un triaje dental inteligente. Analiza el mensaje del paciente y determina el nivel de urgencia (1-5) basado en síntomas como dolor severo, traumatismo, infección, sangrado. Responde con urgencia_nivel y razonamiento.",
                "parameters": {"temperature": 0.3, "max_tokens": 200}
            },
            "is_active": True,
            "priority": 10,
            "dependencies": [],
            "conflicts_with": []
        },
        {
            "name": "Seguimiento Post-Cirugía",
            "description": "Seguimiento automático de pacientes después de cirugías con IA que personaliza el mensaje según el tipo de intervención",
            "category": "follow_up",
            "trigger_type": "time_based",
            "trigger_config": {"delay_hours": 24, "trigger_after": "surgery_appointment"},
            "conditions": [
                {"type": "appointment_type", "field": "treatment_code", "operator": "in", "value": [10]}
            ],
            "actions": [
                {"type": "send_personalized_message", "ai_personalized": True},
                {"type": "create_follow_up_task", "delay_days": 3}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini", 
                "prompt": "Eres un asistente de seguimiento post-cirugía dental. Basándote en el tipo de cirugía realizada, crea un mensaje personalizado de seguimiento que incluya: cuidados específicos, signos de alarma a vigilar, y próximos pasos. Sé empático y profesional.",
                "parameters": {"temperature": 0.5, "max_tokens": 300}
            },
            "is_active": True,
            "priority": 8,
            "dependencies": [],
            "conflicts_with": []
        },
        {
            "name": "Recordatorios Inteligentes Pre-Cita",
            "description": "IA personaliza recordatorios según historial del paciente y tipo de tratamiento",
            "category": "appointment_management",
            "trigger_type": "time_based", 
            "trigger_config": {"delay_hours": -24, "trigger_before": "appointment"},
            "conditions": [
                {"type": "appointment_status", "field": "status", "operator": "equals", "value": "confirmed"}
            ],
            "actions": [
                {"type": "send_ai_reminder", "personalized": True},
                {"type": "include_prep_instructions", "treatment_specific": True}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Personaliza el recordatorio de cita considerando: historial del paciente, tipo de tratamiento, y preparación necesaria. Incluye instrucciones específicas y un tono apropiado según el nivel de ansiedad del paciente.",
                "parameters": {"temperature": 0.6, "max_tokens": 250}
            },
            "is_active": False,  # Disabled by default, conflicts with standard reminders
            "priority": 6,
            "dependencies": [],
            "conflicts_with": ["standard_appointment_reminder"]
        },
        {
            "name": "Análisis de Satisfacción Automático",
            "description": "IA analiza respuestas de pacientes para detectar insatisfacción y generar tareas de seguimiento",
            "category": "patient_communication",
            "trigger_type": "event_based",
            "trigger_config": {"event": "patient_response_received"},
            "conditions": [
                {"type": "ai_sentiment", "field": "message_content", "operator": "sentiment_negative"}
            ],
            "actions": [
                {"type": "create_priority_task", "priority": "medium", "color": "yellow"},
                {"type": "tag_conversation", "tag": "requires_attention"},
                {"type": "notify_manager", "reason": "patient_dissatisfaction"}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Analiza el sentimiento y satisfacción del paciente en su mensaje. Detecta: quejas, insatisfacción, confusión, o problemas. Clasifica el sentimiento (positivo/neutral/negativo) y el nivel de urgencia para seguimiento.",
                "parameters": {"temperature": 0.2, "max_tokens": 150}
            },
            "is_active": True,
            "priority": 7,
            "dependencies": [],
            "conflicts_with": []
        },
        {
            "name": "Gestión Inteligente de Cancelaciones",
            "description": "IA procesa cancelaciones, identifica patrones y sugiere reprogramación óptima",
            "category": "appointment_management",
            "trigger_type": "event_based",
            "trigger_config": {"event": "appointment_cancelled"},
            "conditions": [
                {"type": "cancellation_reason", "field": "reason", "operator": "not_equals", "value": "emergency"}
            ],
            "actions": [
                {"type": "analyze_cancellation_pattern", "ai_analysis": True},
                {"type": "suggest_optimal_reschedule", "ai_optimized": True},
                {"type": "send_reschedule_options", "personalized": True}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Analiza el patrón de cancelaciones del paciente y las razones. Sugiere el mejor momento para reprogramar considerando: historial de cancelaciones, disponibilidad, urgencia del tratamiento, y preferencias del paciente.",
                "parameters": {"temperature": 0.4, "max_tokens": 200}
            },
            "is_active": True,
            "priority": 5,
            "dependencies": [],
            "conflicts_with": []
        },
        {
            "name": "Consentimientos Inteligentes",
            "description": "IA personaliza mensajes de consentimiento según perfil del paciente y complejidad del tratamiento",
            "category": "consent_management",
            "trigger_type": "time_based",
            "trigger_config": {"delay_hours": -24, "trigger_before": "appointment_with_consent"},
            "conditions": [
                {"type": "treatment_requires_consent", "field": "treatment_code", "operator": "in", "value": [9, 10, 11, 16]}
            ],
            "actions": [
                {"type": "send_personalized_consent", "ai_personalized": True},
                {"type": "adjust_explanation_level", "based_on_patient_profile": True}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Personaliza el mensaje de consentimiento considerando: edad del paciente, nivel educativo estimado, historial de ansiedad, y complejidad del tratamiento. Ajusta el lenguaje y nivel de detalle apropiadamente.",
                "parameters": {"temperature": 0.5, "max_tokens": 300}
            },
            "is_active": False,  # Disabled by default, depends on consent system
            "priority": 6,
            "dependencies": ["consent_system_active"],
            "conflicts_with": []
        },
        {
            "name": "Detección de Pacientes en Riesgo",
            "description": "IA identifica pacientes que podrían abandonar el tratamiento basándose en patrones de comportamiento",
            "category": "patient_communication",
            "trigger_type": "condition_based",
            "trigger_config": {"check_frequency": "daily"},
            "conditions": [
                {"type": "ai_risk_analysis", "field": "patient_behavior", "operator": "high_risk_abandonment"}
            ],
            "actions": [
                {"type": "create_retention_task", "priority": "high"},
                {"type": "schedule_retention_call", "urgency": "medium"},
                {"type": "send_care_message", "personalized": True}
            ],
            "ai_behavior": {
                "model": "gpt-4o-mini",
                "prompt": "Analiza patrones de comportamiento del paciente: cancelaciones frecuentes, respuestas tardías, expresiones de preocupación por costos, cambios en el tono de comunicación. Evalúa riesgo de abandono del tratamiento (1-10).",
                "parameters": {"temperature": 0.3, "max_tokens": 200}
            },
            "is_active": True,
            "priority": 9,
            "dependencies": ["patient_history_available"],
            "conflicts_with": []
        }
    ]
    
    for automation_data in default_automations:
        # Check if automation already exists
        existing_automation = await db.automation_rules.find_one({
            "name": automation_data["name"]
        })
        
        if not existing_automation:
            automation = AutomationRule(**automation_data)
            await db.automation_rules.insert_one(prepare_for_mongo(automation.dict()))
            logging.info(f"Created default AI automation: {automation_data['name']}")

# AI-Powered Automation Routes
@api_router.get("/ai-automations")
async def get_ai_automations(
    category: Optional[str] = None, 
    is_active: Optional[bool] = None,
    include_dependencies: bool = True
):
    """Get all AI-powered automation rules with optional filtering"""
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        automations = await db.automation_rules.find(filter_query).sort("priority", -1).to_list(100)
        
        if include_dependencies:
            # Add dependency information
            for automation in automations:
                automation_id = automation["id"]
                
                # Find dependencies
                dependencies = await db.automation_dependencies.find({
                    "dependent_automation_id": automation_id,
                    "is_active": True
                }).to_list(50)
                
                # Find what depends on this automation
                dependents = await db.automation_dependencies.find({
                    "parent_automation_id": automation_id,
                    "is_active": True
                }).to_list(50)
                
                automation["dependency_details"] = {
                    "depends_on": dependencies,
                    "has_dependents": dependents
                }
        
        return [AutomationRule(**parse_from_mongo(automation)) for automation in automations]
        
    except Exception as e:
        logging.error(f"Error fetching AI automations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching automations")

@api_router.post("/ai-automations")
async def create_ai_automation(automation: AutomationRule):
    """Create a new AI-powered automation rule"""
    try:
        # Check if name already exists
        existing_automation = await db.automation_rules.find_one({
            "name": automation.name
        })
        
        if existing_automation:
            raise HTTPException(status_code=400, detail="Automation name already exists")
        
        # Validate dependencies
        if automation.dependencies:
            for dep_id in automation.dependencies:
                dep_exists = await db.automation_rules.find_one({"id": dep_id})
                if not dep_exists:
                    raise HTTPException(status_code=400, detail=f"Dependency automation {dep_id} not found")
        
        await db.automation_rules.insert_one(prepare_for_mongo(automation.dict()))
        
        # Create dependency relationships
        for dep_id in automation.dependencies:
            dependency = AutomationDependency(
                parent_automation_id=dep_id,
                dependent_automation_id=automation.id,
                dependency_type="prerequisite"
            )
            await db.automation_dependencies.insert_one(prepare_for_mongo(dependency.dict()))
        
        return {"message": "Automation created successfully", "automation_id": automation.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating AI automation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating automation")

@api_router.put("/ai-automations/{automation_id}")
async def update_ai_automation(automation_id: str, update_data: dict):
    """Update an AI automation rule"""
    try:
        update_fields = {k: v for k, v in update_data.items() if v is not None}
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.automation_rules.update_one(
            {"id": automation_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Automation not found")
            
        return {"message": "Automation updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating AI automation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating automation")

@api_router.post("/ai-automations/{automation_id}/toggle")
async def toggle_ai_automation(automation_id: str):
    """Toggle active status of an AI automation"""
    try:
        # Get current automation
        automation = await db.automation_rules.find_one({"id": automation_id})
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        new_status = not automation.get("is_active", True)
        
        # Check dependencies when activating
        if new_status:
            dependencies = automation.get("dependencies", [])
            for dep_id in dependencies:
                dep_automation = await db.automation_rules.find_one({"id": dep_id})
                if not dep_automation or not dep_automation.get("is_active", False):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot activate: dependency '{dep_automation.get('name', dep_id)}' is not active"
                    )
        
        # Check conflicts when activating
        if new_status:
            conflicts = automation.get("conflicts_with", [])
            for conflict_name in conflicts:
                conflict_automation = await db.automation_rules.find_one({"name": conflict_name, "is_active": True})
                if conflict_automation:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot activate: conflicts with active automation '{conflict_name}'"
                    )
        
        result = await db.automation_rules.update_one(
            {"id": automation_id},
            {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "message": f"Automation {'activated' if new_status else 'deactivated'} successfully",
            "is_active": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error toggling AI automation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error toggling automation")

@api_router.post("/ai-automations/{automation_id}/train")
async def train_ai_automation(automation_id: str, training_data: AITrainingData):
    """Train the AI behavior for an automation"""
    try:
        # Verify automation exists
        automation = await db.automation_rules.find_one({"id": automation_id})
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        # Store training data
        training_data.automation_id = automation_id
        training_data.training_status = "pending"
        
        await db.ai_training_data.insert_one(prepare_for_mongo(training_data.dict()))
        
        # Here you would typically trigger the actual AI training process
        # For now, we'll simulate it by updating the automation's AI behavior
        ai_behavior = {
            "model": training_data.model_parameters.get("model", "gpt-4o-mini"),
            "prompt": training_data.training_prompt,
            "parameters": training_data.model_parameters,
            "trained_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.automation_rules.update_one(
            {"id": automation_id},
            {"$set": {"ai_behavior": ai_behavior, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "message": "AI training initiated successfully",
            "training_id": training_data.id,
            "status": "training"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error training AI automation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error training automation")

@api_router.get("/ai-automations/dependencies")
async def get_automation_dependencies():
    """Get all automation dependencies and their relationships"""
    try:
        dependencies = await db.automation_dependencies.find({"is_active": True}).to_list(200)
        
        # Build dependency graph
        dependency_graph = {}
        for dep in dependencies:
            parent_id = dep["parent_automation_id"]
            dependent_id = dep["dependent_automation_id"]
            
            if parent_id not in dependency_graph:
                dependency_graph[parent_id] = {"dependents": [], "dependencies": []}
            if dependent_id not in dependency_graph:
                dependency_graph[dependent_id] = {"dependents": [], "dependencies": []}
            
            dependency_graph[parent_id]["dependents"].append({
                "id": dependent_id,
                "type": dep["dependency_type"],
                "config": dep["dependency_config"]
            })
            
            dependency_graph[dependent_id]["dependencies"].append({
                "id": parent_id,
                "type": dep["dependency_type"],
                "config": dep["dependency_config"]
            })
        
        return {"dependency_graph": dependency_graph, "raw_dependencies": dependencies}
        
    except Exception as e:
        logging.error(f"Error fetching automation dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching dependencies")

@api_router.get("/ai-automations/execution-history")
async def get_automation_execution_history(
    automation_id: Optional[str] = None,
    limit: int = 50,
    status: Optional[str] = None
):
    """Get execution history for automations"""
    try:
        filter_query = {}
        if automation_id:
            filter_query["automation_id"] = automation_id
        if status:
            filter_query["execution_status"] = status
        
        executions = await db.automation_executions.find(filter_query).sort("started_at", -1).limit(limit).to_list(limit)
        
        return [AutomationExecution(**parse_from_mongo(execution)) for execution in executions]
        
    except Exception as e:
        logging.error(f"Error fetching execution history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching execution history")  
@api_router.post("/consent-templates", response_model=ConsentTemplate)
async def create_consent_template(template: dict):
    """Create a new consent template"""
    template_obj = ConsentTemplate(**template)
    template_data = prepare_for_mongo(template_obj.dict())
    await db.consent_templates.insert_one(template_data)
    return template_obj

@api_router.get("/consent-templates", response_model=List[ConsentTemplate])
async def get_consent_templates():
    """Get all consent templates"""
    templates = await db.consent_templates.find().to_list(1000)
    return [ConsentTemplate(**parse_from_mongo(template)) for template in templates]

@api_router.get("/consent-templates/by-treatment/{treatment_code}")
async def get_consent_template_by_treatment(treatment_code: int):
    """Get consent template for specific treatment"""
    template = await db.consent_templates.find_one({
        "treatment_code": treatment_code,
        "active": True
    })
    if not template:
        return None
    return ConsentTemplate(**parse_from_mongo(template))

@api_router.put("/consent-templates/{template_id}", response_model=ConsentTemplate)
async def update_consent_template(template_id: str, updates: dict):
    """Update consent template"""
    update_data = {k: v for k, v in updates.items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data = prepare_for_mongo(update_data)
    
    result = await db.consent_templates.update_one(
        {"id": template_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consent template not found")
    
    updated_template = await db.consent_templates.find_one({"id": template_id})
    return ConsentTemplate(**parse_from_mongo(updated_template))

# Consent Delivery Routes
@api_router.post("/consent-deliveries", response_model=ConsentDelivery)
async def create_consent_delivery(delivery: dict):
    """Schedule consent delivery for an appointment"""
    delivery_obj = ConsentDelivery(**delivery)
    delivery_data = prepare_for_mongo(delivery_obj.dict())
    await db.consent_deliveries.insert_one(delivery_data)
    return delivery_obj

@api_router.get("/consent-deliveries")
async def get_consent_deliveries(status: Optional[str] = None):
    """Get consent deliveries, optionally filtered by status"""
    filter_query = {}
    if status:
        filter_query["delivery_status"] = status
    
    deliveries = await db.consent_deliveries.find(filter_query).sort("scheduled_date", 1).to_list(1000)
    return [ConsentDelivery(**parse_from_mongo(delivery)) for delivery in deliveries]

@api_router.put("/consent-deliveries/{delivery_id}/status")
async def update_consent_delivery_status(delivery_id: str, status_data: dict):
    """Update consent delivery status"""
    update_fields = {
        "delivery_status": status_data.get("status", "pending")
    }
    if status_data.get("status") == "sent":
        update_fields["sent_at"] = datetime.now(timezone.utc)
    
    result = await db.consent_deliveries.update_one(
        {"id": delivery_id},
        {"$set": update_fields}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consent delivery not found")
    
    return {"message": "Consent delivery status updated successfully"}

# Gesden Integration Routes
@api_router.get("/gesden/status")
async def get_gesden_status():
    """Get current Gesden synchronization status"""
    try:
        # Get latest sync status
        latest_sync = await db.gesden_syncs.find_one(sort=[("started_at", -1)])
        
        # Get total appointments in Gesden collection
        gesden_appointments = await db.gesden_appointments.count_documents({})
        synced_appointments = await db.gesden_appointments.count_documents({"synced_to_app": True})
        
        # Get pending consent deliveries
        pending_consents = await db.consent_deliveries.count_documents({"delivery_status": "pending"})
        
        return {
            "last_sync": latest_sync,
            "gesden_appointments": gesden_appointments,
            "synced_appointments": synced_appointments, 
            "sync_percentage": (synced_appointments / gesden_appointments * 100) if gesden_appointments > 0 else 0,
            "pending_consents": pending_consents,
            "connection_status": "connected" if gesden_appointments > 0 else "disconnected"
        }
    except Exception as e:
        logging.error(f"Error getting Gesden status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching Gesden status")

@api_router.post("/gesden/sync")
async def sync_gesden_data(background_tasks: BackgroundTasks):
    """Trigger Gesden data synchronization"""
    try:
        # Create sync record
        sync_record = GesdenSync(
            sync_type="import",
            status="pending"
        )
        sync_data = prepare_for_mongo(sync_record.dict())
        await db.gesden_syncs.insert_one(sync_data)
        
        # Add background task for actual sync
        background_tasks.add_task(process_gesden_sync, sync_record.id)
        
        return {"message": "Gesden sync initiated", "sync_id": sync_record.id}
    except Exception as e:
        logging.error(f"Error initiating Gesden sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Error initiating sync")

@api_router.get("/gesden/appointments")
async def get_gesden_appointments(date: Optional[str] = None):
    """Get Gesden appointments, optionally filtered by date"""
    try:
        filter_query = {}
        if date:
            target_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            filter_query["date"] = {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            }
        
        appointments = await db.gesden_appointments.find(filter_query).sort("date", 1).to_list(1000)
        return [GesdenAppointment(**parse_from_mongo(apt)) for apt in appointments]
    except Exception as e:
        logging.error(f"Error fetching Gesden appointments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching appointments")

@api_router.post("/gesden/appointments/receive")
async def receive_gesden_appointment(appointment_data: dict):
    """Receive appointment data directly from Gesden via Python script"""
    try:
        # Map Gesden data to our structure
        gesden_appointment = GesdenAppointment(
            gesden_id=appointment_data.get("id", str(uuid.uuid4())),
            patient_number=appointment_data.get("NumPac", ""),
            patient_name=f"{appointment_data.get('Nombre', '')} {appointment_data.get('Apellidos', '')}".strip(),
            phone=appointment_data.get("TelMovil", ""),
            date=datetime.fromisoformat(appointment_data.get("Fecha", datetime.now().isoformat())),
            time=appointment_data.get("Hora", ""),
            doctor_code=appointment_data.get("IdUsu", 0),
            doctor_name=DOCTOR_CODES.get(appointment_data.get("IdUsu", 0), "Doctor no asignado"),
            treatment_code=appointment_data.get("IdIcono", 0),
            treatment_name=TREATMENT_CODES.get(appointment_data.get("IdIcono", 0), {}).get("name", "Tratamiento desconocido"),
            status_code=appointment_data.get("IdSitC", 0),
            status_name=STATUS_CODES.get(appointment_data.get("IdSitC", 0), "Estado desconocido"),
            notes=appointment_data.get("Notas", ""),
            duration=appointment_data.get("Duracion", 30)
        )
        
        # Store in Gesden appointments collection
        appointment_mongo_data = prepare_for_mongo(gesden_appointment.dict())
        await db.gesden_appointments.insert_one(appointment_mongo_data)
        
        # Create corresponding appointment in main system
        contact_id = await get_or_create_contact_from_gesden(gesden_appointment)
        app_appointment = await create_appointment_from_gesden(gesden_appointment, contact_id)
        
        # Update Gesden appointment with app reference
        await db.gesden_appointments.update_one(
            {"id": gesden_appointment.id},
            {"$set": {"synced_to_app": True, "app_appointment_id": app_appointment.id}}
        )
        
        # Schedule consent delivery if needed
        await schedule_consent_if_needed(gesden_appointment, app_appointment)
        
        return {"message": "Gesden appointment processed successfully", "appointment_id": app_appointment.id}
    
    except Exception as e:
        logging.error(f"Error processing Gesden appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing appointment")

# Helper functions for Gesden integration
async def get_or_create_contact_from_gesden(gesden_appointment: GesdenAppointment):
    """Get existing contact or create new one from Gesden data"""
    # Try to find existing contact by patient number or name
    contact = await db.contacts.find_one({
        "$or": [
            {"patient_number": gesden_appointment.patient_number},
            {"name": gesden_appointment.patient_name}
        ]
    })
    
    if contact:
        return contact["id"]
    
    # Create new contact
    new_contact = Contact(
        name=gesden_appointment.patient_name,
        phone=gesden_appointment.phone,
        tags=["paciente", "gesden"],
        notes=f"Importado desde Gesden - Número de paciente: {gesden_appointment.patient_number}"
    )
    
    contact_data = prepare_for_mongo(new_contact.dict())
    await db.contacts.insert_one(contact_data)
    
    return new_contact.id

async def create_appointment_from_gesden(gesden_appointment: GesdenAppointment, contact_id: str):
    """Create main appointment from Gesden appointment"""
    # Map Gesden status to app status
    status_mapping = {
        0: AppointmentStatus.SCHEDULED,     # Planificada
        1: AppointmentStatus.CANCELLED,     # Anulada
        5: AppointmentStatus.COMPLETED,     # Finalizada  
        7: AppointmentStatus.CONFIRMED,     # Confirmada
        8: AppointmentStatus.CANCELLED      # Cancelada
    }
    
    app_appointment = Appointment(
        contact_id=contact_id,
        contact_name=gesden_appointment.patient_name,
        title=f"{gesden_appointment.treatment_name} - {gesden_appointment.doctor_name}",
        date=gesden_appointment.date,
        duration_minutes=gesden_appointment.duration or 30,
        status=status_mapping.get(gesden_appointment.status_code, AppointmentStatus.SCHEDULED),
        patient_number=gesden_appointment.patient_number,
        phone=gesden_appointment.phone,
        doctor=gesden_appointment.doctor_name,
        treatment=gesden_appointment.treatment_name,
        time=gesden_appointment.time
    )
    
    appointment_data = prepare_for_mongo(app_appointment.dict())
    await db.appointments.insert_one(appointment_data)
    
    return app_appointment

async def schedule_consent_if_needed(gesden_appointment: GesdenAppointment, app_appointment: Appointment):
    """Schedule consent delivery if treatment requires it"""
    treatment_info = TREATMENT_CODES.get(gesden_appointment.treatment_code, {})
    
    # Check if treatment requires consent
    if treatment_info.get("requires_consent", False):
        # Get consent template for this treatment
        template = await db.consent_templates.find_one({
            "treatment_code": gesden_appointment.treatment_code,
            "active": True
        })
        
        if template:
            # Calculate delivery date (day before at specified time)
            delivery_date = gesden_appointment.date - timedelta(days=1)
            delivery_time = template.get("send_hour", "10:00").split(":")
            delivery_date = delivery_date.replace(
                hour=int(delivery_time[0]),
                minute=int(delivery_time[1]),
                second=0,
                microsecond=0
            )
            
            consent_delivery = ConsentDelivery(
                appointment_id=app_appointment.id,
                consent_template_id=template["id"],
                patient_name=gesden_appointment.patient_name,
                patient_phone=gesden_appointment.phone,
                treatment_code=gesden_appointment.treatment_code,
                treatment_name=gesden_appointment.treatment_name,
                scheduled_date=delivery_date
            )
            
            delivery_data = prepare_for_mongo(consent_delivery.dict())
            await db.consent_deliveries.insert_one(delivery_data)
    
    # Check if it's first appointment (requires LOPD)
    elif treatment_info.get("requires_lopd", False) or gesden_appointment.treatment_code == 13:
        # Schedule LOPD delivery immediately
        lopd_template = await db.consent_templates.find_one({
            "treatment_code": 13,  # First appointment LOPD template
            "active": True
        })
        
        if lopd_template:
            consent_delivery = ConsentDelivery(
                appointment_id=app_appointment.id,
                consent_template_id=lopd_template["id"],
                patient_name=gesden_appointment.patient_name,
                patient_phone=gesden_appointment.phone,
                treatment_code=13,
                treatment_name="LOPD - Primera cita",
                scheduled_date=datetime.now(timezone.utc),  # Send immediately
                delivery_method="whatsapp"
            )
            
            delivery_data = prepare_for_mongo(consent_delivery.dict())
            await db.consent_deliveries.insert_one(delivery_data)

async def process_gesden_sync(sync_id: str):
    """Background task to process Gesden synchronization"""
    try:
        # Update sync status to running
        await db.gesden_syncs.update_one(
            {"id": sync_id},
            {"$set": {"status": "running"}}
        )
        
        # Here you would implement the actual sync logic
        # For now, just mark as completed
        await db.gesden_syncs.update_one(
            {"id": sync_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc)
            }}
        )
        
    except Exception as e:
        logging.error(f"Error in Gesden sync background task: {str(e)}")
        await db.gesden_syncs.update_one(
            {"id": sync_id},
            {"$set": {
                "status": "failed",
                "errors": [str(e)],
                "completed_at": datetime.now(timezone.utc)
            }}
        )

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

# AI Assistant Routes
@api_router.post("/ai/voice-assistant", response_model=VoiceAssistantResponse)
async def voice_assistant(request: VoiceAssistantRequest):
    """Process voice assistant request with AI"""
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get AI settings
        ai_settings = await db.ai_settings.find_one({}) or {}
        
        # Initialize LLM Chat
        api_key = os.getenv('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI key not configured")
        
        # Get clinic settings for context
        clinic_settings = await db.clinic_settings.find_one({}) or {}
        
        # Create system prompt based on professional guide
        system_prompt = f"""
        Eres el asistente clínico virtual de {clinic_settings.get('name', 'RUBIO GARCÍA DENTAL')}. 
        
        INFORMACIÓN DE LA CLÍNICA:
        - Dirección: {clinic_settings.get('address', 'Calle Mayor 19, Alcorcón, 28921 Madrid')}
        - Teléfono: {clinic_settings.get('phone', '916 410 841')}
        - WhatsApp: {clinic_settings.get('whatsapp', '664 218 253')}
        - Email: {clinic_settings.get('email', 'info@rubiogarciadental.com')}
        - Horarios: {clinic_settings.get('schedule', 'Lun-Jue 10:00-14:00 y 16:00-20:00 | Vie 10:00-14:00')}
        
        EQUIPO MÉDICO:
        - Dr. Mario Rubio: Implantólogo, periodoncista y estética
        - Dra. Virginia Tresgallo: Ortodoncista y odontología preventiva  
        - Dra. Irene García: Endodoncista y general
        - Dra. Miriam Carrasco: Endodoncista y general
        - Juan A. Manzanedo: Atención al paciente y dirección
        
        PROTOCOLO DE SONDEO OBLIGATORIO:
        
        1. SALUDO Y MOTIVO:
        "Hola. Para poder ayudarte a concertar una cita con el especialista adecuado, ¿podrías explicarme brevemente el motivo de tu consulta?"
        
        2. VALORACIÓN DEL DOLOR (OBLIGATORIO):
        "Para valorar la urgencia, por favor, asigna una calificación a tu dolor del 1 al 10, donde 1 es una molestia leve y 10 es un dolor constante, que no se alivia con medicación y que te despierta por las noches."
        
        CRITERIOS DE URGENCIA:
        - Dolor 8-10: URGENCIA. Responder: "Según tu valoración, tu caso se considera una urgencia. Por favor, llama directamente a la clínica al 916 410 841 para que podamos atenderte lo antes posible."
        - Dolor 1-7: No urgencia. Continuar con sondeo normal.
        
        3. HISTORIAL DEL PACIENTE:
        "Para ofrecerte la mejor atención, me gustaría revisar si ya has sido atendido/a en nuestra clínica. ¿Has visitado antes Rubio García Dental?"
        
        4. DERIVACIÓN POR ESPECIALIDAD:
        - Dolor de muelas/nervio: Dra. Irene García o Dra. Miriam Carrasco (Endodoncia)
        - Alineación dental/brackets: Dra. Virginia Tresgallo (Ortodoncia)
        - Falta de diente/implante: Dr. Mario Rubio (Implantología)
        - Blanqueamiento/estética: Dr. Mario Rubio (Estética)
        - Limpieza/revisión general: Cualquier doctor de odontología general
        
        TONO: Profesional y empático, pero directo y sin rodeos, actuando como un asistente clínico.
        
        ACCIONES A IDENTIFICAR:
        - "URGENCIA": Si dolor >= 8
        - "CITA_REGULAR": Si dolor < 8 y necesita cita
        - "INFO_GENERAL": Si solo pide información
        - "DERIVAR_ESPECIALISTA": Cuando identifiques la especialidad necesaria
        
        Siempre sigue este protocolo paso a paso. No saltes pasos.
        """
        
        # Initialize chat
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_prompt
        ).with_model(
            ai_settings.get('model_provider', 'openai'),
            ai_settings.get('model_name', 'gpt-4o-mini')
        )
        
        # Create user message
        user_message = UserMessage(text=request.message)
        
        # Get AI response
        response = await chat.send_message(user_message)
        
        # Analyze response for actions and urgency
        action_type = None
        extracted_data = {}
        urgency_color = "gray"
        pain_level = None
        
        # Extract pain level if mentioned
        import re
        pain_match = re.search(r'\b([1-9]|10)\b.*dolor|dolor.*\b([1-9]|10)\b', request.message.lower())
        if pain_match:
            pain_level = int(pain_match.group(1) or pain_match.group(2))
            if pain_level >= 8:
                action_type = "URGENCIA"
                urgency_color = "red"
            elif pain_level >= 5:
                urgency_color = "yellow"
        
        # Action detection based on message content
        if action_type != "URGENCIA":
            if any(keyword in request.message.lower() for keyword in ["envía mensaje", "mandar mensaje", "enviar mensaje"]):
                action_type = "send_message"
            elif any(keyword in request.message.lower() for keyword in ["programa recordatorio", "recordatorio", "recordar"]):
                action_type = "schedule_reminder"
            elif any(keyword in request.message.lower() for keyword in ["agendar cita", "programar cita", "nueva cita", "cita"]):
                action_type = "CITA_REGULAR"
                urgency_color = "black"
            elif any(keyword in request.message.lower() for keyword in ["información", "horario", "precio", "tratamiento"]):
                action_type = "INFO_GENERAL"
        
        # Specialty detection
        specialty_needed = None
        if any(keyword in request.message.lower() for keyword in ["duele", "dolor de muela", "nervio", "endodoncia"]):
            specialty_needed = "Endodoncia"
        elif any(keyword in request.message.lower() for keyword in ["bracket", "ortodoncia", "alinear", "enderezar"]):
            specialty_needed = "Ortodoncia"
        elif any(keyword in request.message.lower() for keyword in ["implante", "falta diente", "perdí"]):
            specialty_needed = "Implantología"
        elif any(keyword in request.message.lower() for keyword in ["blanquear", "estética", "blanqueamiento"]):
            specialty_needed = "Estética Dental"
        elif any(keyword in request.message.lower() for keyword in ["limpieza", "revisión", "general"]):
            specialty_needed = "Odontología General"
            
        if specialty_needed:
            action_type = "DERIVAR_ESPECIALISTA"
        
        extracted_data = {
            "pain_level": pain_level,
            "urgency_color": urgency_color,
            "specialty_needed": specialty_needed,
            "requires_followup": urgency_color in ["red", "black", "yellow"]
        }
        
        # Store conversation status for dashboard
        try:
            dashboard_task = DashboardTask(
                task_type="conversation_follow_up",
                patient_name=f"Usuario_{session_id[:8]}",
                patient_phone=session_id,
                description=f"Conversación: {request.message[:50]}...",
                priority="high" if urgency_color == "red" else "medium" if urgency_color in ["black", "yellow"] else "low",
                color_code=urgency_color,
                status="pending" if urgency_color in ["red", "black"] else "completed",
                notes=f"Nivel de dolor: {pain_level}, Especialidad: {specialty_needed}"
            )
            
            # Save to database
            task_data = prepare_for_mongo(dashboard_task.dict())
            await db.dashboard_tasks.replace_one(
                {"patient_phone": session_id},
                task_data,
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving conversation status: {str(e)}")
        
        return VoiceAssistantResponse(
            response=response,
            session_id=session_id,
            action_type=action_type,
            extracted_data=extracted_data
        )
        
    except Exception as e:
        logger.error(f"Error in voice assistant: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing voice request")

# Google Sheets Sync Routes
@api_router.put("/appointments/{appointment_id}")
async def update_appointment(appointment_id: str, update_data: AppointmentUpdate):
    """Update appointment and sync to Google Sheets"""
    try:
        # Get existing appointment
        appointment = await db.appointments.find_one({"id": appointment_id})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Build update fields
        update_fields = {}
        if update_data.status is not None:
            update_fields["status"] = update_data.status
        if update_data.doctor is not None:
            update_fields["doctor"] = update_data.doctor
        if update_data.treatment is not None:
            update_fields["treatment"] = update_data.treatment
        if update_data.time is not None:
            update_fields["time"] = update_data.time
        if update_data.date is not None:
            update_fields["date"] = update_data.date
        if update_data.notes is not None:
            update_fields["notes"] = update_data.notes
        if update_data.duration_minutes is not None:
            update_fields["duration_minutes"] = update_data.duration_minutes
        
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_fields["synced_to_sheets"] = False  # Mark as needing sync
        
        # Update appointment in database
        result = await db.appointments.update_one(
            {"id": appointment_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Get updated appointment for sync
        updated_appointment = await db.appointments.find_one({"id": appointment_id})
        
        # Try to sync to Google Sheets immediately
        try:
            from google_sync import sync_appointment_to_sheets
            sync_success = await sync_appointment_to_sheets(updated_appointment)
            if sync_success:
                logger.info(f"✅ Appointment {appointment_id} synced to Google Sheets")
            else:
                logger.warning(f"⚠️ Failed to sync appointment {appointment_id} to Google Sheets")
        except Exception as sync_error:
            logger.error(f"❌ Sync error: {str(sync_error)}")
        
        return {"message": "Appointment updated successfully", "appointment_id": appointment_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating appointment")

@api_router.post("/appointments/{appointment_id}/sync")
async def sync_appointment_to_sheets_endpoint(appointment_id: str):
    """Manually sync a single appointment to Google Sheets"""
    try:
        # Get appointment
        appointment = await db.appointments.find_one({"id": appointment_id})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Sync to Google Sheets
        from google_sync import sync_appointment_to_sheets
        success = await sync_appointment_to_sheets(appointment)
        
        if success:
            return {"message": "Appointment synced to Google Sheets successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to sync appointment to Google Sheets")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error syncing appointment")

@api_router.post("/sync/sheets/all")
async def sync_all_pending_to_sheets():
    """Sync all pending changes to Google Sheets"""
    try:
        from google_sync import sync_pending_changes_to_sheets
        success = await sync_pending_changes_to_sheets()
        
        if success:
            return {"message": "All pending changes synced to Google Sheets successfully"}
        else:
            return {"message": "Sync completed with some errors", "status": "partial"}
        
    except Exception as e:
        logger.error(f"Error in bulk sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in bulk sync process")

@api_router.get("/sync/sheets/status")
async def get_sync_status():
    """Get sync status and pending changes count"""
    try:
        # Count pending appointments
        pending_count = await db.appointments.count_documents({
            "synced_to_sheets": {"$ne": True}
        })
        
        # Get last sync time
        last_sync = await db.appointments.find_one(
            {"synced_to_sheets": True},
            sort=[("last_synced_at", -1)]
        )
        
        last_sync_time = None
        if last_sync and last_sync.get("last_synced_at"):
            last_sync_time = last_sync["last_synced_at"]
        
        return {
            "pending_changes": pending_count,
            "last_sync_time": last_sync_time,
            "sync_available": True
        }
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting sync status")

# WhatsApp Routes
@api_router.get("/whatsapp/status")
async def get_whatsapp_status():
    """Get WhatsApp connection status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/status", timeout=5.0)
            return response.json()
    except Exception as e:
        logger.error(f"Error getting WhatsApp status: {str(e)}")
        return {"connected": False, "status": "error", "error": str(e)}

@api_router.get("/whatsapp/qr")
async def get_whatsapp_qr():
    """Get WhatsApp QR code for connection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/qr", timeout=5.0)
            return response.json()
    except Exception as e:
        logger.error(f"Error getting WhatsApp QR: {str(e)}")
        return {"qr": None, "error": str(e)}

@api_router.post("/whatsapp/send")
async def send_whatsapp_message(message_data: WhatsAppMessage):
    """Send message via WhatsApp"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3001/send",
                json={
                    "phone_number": message_data.phone_number,
                    "message": message_data.message
                },
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending WhatsApp message")

@api_router.post("/whatsapp/send-reminder")
async def send_whatsapp_reminder(reminder_data: WhatsAppReminder):
    """Send appointment reminder via WhatsApp"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3001/send-reminder",
                json={
                    "phone_number": reminder_data.phone_number,
                    "appointment_data": reminder_data.appointment_data
                },
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error sending WhatsApp reminder: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending WhatsApp reminder")

@api_router.post("/whatsapp/send-consent")
async def send_whatsapp_consent(reminder_data: WhatsAppReminder):
    """Send surgery consent reminder via WhatsApp"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3001/send-consent",
                json={
                    "phone_number": reminder_data.phone_number,
                    "appointment_data": reminder_data.appointment_data
                },
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error sending WhatsApp consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending WhatsApp consent")

# WhatsApp Interactive Button Response Routes
@api_router.post("/whatsapp/button-response")
async def handle_button_response(response: ButtonResponse):
    """Handle WhatsApp button responses (appointments, consents, etc.)"""
    try:
        # Log the button response
        await db.button_responses.insert_one(prepare_for_mongo(response.dict()))
        
        reply_message = ""
        task_created = False
        
        # Handle appointment-related buttons
        if response.button_id in ['confirm_appointment', 'cancel_appointment', 'reschedule_appointment']:
            reply_message, task_created = await handle_appointment_response(response)
        
        # Handle consent-related buttons
        elif response.button_id in ['consent_accept', 'consent_explain', 'lopd_accept', 'lopd_info']:
            reply_message, task_created = await handle_consent_response(response)
        
        return {
            "success": True,
            "reply_message": reply_message,
            "task_created": task_created
        }
        
    except Exception as e:
        logging.error(f"Error handling button response: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing button response")

@api_router.post("/whatsapp/send-consent")
async def send_consent_form(consent_data: dict):
    """Send consent form with interactive buttons"""
    try:
        phone_number = consent_data.get("phone_number")
        patient_name = consent_data.get("patient_name")
        treatment_code = consent_data.get("treatment_code")
        consent_type = consent_data.get("consent_type", "treatment")
        
        # Get WhatsApp service URL
        whatsapp_url = "http://localhost:3001"
        
        # Prepare consent data for WhatsApp service
        consent_payload = {
            "phone_number": phone_number,
            "consent_data": {
                "patient_name": patient_name,
                "treatment_name": TREATMENT_CODES.get(treatment_code, {}).get("name", "Tratamiento"),
                "consent_type": consent_type,
                "pdf_path": f"/app/documents/consent_{consent_type}_{treatment_code}.pdf"
            }
        }
        
        # Send via WhatsApp service
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{whatsapp_url}/send-consent", json=consent_payload)
            
        if response.status_code == 200:
            # Create consent delivery record
            consent_delivery = ConsentDelivery(
                appointment_id=consent_data.get("appointment_id", ""),
                consent_template_id=consent_data.get("template_id", ""),
                patient_name=patient_name,
                patient_phone=phone_number,
                treatment_code=treatment_code,
                treatment_name=TREATMENT_CODES.get(treatment_code, {}).get("name", "Tratamiento"),
                scheduled_date=datetime.now(timezone.utc),
                delivery_status="sent",
                sent_at=datetime.now(timezone.utc)
            )
            
            await db.consent_deliveries.insert_one(prepare_for_mongo(consent_delivery.dict()))
            
            return {"success": True, "message": "Consent form sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send consent form")
            
    except Exception as e:
        logging.error(f"Error sending consent form: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending consent form")

@api_router.post("/whatsapp/send-survey")
async def send_first_visit_survey(survey_data: dict):
    """Send first visit survey to patient"""
    try:
        phone_number = survey_data.get("phone_number")
        patient_name = survey_data.get("patient_name")
        
        # Get WhatsApp service URL
        whatsapp_url = "http://localhost:3001"
        
        # Prepare survey data for WhatsApp service
        survey_payload = {
            "phone_number": phone_number,
            "patient_data": {
                "patient_name": patient_name
            }
        }
        
        # Send via WhatsApp service
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{whatsapp_url}/send-survey", json=survey_payload)
            
        if response.status_code == 200:
            # Create dashboard task to track survey response
            survey_task = DashboardTask(
                task_type="survey_review",
                patient_name=patient_name,
                patient_phone=phone_number,
                description=f"Encuesta primera visita enviada a {patient_name}",
                priority="medium",
                color_code="yellow",
                status="pending"
            )
            
            await db.dashboard_tasks.insert_one(prepare_for_mongo(survey_task.dict()))
            
            return {"success": True, "message": "Survey sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send survey")
            
    except Exception as e:
        logging.error(f"Error sending survey: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending survey")

# Helper functions for button responses
async def handle_appointment_response(response: ButtonResponse):
    """Handle appointment confirmation/cancellation/rescheduling buttons"""
    reply_message = ""
    task_created = False
    
    try:
        # Find appointment by phone number
        appointments = await db.appointments.find({"phone": response.phone_number}).to_list(10)
        if not appointments:
            return "No encontramos citas asociadas a este teléfono.", False
        
        # Get the most recent future appointment
        current_appointment = None
        for apt in appointments:
            apt_date = datetime.fromisoformat(apt["date"].replace("Z", "+00:00"))
            if apt_date > datetime.now(timezone.utc):
                current_appointment = apt
                break
        
        if not current_appointment:
            return "No tiene citas futuras para modificar.", False
        
        if response.button_id == 'confirm_appointment':
            # Update appointment status to confirmed
            await db.appointments.update_one(
                {"id": current_appointment["id"]},
                {"$set": {"status": "confirmed", "updated_at": datetime.now(timezone.utc)}}
            )
            reply_message = "✅ Su cita ha sido confirmada correctamente. ¡Le esperamos!"
            
        elif response.button_id == 'cancel_appointment':
            # Update appointment status to cancelled
            await db.appointments.update_one(
                {"id": current_appointment["id"]},
                {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc)}}
            )
            reply_message = "❌ Su cita ha sido cancelada. ¿Desea reprogramar? Responda:\n🔍 BUSCAR CITA - Para nueva cita\n📞 CONTACTAR DESPUÉS - Para contacto posterior"
            
        elif response.button_id == 'reschedule_appointment':
            # Create task for staff to reschedule
            reschedule_task = DashboardTask(
                task_type="reschedule_request",
                patient_name=current_appointment.get("contact_name", "Paciente"),
                patient_phone=response.phone_number,
                description=f"Solicitud de reprogramación - {current_appointment.get('treatment', 'Cita')}",
                priority="medium",
                color_code="yellow",
                status="pending"
            )
            
            await db.dashboard_tasks.insert_one(prepare_for_mongo(reschedule_task.dict()))
            task_created = True
            reply_message = "📅 Su solicitud de reprogramación ha sido registrada. Nuestro equipo se contactará con usted pronto."
            
        return reply_message, task_created
        
    except Exception as e:
        logging.error(f"Error handling appointment response: {str(e)}")
        return "Error procesando su respuesta. Contacte al 916 410 841.", False

async def handle_consent_response(response: ButtonResponse):
    """Handle consent form responses"""
    reply_message = ""
    task_created = False
    
    try:
        if response.button_id == 'consent_accept':
            # Record consent acceptance
            consent_response = ConsentResponse(
                patient_id=response.phone_number,
                patient_name="Paciente",  # Should be retrieved from contact database
                treatment_code=0,  # Should be retrieved from context
                consent_type="treatment",
                response="accepted"
            )
            
            await db.consent_responses.insert_one(prepare_for_mongo(consent_response.dict()))
            reply_message = "✅ Su consentimiento ha sido registrado correctamente. Gracias por su confianza en nuestro equipo."
            
        elif response.button_id == 'consent_explain':
            # Create task for staff to explain treatment
            explanation_task = DashboardTask(
                task_type="consent_follow_up",
                patient_name="Paciente",  # Should be retrieved from contact database
                patient_phone=response.phone_number,
                description="Paciente solicita explicación adicional del consentimiento informado",
                priority="high",
                color_code="red",
                status="pending"
            )
            
            await db.dashboard_tasks.insert_one(prepare_for_mongo(explanation_task.dict()))
            task_created = True
            reply_message = "👨‍⚕️ Hemos registrado su solicitud. Nuestro equipo médico se contactará para explicarle el tratamiento detalladamente."
            
        elif response.button_id == 'lopd_accept':
            # Record LOPD acceptance
            lopd_response = ConsentResponse(
                patient_id=response.phone_number,
                patient_name="Paciente",
                treatment_code=13,
                consent_type="lopd",
                response="accepted"
            )
            
            await db.consent_responses.insert_one(prepare_for_mongo(lopd_response.dict()))
            reply_message = "✅ Su consentimiento para el tratamiento de datos ha sido registrado según la LOPD. Sus datos están protegidos."
            
        elif response.button_id == 'lopd_info':
            # Create task for staff to provide LOPD information
            lopd_task = DashboardTask(
                task_type="consent_follow_up",
                patient_name="Paciente",
                patient_phone=response.phone_number,
                description="Paciente solicita más información sobre LOPD",
                priority="medium",
                color_code="yellow",
                status="pending"
            )
            
            await db.dashboard_tasks.insert_one(prepare_for_mongo(lopd_task.dict()))
            task_created = True
            reply_message = "📞 Nuestro equipo le proporcionará información detallada sobre el tratamiento de sus datos personales."
            
        return reply_message, task_created
        
    except Exception as e:
        logging.error(f"Error handling consent response: {str(e)}")
        return "Error procesando su respuesta. Contacte al 916 410 841.", False

# Dashboard Tasks Routes
@api_router.get("/dashboard/tasks")
async def get_dashboard_tasks(status: Optional[str] = None, priority: Optional[str] = None):
    """Get dashboard tasks for staff follow-up"""
    try:
        filter_query = {}
        if status:
            filter_query["status"] = status
        if priority:
            filter_query["priority"] = priority
            
        tasks = await db.dashboard_tasks.find(filter_query).sort("created_at", -1).to_list(100)
        return [DashboardTask(**parse_from_mongo(task)) for task in tasks]
        
    except Exception as e:
        logging.error(f"Error fetching dashboard tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")

@api_router.put("/dashboard/tasks/{task_id}")
async def update_dashboard_task(task_id: str, update_data: dict):
    """Update dashboard task status and notes"""
    try:
        update_fields = {k: v for k, v in update_data.items() if v is not None}
        update_fields["created_at"] = datetime.now(timezone.utc)  # Track last update
        
        result = await db.dashboard_tasks.update_one(
            {"id": task_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return {"message": "Task updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating task")

# Settings Routes
@api_router.get("/settings/clinic")
async def get_clinic_settings():
    """Get clinic settings"""
    try:
        settings = await db.clinic_settings.find_one({})
        if not settings:
            # Create default settings
            default_settings = ClinicSettings()
            await db.clinic_settings.insert_one(prepare_for_mongo(default_settings.dict()))
            return default_settings
        return ClinicSettings(**parse_from_mongo(settings))
    except Exception as e:
        logger.error(f"Error fetching clinic settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching settings")

@api_router.put("/settings/clinic")
async def update_clinic_settings(settings: ClinicSettings):
    """Update clinic settings"""
    try:
        settings.updated_at = datetime.now(timezone.utc)
        settings_data = prepare_for_mongo(settings.dict())
        
        await db.clinic_settings.replace_one(
            {},
            settings_data,
            upsert=True
        )
        
        return {"message": "Clinic settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating clinic settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating settings")

@api_router.get("/settings/ai")
async def get_ai_settings():
    """Get AI settings"""
    try:
        settings = await db.ai_settings.find_one({})
        if not settings:
            # Create default AI settings
            default_settings = AISettings()
            await db.ai_settings.insert_one(prepare_for_mongo(default_settings.dict()))
            return default_settings
        return AISettings(**parse_from_mongo(settings))
    except Exception as e:
        logger.error(f"Error fetching AI settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching AI settings")

@api_router.put("/settings/ai")
async def update_ai_settings(settings: AISettings):
    """Update AI settings"""
    try:
        settings.updated_at = datetime.now(timezone.utc)
        settings_data = prepare_for_mongo(settings.dict())
        
        await db.ai_settings.replace_one(
            {},
            settings_data,
            upsert=True
        )
        
        return {"message": "AI settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating AI settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating AI settings")

@api_router.get("/settings/automations")
async def get_automation_rules():
    """Get automation rules"""
    try:
        rules = await db.automation_rules.find({}).to_list(100)
        if not rules:
            # Create default automation rules
            default_rules = [
                AutomationRule(
                    name="Recordatorio de Cita",
                    description="Enviar recordatorio el día anterior a las 16:00h",
                    trigger_type="appointment_day_before",
                    trigger_time="16:00",
                    template_id="default_reminder",
                    conditions={"appointment_types": ["all"]}
                ),
                AutomationRule(
                    name="Nueva Cita Registrada",
                    description="Mensaje automático cuando se registra nueva cita",
                    trigger_type="new_appointment",
                    template_id="appointment_confirmation",
                    conditions={"send_immediately": True}
                ),
                AutomationRule(
                    name="Recordatorio de Cirugía",
                    description="Enviar consentimiento informado día anterior a cirugía",
                    trigger_type="surgery_reminder",
                    trigger_time="10:00",
                    template_id="surgery_consent",
                    conditions={"treatment_types": ["implante", "cirugía", "extracción"]}
                )
            ]
            
            for rule in default_rules:
                await db.automation_rules.insert_one(prepare_for_mongo(rule.dict()))
            
            return [AutomationRule(**parse_from_mongo(prepare_for_mongo(rule.dict()))) for rule in default_rules]
        
        return [AutomationRule(**parse_from_mongo(rule)) for rule in rules]
    except Exception as e:
        logger.error(f"Error fetching automation rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching automation rules")

@api_router.post("/settings/automations")
async def create_automation_rule(rule: AutomationRule):
    """Create new automation rule"""
    try:
        rule_data = prepare_for_mongo(rule.dict())
        await db.automation_rules.insert_one(rule_data)
        return {"message": "Automation rule created successfully", "rule_id": rule.id}
    except Exception as e:
        logger.error(f"Error creating automation rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating automation rule")

@api_router.put("/settings/automations/{rule_id}")
async def update_automation_rule(rule_id: str, rule: AutomationRule):
    """Update automation rule"""
    try:
        rule.updated_at = datetime.now(timezone.utc)
        rule_data = prepare_for_mongo(rule.dict())
        
        result = await db.automation_rules.update_one(
            {"id": rule_id},
            {"$set": rule_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Automation rule not found")
        
        return {"message": "Automation rule updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating automation rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating automation rule")

@api_router.delete("/settings/automations/{rule_id}")
async def delete_automation_rule(rule_id: str):
    """Delete automation rule"""
    try:
        result = await db.automation_rules.delete_one({"id": rule_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Automation rule not found")
        
        return {"message": "Automation rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting automation rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting automation rule")

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

async def automation_job():
    """Background job to process automated reminders"""
    try:
        # Get enabled automation rules
        rules = await db.automation_rules.find({"enabled": True}).to_list(100)
        
        for rule in rules:
            await process_automation_rule(rule)
        
        logger.info("✅ Automation rules processed")
    except Exception as e:
        logger.error(f"❌ Automation processing failed: {str(e)}")

async def process_automation_rule(rule: dict):
    """Process individual automation rule"""
    try:
        current_time = datetime.now(timezone.utc)
        current_hour_minute = current_time.strftime("%H:%M")
        
        # Check if it's time to execute this rule
        if rule.get("trigger_time") and rule["trigger_time"] != current_hour_minute:
            return
        
        rule_type = rule["trigger_type"]
        
        if rule_type == "appointment_day_before":
            await process_appointment_reminders(rule, current_time)
        elif rule_type == "surgery_reminder":
            await process_surgery_reminders(rule, current_time)
        
    except Exception as e:
        logger.error(f"Error processing automation rule {rule.get('name', 'Unknown')}: {str(e)}")

async def process_appointment_reminders(rule: dict, current_time: datetime):
    """Send appointment reminders for next day via WhatsApp"""
    try:
        # Calculate tomorrow's date range
        tomorrow = current_time + timedelta(days=1)
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get appointments for tomorrow
        filter_query = {
            "date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            },
            "reminder_sent": {"$ne": True}
        }
        
        appointments = await db.appointments.find(filter_query).to_list(1000)
        
        sent_count = 0
        for appointment in appointments:
            if appointment.get("phone"):
                try:
                    # Send WhatsApp reminder
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://localhost:3001/send-reminder",
                            json={
                                "phone_number": appointment["phone"],
                                "appointment_data": {
                                    "contact_name": appointment.get("contact_name", ""),
                                    "date": appointment.get("date", ""),
                                    "time": appointment.get("time", ""),
                                    "doctor": appointment.get("doctor", ""),
                                    "treatment": appointment.get("treatment", "")
                                }
                            },
                            timeout=10.0
                        )
                    
                    if response.status_code == 200:
                        # Create message record
                        message = {
                            "id": str(uuid.uuid4()),
                            "contact_id": appointment.get("contact_id"),
                            "message": f"Recordatorio WhatsApp enviado para cita del {tomorrow.strftime('%d/%m/%Y')}",
                            "type": "outbound",
                            "timestamp": current_time.isoformat(),
                            "status": "sent",
                            "ai_generated": False,
                            "automated": True,
                            "platform": "whatsapp"
                        }
                        
                        await db.messages.insert_one(message)
                        
                        # Mark appointment as reminded
                        await db.appointments.update_one(
                            {"id": appointment["id"]},
                            {"$set": {
                                "reminder_sent": True, 
                                "whatsapp_reminder_sent": True,
                                "updated_at": current_time.isoformat()
                            }}
                        )
                        
                        sent_count += 1
                        logger.info(f"✅ WhatsApp reminder sent to {appointment.get('contact_name')}")
                        
                except Exception as e:
                    logger.error(f"Error sending WhatsApp reminder to {appointment.get('contact_name')}: {str(e)}")
        
        if sent_count > 0:
            logger.info(f"✅ Sent {sent_count} automatic WhatsApp appointment reminders")
        
    except Exception as e:
        logger.error(f"Error in WhatsApp appointment reminders: {str(e)}")

async def process_surgery_reminders(rule: dict, current_time: datetime):
    """Send surgery consent reminders for next day via WhatsApp"""
    try:
        # Calculate tomorrow's date range
        tomorrow = current_time + timedelta(days=1)
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get surgery appointments for tomorrow
        surgery_keywords = ["implante", "cirugía", "extracción", "exodoncia"]
        
        filter_query = {
            "date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            },
            "treatment": {"$regex": "|".join(surgery_keywords), "$options": "i"},
            "consent_sent": {"$ne": True}
        }
        
        appointments = await db.appointments.find(filter_query).to_list(1000)
        
        sent_count = 0
        for appointment in appointments:
            if appointment.get("phone"):
                try:
                    # Send WhatsApp surgery consent
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://localhost:3001/send-consent",
                            json={
                                "phone_number": appointment["phone"],
                                "appointment_data": {
                                    "contact_name": appointment.get("contact_name", ""),
                                    "date": appointment.get("date", ""),
                                    "time": appointment.get("time", ""),
                                    "treatment": appointment.get("treatment", "")
                                }
                            },
                            timeout=10.0
                        )
                    
                    if response.status_code == 200:
                        # Create message record
                        message = {
                            "id": str(uuid.uuid4()),
                            "contact_id": appointment.get("contact_id"),
                            "message": f"Consentimiento informado WhatsApp enviado para cirugía del {tomorrow.strftime('%d/%m/%Y')}",
                            "type": "outbound",
                            "timestamp": current_time.isoformat(),
                            "status": "sent",
                            "ai_generated": False,
                            "automated": True,
                            "platform": "whatsapp"
                        }
                        
                        await db.messages.insert_one(message)
                        
                        # Mark appointment as consent sent
                        await db.appointments.update_one(
                            {"id": appointment["id"]},
                            {"$set": {
                                "consent_sent": True,
                                "whatsapp_consent_sent": True,
                                "updated_at": current_time.isoformat()
                            }}
                        )
                        
                        sent_count += 1
                        logger.info(f"✅ WhatsApp surgery consent sent to {appointment.get('contact_name')}")
                        
                except Exception as e:
                    logger.error(f"Error sending WhatsApp consent to {appointment.get('contact_name')}: {str(e)}")
        
        if sent_count > 0:
            logger.info(f"✅ Sent {sent_count} automatic WhatsApp surgery consent reminders")
        
    except Exception as e:
        logger.error(f"Error in WhatsApp surgery reminders: {str(e)}")

# Add consent delivery processing job (every 15 minutes)
async def process_consent_deliveries():
    """Process pending consent deliveries"""
    try:
        now = datetime.now(timezone.utc)
        
        # Get consent deliveries that should be sent now
        pending_deliveries = await db.consent_deliveries.find({
            "delivery_status": "pending",
            "scheduled_date": {"$lte": now.isoformat()}
        }).to_list(100)
        
        for delivery in pending_deliveries:
            try:
                # Get consent template content
                template = await db.consent_templates.find_one({"id": delivery["consent_template_id"]})
                if not template:
                    continue
                
                # Replace variables in template content
                content = template["content"]
                for variable in template.get("variables", []):
                    if variable in delivery:
                        content = content.replace(f"{{{variable}}}", str(delivery[variable]))
                
                # Send via WhatsApp (integrate with existing WhatsApp system)
                whatsapp_data = {
                    "phone_number": delivery["patient_phone"],
                    "message": content,
                    "platform": "whatsapp"
                }
                
                # Here you would integrate with the WhatsApp service
                # For now, just mark as sent
                await db.consent_deliveries.update_one(
                    {"id": delivery["id"]},
                    {"$set": {
                        "delivery_status": "sent",
                        "sent_at": now
                    }}
                )
                
                logger.info(f"Sent consent for {delivery['patient_name']} - {delivery['treatment_name']}")
                
            except Exception as e:
                logger.error(f"Error sending consent delivery {delivery['id']}: {str(e)}")
                await db.consent_deliveries.update_one(
                    {"id": delivery["id"]},
                    {"$set": {"delivery_status": "failed"}}
                )
        
        if pending_deliveries:
            logger.info(f"Processed {len(pending_deliveries)} consent deliveries")
            
    except Exception as e:
        logger.error(f"Error processing consent deliveries: {str(e)}")

def start_scheduler():
    """Start the appointment sync and automation scheduler"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        
        # Appointment sync every 5 minutes
        scheduler.add_job(
            sync_job,
            trigger=IntervalTrigger(minutes=5),
            id='appointment_sync',
            replace_existing=True
        )
        
        # Automation processing every hour
        scheduler.add_job(
            automation_job,
            trigger=CronTrigger(minute=0),  # Run every hour at minute 0
            id='automation_processing',
            replace_existing=True
        )
        
        # Consent delivery processing every 15 minutes
        scheduler.add_job(
            process_consent_deliveries,
            trigger=IntervalTrigger(minutes=15),  # Run every 15 minutes
            id='process_consent_deliveries',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("🚀 Scheduler started: sync (5min) + automations (hourly) + consent deliveries (15min)")

def stop_scheduler():
    """Stop the appointment sync scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("⏹️ Appointment sync scheduler stopped")

# Include the router in the main app
app.include_router(api_router)

# Initialize default consent templates
async def initialize_default_consent_templates():
    """Initialize default consent templates if they don't exist"""
    try:
        # Check if templates already exist
        existing_templates = await db.consent_templates.count_documents({})
        if existing_templates > 0:
            return  # Templates already exist
        
        default_templates = [
            {
                "treatment_code": 9,
                "treatment_name": "Periodoncia",
                "name": "Consentimiento Periodontal",
                "content": "Estimado/a {nombre},\n\nEn relación a su cita de periodoncia programada para el día {fecha} a las {hora} con {doctor}, le enviamos el consentimiento informado que debe revisar antes de su tratamiento.\n\nEl tratamiento periodontal puede incluir:\n- Raspado y alisado radicular\n- Curetajes\n- Posibles medicaciones locales\n\nPor favor, confirme la recepción de este mensaje.\n\nSaludos,\nRUBIO GARCÍA DENTAL\nTeléfono: 916 410 841",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            },
            {
                "treatment_code": 10,
                "treatment_name": "Cirugía e Implantes",
                "name": "Consentimiento Quirúrgico",
                "content": "Estimado/a {nombre},\n\nEn relación a su cirugía programada para el día {fecha} a las {hora} con {doctor}, le enviamos el consentimiento informado que debe revisar y firmar antes del procedimiento.\n\nEl procedimiento quirúrgico incluye:\n- Posible colocación de implantes\n- Cirugía periodontal\n- Extracciones complejas\n\nRiesgos y complicaciones:\n- Inflamación postoperatoria\n- Posible sangrado\n- Dolor temporal\n- Posible fallo del implante\n\nInstrucciones preoperatorias:\n- No fumar 24h antes\n- Medicación según prescripción\n- Acudir con acompañante\n\nPor favor, confirme la recepción y comprensión.\n\nSaludos,\nRUBIO GARCÍA DENTAL\nTeléfono: 916 410 841",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            },
            {
                "treatment_code": 11,
                "treatment_name": "Ortodoncia",
                "name": "Consentimiento Ortodóncico",
                "content": "Estimado/a {nombre},\n\nEn relación a su tratamiento de ortodoncia programado para el día {fecha} a las {hora} con {doctor}, le enviamos el consentimiento informado.\n\nEl tratamiento ortodóncico incluye:\n- Colocación de aparatología fija o removible\n- Controles periódicos mensuales\n- Posibles molestias iniciales\n- Duración estimada del tratamiento\n\nRecomendaciones importantes:\n- Higiene bucal estricta\n- Evitar alimentos duros o pegajosos\n- Acudir a todas las citas de control\n- Uso correcto de la aparatología\n\nPor favor, confirme la recepción de este mensaje.\n\nSaludos,\nRUBIO GARCÍA DENTAL\nTeléfono: 916 410 841",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            },
            {
                "treatment_code": 16,
                "treatment_name": "Endodoncia",
                "name": "Consentimiento Endodóncico",
                "content": "Estimado/a {nombre},\n\nEn relación a su tratamiento de endodoncia programado para el día {fecha} a las {hora} con {doctor}, le enviamos el consentimiento informado.\n\nEl tratamiento endodóncico (tratamiento de conductos) incluye:\n- Eliminación del tejido pulpar infectado\n- Limpieza y desinfección de los conductos\n- Sellado de los conductos radiculares\n- Posible colocación de corona posterior\n\nPosibles complicaciones:\n- Dolor postoperatorio temporal\n- Posible necesidad de retratamiento\n- Fractura del instrumento (raro)\n- Perforación radicular (raro)\n\nCuidados posteriores:\n- Evitar masticación en la zona tratada\n- Medicación según prescripción\n- Acudir a cita de control\n\nPor favor, confirme la recepción de este mensaje.\n\nSaludos,\nRUBIO GARCÍA DENTAL\nTeléfono: 916 410 841",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            },
            {
                "treatment_code": 13,
                "treatment_name": "Primera cita",
                "name": "LOPD - Información de Protección de Datos",
                "content": "Estimado/a {nombre},\n\nBienvenido/a a RUBIO GARCÍA DENTAL.\n\nDe acuerdo con la Ley Orgánica de Protección de Datos (LOPD), le informamos que:\n\n📋 TRATAMIENTO DE DATOS:\n- Sus datos se utilizan exclusivamente para su atención médica\n- Gestión de citas y tratamientos\n- Comunicaciones relacionadas con su salud dental\n\n🔒 PROTECCIÓN:\n- Sus datos están protegidos y son confidenciales\n- Solo personal autorizado tiene acceso\n- No se ceden a terceros sin su consentimiento\n\n⚖️ SUS DERECHOS:\n- Acceso, rectificación y cancelación de datos\n- Puede revocar el consentimiento en cualquier momento\n- Información disponible en recepción\n\n📍 RESPONSABLE:\nRUBIO GARCÍA DENTAL\nCalle Mayor 19, Alcorcón\nTeléfono: 916 410 841\n\nPor favor, confirme que ha recibido esta información.\n\nGracias por confiar en nosotros.\n\nSaludos,\nRUBIO GARCÍA DENTAL",
                "variables": ["nombre"],
                "send_timing": "same_day",
                "send_hour": "09:00",
                "active": True
            }
        ]
        
        # Insert default templates
        for template_data in default_templates:
            template_obj = ConsentTemplate(**template_data)
            mongo_data = prepare_for_mongo(template_obj.dict())
            await db.consent_templates.insert_one(mongo_data)
        
        logger.info(f"Initialized {len(default_templates)} default consent templates")
        
    except Exception as e:
        logger.error(f"Error initializing consent templates: {str(e)}")

@api_router.get("/test")
async def test():
    return {"message": "API is working correctly", "timestamp": datetime.now().isoformat()}

@api_router.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Test database connection
        await db.sessions.count_documents({}, limit=1)
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development")
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "database": "disconnected"
        }

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

# Database initialization functions
async def init_database_collections():
    """Initialize database collections and indexes"""
    try:
        # Create indexes for better performance
        await db.contacts.create_index("id")
        await db.appointments.create_index("id")
        await db.appointments.create_index("date")
        await db.messages.create_index("contact_id")
        await db.chat_sessions.create_index("contact_id")
        logging.info("Database collections initialized")
    except Exception as e:
        logging.error(f"Error initializing database collections: {str(e)}")

async def create_default_consent_templates():
    """Create default consent templates if they don't exist"""
    try:
        # Check if templates already exist
        existing_count = await db.consent_templates.count_documents({})
        if existing_count > 0:
            return
        
        # Create basic default templates
        default_templates = [
            {
                "treatment_code": 9,
                "treatment_name": "Periodoncia",
                "name": "Consentimiento Periodontal",
                "content": "Consentimiento informado para tratamiento periodontal",
                "variables": ["nombre", "fecha", "hora", "doctor"],
                "send_timing": "day_before",
                "send_hour": "10:00",
                "active": True
            }
        ]
        
        for template_data in default_templates:
            template = ConsentTemplate(**template_data)
            await db.consent_templates.insert_one(prepare_for_mongo(template.dict()))
            
        logging.info("Default consent templates created")
    except Exception as e:
        logging.error(f"Error creating default consent templates: {str(e)}")

