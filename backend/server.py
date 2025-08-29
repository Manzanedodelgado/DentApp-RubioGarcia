from fastapi import FastAPI, APIRouter, HTTPException, Query
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

class DashboardStats(BaseModel):
    total_contacts: int
    active_contacts: int
    total_appointments: int
    today_appointments: int
    pending_messages: int
    active_campaigns: int

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
    
    return DashboardStats(
        total_contacts=total_contacts,
        active_contacts=active_contacts,
        total_appointments=total_appointments,
        today_appointments=today_appointments,
        pending_messages=pending_messages,
        active_campaigns=active_campaigns
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()