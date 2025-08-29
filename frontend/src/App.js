import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Calendar, MessageCircle, Users, BarChart3, Settings, Plus, Phone, Mail, MessageSquare, Clock, CheckCircle, XCircle, Search, Filter, Tag, Menu, X, Bot, Brain, Smartphone, Monitor, Zap } from "lucide-react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { toast, Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mobile Menu Component
const MobileMenu = ({ isOpen, onClose, navigationItems, activeTab, onTabChange }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="fixed top-0 left-0 w-64 h-full bg-white shadow-xl">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <img 
                src="https://customer-assets.emergentagent.com/job_omnidesk-2/artifacts/tckikfmy_Logo%20blanco.jpeg"
                alt="Rubio García Dental"
                className="w-8 h-8 rounded-lg object-contain bg-blue-600 p-1"
              />
              <div>
                <h1 className="text-sm font-bold text-blue-800">RUBIO GARCÍA</h1>
                <p className="text-xs text-gray-600">DENTAL</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
        
        <nav className="p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  onClose();
                }}
                className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === item.id
                    ? "bg-blue-50 text-blue-700 border border-blue-200"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      toast.error("Error loading dashboard stats");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">Panel de Control</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filtros
          </Button>
        </div>
      </div>

      {/* Stats Cards - Responsive Grid */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700">Pacientes Totales</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">{stats?.total_contacts || 0}</div>
            <p className="text-xs text-blue-600 mt-1">
              {stats?.active_contacts || 0} activos
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-50 to-green-50 border-emerald-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-emerald-700">Citas de Hoy</CardTitle>
            <Calendar className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-900">{stats?.today_appointments || 0}</div>
            <p className="text-xs text-emerald-600 mt-1">
              {stats?.total_appointments || 0} total este mes
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700">Mensajes Pendientes</CardTitle>
            <MessageCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900">{stats?.pending_messages || 0}</div>
            <p className="text-xs text-orange-600 mt-1">
              Requieren respuesta
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700">IA Conversaciones</CardTitle>
            <Bot className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">{stats?.ai_conversations || 0}</div>
            <p className="text-xs text-purple-600 mt-1">
              Chats activos
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Hero Section with Background Image */}
      <Card className="relative overflow-hidden bg-slate-900 text-white">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{ 
            backgroundImage: 'url(https://images.unsplash.com/photo-1608222351212-18fe0ec7b13b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwyfHxidXNpbmVzcyUyMGRhc2hib2FyZHxlbnwwfHx8fDE3NTY0MjY1Nzd8MA&ixlib=rb-4.1.0&q=85)' 
          }}
        />
        <div className="relative z-10">
          <CardHeader>
            <CardTitle className="text-xl lg:text-2xl">Gestión Dental Inteligente con IA</CardTitle>
            <CardDescription className="text-slate-300">
              Automatiza las conversaciones de WhatsApp, agenda citas y mejora la experiencia de tus pacientes con inteligencia artificial.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button variant="secondary" size="sm">
                <Bot className="w-4 h-4 mr-2" />
                Configurar IA
              </Button>
              <Button variant="outline" size="sm" className="text-white border-white hover:bg-white hover:text-slate-900">
                <Zap className="w-4 h-4 mr-2" />
                Ver Analíticas
              </Button>
            </div>
          </CardContent>
        </div>
      </Card>

      {/* Quick Actions & Activity - Responsive Layout */}
      <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Acciones Rápidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Paciente
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              Agendar Cita
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Bot className="w-4 h-4 mr-2" />
              Entrenar IA
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Actividad Reciente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Cita confirmada con paciente</span>
              </div>
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-purple-500" />
                <span>IA respondió consulta de WhatsApp</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-orange-500" />
                <span>Recordatorio enviado automáticamente</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Platform Support */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Optimizado para Todas las Plataformas</h3>
              <p className="text-blue-600 text-sm">Accede desde cualquier dispositivo - escritorio, tablet o móvil</p>
            </div>
            <div className="flex space-x-4">
              <div className="flex flex-col items-center p-3 bg-white rounded-lg shadow-sm">
                <Monitor className="w-6 h-6 text-blue-600 mb-1" />
                <span className="text-xs text-blue-600">Escritorio</span>
              </div>
              <div className="flex flex-col items-center p-3 bg-white rounded-lg shadow-sm">
                <Smartphone className="w-6 h-6 text-blue-600 mb-1" />
                <span className="text-xs text-blue-600">Móvil</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Contacts Component (Updated for mobile)
const Contacts = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newContact, setNewContact] = useState({
    name: "",
    email: "",
    phone: "",
    whatsapp: "",
    notes: "",
    tags: []
  });

  useEffect(() => {
    fetchContacts();
  }, [selectedStatus]);

  const fetchContacts = async () => {
    try {
      const params = selectedStatus !== "all" ? { status: selectedStatus } : {};
      const response = await axios.get(`${API}/contacts`, { params });
      setContacts(response.data);
    } catch (error) {
      console.error("Error fetching contacts:", error);
      toast.error("Error loading contacts");
    } finally {
      setLoading(false);
    }
  };

  const createContact = async () => {
    try {
      await axios.post(`${API}/contacts`, newContact);
      toast.success("Paciente creado exitosamente");
      setShowCreateDialog(false);
      setNewContact({ name: "", email: "", phone: "", whatsapp: "", notes: "", tags: [] });
      fetchContacts();
    } catch (error) {
      console.error("Error creating contact:", error);
      toast.error("Error al crear paciente");
    }
  };

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (contact.email && contact.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (contact.phone && contact.phone.includes(searchTerm))
  );

  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">Pacientes</h1>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Nuevo Paciente</span>
              <span className="sm:hidden">Nuevo</span>
            </Button>
          </DialogTrigger>
          <DialogContent className="w-full max-w-lg mx-4">
            <DialogHeader>
              <DialogTitle>Crear Nuevo Paciente</DialogTitle>
              <DialogDescription>
                Agrega un nuevo paciente a tu lista.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Nombre *</Label>
                <Input
                  id="name"
                  value={newContact.name}
                  onChange={(e) => setNewContact({...newContact, name: e.target.value})}
                  placeholder="Nombre completo"
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={newContact.email}
                  onChange={(e) => setNewContact({...newContact, email: e.target.value})}
                  placeholder="correo@ejemplo.com"
                />
              </div>
              <div>
                <Label htmlFor="phone">Teléfono</Label>
                <Input
                  id="phone"
                  value={newContact.phone}
                  onChange={(e) => setNewContact({...newContact, phone: e.target.value})}
                  placeholder="+1234567890"
                />
              </div>
              <div>
                <Label htmlFor="whatsapp">WhatsApp</Label>
                <Input
                  id="whatsapp"
                  value={newContact.whatsapp}
                  onChange={(e) => setNewContact({...newContact, whatsapp: e.target.value})}
                  placeholder="+1234567890"
                />
              </div>
              <div>
                <Label htmlFor="notes">Notas</Label>
                <Textarea
                  id="notes"
                  value={newContact.notes}
                  onChange={(e) => setNewContact({...newContact, notes: e.target.value})}
                  placeholder="Información adicional..."
                  className="min-h-[80px]"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={createContact} disabled={!newContact.name}>
                Crear Paciente
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters - Responsive */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Buscar pacientes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            <SelectItem value="active">Activos</SelectItem>
            <SelectItem value="inactive">Inactivos</SelectItem>
            <SelectItem value="blocked">Bloqueados</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Contacts List - Mobile Optimized */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredContacts.length > 0 ? (
          filteredContacts.map((contact) => (
            <Card key={contact.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                    {contact.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-slate-900 truncate">{contact.name}</h3>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 text-sm text-slate-500 gap-1 sm:gap-0">
                      {contact.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="w-3 h-3 flex-shrink-0" />
                          <span className="truncate">{contact.email}</span>
                        </div>
                      )}
                      {contact.phone && (
                        <div className="flex items-center space-x-1">
                          <Phone className="w-3 h-3 flex-shrink-0" />
                          <span>{contact.phone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between lg:justify-end space-x-2">
                  <div className="flex flex-wrap gap-1">
                    {contact.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <Badge 
                    variant={contact.status === 'active' ? 'default' : 'secondary'}
                    className="text-xs flex-shrink-0"
                  >
                    {contact.status === 'active' ? 'Activo' : 
                     contact.status === 'inactive' ? 'Inactivo' : 'Bloqueado'}
                  </Badge>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card className="p-8 text-center">
            <Users className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-600 mb-2">No hay pacientes</h3>
            <p className="text-slate-500">Crea tu primer paciente para comenzar.</p>
          </Card>
        )}
      </div>
    </div>
  );
};

// AI Training Component
const AITraining = () => {
  const [training, setTraining] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [formData, setFormData] = useState({
    practice_name: "RUBIO GARCÍA DENTAL",
    system_prompt: "",
    specialties: ["Implantología", "Estética dental", "Ortodoncia"],
    services: ["Consultas generales", "Limpiezas", "Implantes", "Blanqueamientos"],
    working_hours: "Lunes a Viernes 9:00-18:00",
    emergency_contact: "",
    appointment_instructions: "",
    policies: "",
    personality: "profesional y amigable",
    language: "español"
  });

  useEffect(() => {
    fetchTraining();
  }, []);

  const fetchTraining = async () => {
    try {
      const response = await axios.get(`${API}/ai/training`);
      if (response.data) {
        setTraining(response.data);
        setFormData(response.data);
      }
    } catch (error) {
      console.error("Error fetching AI training:", error);
    } finally {
      setLoading(false);
    }
  };

  const saveTraining = async () => {
    try {
      if (training) {
        await axios.put(`${API}/ai/training`, formData);
        toast.success("Configuración de IA actualizada");
      } else {
        await axios.post(`${API}/ai/training`, formData);
        toast.success("Configuración de IA creada");
      }
      setShowEditDialog(false);
      fetchTraining();
    } catch (error) {
      console.error("Error saving AI training:", error);
      toast.error("Error al guardar configuración");
    }
  };

  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">Entrenamiento de IA</h1>
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogTrigger asChild>
            <Button>
              <Brain className="w-4 h-4 mr-2" />
              {training ? "Editar IA" : "Configurar IA"}
            </Button>
          </DialogTrigger>
          <DialogContent className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Configuración de IA</DialogTitle>
              <DialogDescription>
                Entrena a tu asistente virtual para que responda como deseas
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="practice_name">Nombre de la Clínica</Label>
                <Input
                  id="practice_name"
                  value={formData.practice_name}
                  onChange={(e) => setFormData({...formData, practice_name: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="specialties">Especialidades</Label>
                <Input
                  id="specialties"
                  value={formData.specialties.join(", ")}
                  onChange={(e) => setFormData({...formData, specialties: e.target.value.split(", ")})}
                  placeholder="Implantología, Estética dental, Ortodoncia"
                />
              </div>

              <div>
                <Label htmlFor="services">Servicios</Label>
                <Input
                  id="services"
                  value={formData.services.join(", ")}
                  onChange={(e) => setFormData({...formData, services: e.target.value.split(", ")})}
                  placeholder="Consultas, Limpiezas, Implantes"
                />
              </div>

              <div>
                <Label htmlFor="working_hours">Horarios de Atención</Label>
                <Input
                  id="working_hours"
                  value={formData.working_hours}
                  onChange={(e) => setFormData({...formData, working_hours: e.target.value})}
                />
              </div>

              <div>
                <Label htmlFor="system_prompt">Instrucciones para la IA</Label>
                <Textarea
                  id="system_prompt"
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({...formData, system_prompt: e.target.value})}
                  placeholder="Describe cómo debe comportarse la IA, qué información puede dar, etc."
                  className="min-h-[100px]"
                />
              </div>

              <div>
                <Label htmlFor="appointment_instructions">Instrucciones para Citas</Label>
                <Textarea
                  id="appointment_instructions"
                  value={formData.appointment_instructions}
                  onChange={(e) => setFormData({...formData, appointment_instructions: e.target.value})}
                  placeholder="¿Qué información necesitas para agendar citas?"
                  className="min-h-[80px]"
                />
              </div>

              <div>
                <Label htmlFor="personality">Personalidad de la IA</Label>
                <Select value={formData.personality} onValueChange={(value) => setFormData({...formData, personality: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="profesional y amigable">Profesional y Amigable</SelectItem>
                    <SelectItem value="formal">Formal</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="empático">Empático</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={saveTraining}>
                Guardar Configuración
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : training ? (
        <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-purple-600" />
                <span>Configuración Actual</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-gray-600">Clínica</Label>
                <p className="text-sm text-gray-900">{training.practice_name}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Personalidad</Label>
                <p className="text-sm text-gray-900 capitalize">{training.personality}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Horarios</Label>
                <p className="text-sm text-gray-900">{training.working_hours}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Especialidades</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {training.specialties.map((specialty, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-green-600" />
                <span>Prueba la IA</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-600 mb-2">Mensaje de prueba:</p>
                <p className="text-sm">"Hola, ¿pueden atenderme hoy?"</p>
              </div>
              <Button className="w-full" variant="outline">
                <MessageCircle className="w-4 h-4 mr-2" />
                Probar Conversación
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card className="p-8 text-center">
          <Bot className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">Configura tu IA</h3>
          <p className="text-slate-500 mb-4">Entrena a tu asistente virtual para responder a los pacientes automáticamente</p>
          <Button onClick={() => setShowEditDialog(true)}>
            <Brain className="w-4 h-4 mr-2" />
            Comenzar Configuración
          </Button>
        </Card>
      )}
    </div>
  );
};

// Agenda Component with Monthly Calendar and Appointment List
const Agenda = () => {
  // Start with January 2, 2025 (where the real appointments start - 23 appointments available)
  const [appointments, setAppointments] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date(2025, 0, 2)); // January 2, 2025 (where real appointments exist)
  const [loading, setLoading] = useState(false);
  const [selectedAppointments, setSelectedAppointments] = useState([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Format date to YYYY-MM-DD
  const formatDateForAPI = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Format date for display
  const formatDateForDisplay = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    });
  };

  // Format time for display
  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get status color
  const getStatusColor = (status) => {
    const colors = {
      'scheduled': 'bg-blue-100 text-blue-800',
      'confirmed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800',
      'completed': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  // Get status text
  const getStatusText = (status) => {
    const texts = {
      'scheduled': 'Programada',
      'confirmed': 'Confirmada',
      'cancelled': 'Cancelada',
      'completed': 'Completada'
    };
    return texts[status] || status;
  };

  // Fetch appointments for selected date
  const fetchAppointments = async (date) => {
    setLoading(true);
    try {
      const dateStr = formatDateForAPI(date);
      console.log(`🔍 Fetching appointments for date: ${dateStr}`);
      
      const response = await axios.get(`${API}/appointments/by-date?date=${dateStr}`);
      console.log(`✅ API Response:`, response.data);
      
      setAppointments(response.data);
      
      if (response.data.length > 0) {
        console.log(`📅 Found ${response.data.length} appointments for ${dateStr}`);
      } else {
        console.log(`📭 No appointments found for ${dateStr}`);
      }
    } catch (error) {
      console.error("❌ Error fetching appointments:", error);
      console.error("Error details:", error.response?.data);
      toast.error("Error loading appointments");
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  // Generate calendar days for the month
  const getCalendarDays = () => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    
    // Convert Sunday=0 based getDay() to Monday=0 based for our calendar
    const firstDayWeekday = (firstDayOfMonth.getDay() + 6) % 7;
    
    const days = [];
    
    // Add previous month's trailing days
    for (let i = firstDayWeekday - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      days.push({ date, isCurrentMonth: false });
    }
    
    // Add current month's days
    for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
      const date = new Date(year, month, day);
      days.push({ date, isCurrentMonth: true });
    }
    
    // Add next month's leading days to complete the grid
    const remainingDays = 42 - days.length;
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day);
      days.push({ date, isCurrentMonth: false });
    }
    
    return days;
  };

  // Handle calendar navigation
  const navigateMonth = (direction) => {
    const newDate = new Date(selectedDate);
    newDate.setMonth(selectedDate.getMonth() + direction);
    setSelectedDate(newDate);
  };

  // Handle day selection
  const selectDay = (date) => {
    setSelectedDate(date);
    fetchAppointments(date);
  };

  // Handle appointment selection
  const toggleAppointmentSelection = (appointmentId) => {
    setSelectedAppointments(prev => {
      if (prev.includes(appointmentId)) {
        return prev.filter(id => id !== appointmentId);
      } else {
        return [...prev, appointmentId];
      }
    });
  };

  // Send confirmation messages
  const sendConfirmationMessages = () => {
    // This will be implemented later
    toast.success(`Se enviarán mensajes de confirmación a ${selectedAppointments.length} citas seleccionadas`);
    setSelectedAppointments([]);
    setShowConfirmDialog(false);
  };

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedDate) {
        fetchAppointments(selectedDate);
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [selectedDate]);

  // Initial load
  useEffect(() => {
    fetchAppointments(selectedDate);
  }, []);

  const calendarDays = getCalendarDays();
  const today = new Date();
  const todayStr = formatDateForAPI(today);
  const selectedDateStr = formatDateForAPI(selectedDate);

  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">
          Agenda - {formatDateForDisplay(selectedDate)}
        </h1>
        {selectedAppointments.length > 0 && (
          <Button onClick={() => setShowConfirmDialog(true)} className="bg-blue-600 hover:bg-blue-700">
            <MessageCircle className="w-4 h-4 mr-2" />
            Enviar Confirmaciones ({selectedAppointments.length})
          </Button>
        )}
      </div>

      {/* Monthly Calendar */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              {selectedDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
            </CardTitle>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => navigateMonth(-1)}>
                ←
              </Button>
              <Button variant="outline" size="sm" onClick={() => selectDay(today)}>
                Hoy
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigateMonth(1)}>
                →
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Calendar Header */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map(day => (
              <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
                {day}
              </div>
            ))}
          </div>
          
          {/* Calendar Days */}
          <div className="grid grid-cols-7 gap-1">
            {calendarDays.map((dayInfo, index) => {
              const dayStr = formatDateForAPI(dayInfo.date);
              const isToday = dayStr === todayStr;
              const isSelected = dayStr === selectedDateStr;
              
              return (
                <button
                  key={index}
                  onClick={() => selectDay(dayInfo.date)}
                  className={`
                    p-2 text-sm rounded-lg hover:bg-blue-50 transition-colors
                    ${dayInfo.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                    ${isToday ? 'bg-blue-100 font-semibold text-blue-600' : ''}
                    ${isSelected ? 'bg-blue-600 text-white hover:bg-blue-700' : ''}
                  `}
                >
                  {dayInfo.date.getDate()}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Appointment List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>Citas del {formatDateForDisplay(selectedDate)}</span>
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 ml-2"></div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : appointments.length > 0 ? (
            <div className="space-y-3">
              {appointments.map((appointment) => (
                <div 
                  key={appointment.id}
                  className={`p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer ${
                    selectedAppointments.includes(appointment.id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                  }`}
                  onClick={() => toggleAppointmentSelection(appointment.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={selectedAppointments.includes(appointment.id)}
                          onChange={() => toggleAppointmentSelection(appointment.id)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                          {appointment.contact_name.charAt(0).toUpperCase()}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2">
                          <div>
                            <h3 className="font-semibold text-gray-900">
                              {appointment.contact_name}
                            </h3>
                            <p className="text-sm text-gray-600 truncate">
                              {appointment.title}
                            </p>
                            {appointment.description && (
                              <p className="text-xs text-gray-500 mt-1">
                                {appointment.description}
                              </p>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-3 text-sm">
                            <div className="flex items-center space-x-1 text-gray-600">
                              <Clock className="w-4 h-4" />
                              <span>{formatTime(appointment.date)}</span>
                            </div>
                            
                            <div className="flex items-center space-x-1 text-gray-600">
                              <span>{appointment.duration_minutes} min</span>
                            </div>
                            
                            <Badge className={getStatusColor(appointment.status)}>
                              {getStatusText(appointment.status)}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">No hay citas programadas</h3>
              <p className="text-gray-500">No se encontraron citas para el día seleccionado.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enviar Mensajes de Confirmación</DialogTitle>
            <DialogDescription>
              ¿Deseas enviar mensajes de confirmación a las {selectedAppointments.length} citas seleccionadas?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={sendConfirmationMessages}>
              Enviar Confirmaciones
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Messages Component (Updated)
const Messages = () => {
  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">WhatsApp IA</h1>
        <Button>
          <MessageCircle className="w-4 h-4 mr-2" />
          <span className="hidden sm:inline">Nueva Conversación</span>
          <span className="sm:hidden">Nueva</span>
        </Button>
      </div>

      <Card 
        className="relative overflow-hidden"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1556745753-b2904692b3cd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxjdXN0b21lciUyMHNlcnZpY2V8ZW58MHx8fHwxNzU2NDI2NTg0fDA&ixlib=rb-4.1.0&q=85)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-slate-900 bg-opacity-80" />
        <CardHeader className="relative z-10 text-white">
          <CardTitle className="text-xl lg:text-2xl">WhatsApp con Inteligencia Artificial</CardTitle>
          <CardDescription className="text-slate-300">
            Respuestas automáticas a consultas de pacientes, agendamiento de citas y atención 24/7.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="text-center py-12">
        <Bot className="w-16 h-16 text-purple-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-slate-600 mb-2">Conecta WhatsApp Business</h3>
        <p className="text-slate-500 mb-4">Configura la IA primero, luego conecta tu WhatsApp Business para automatizar respuestas</p>
        <Button variant="outline">
          <MessageSquare className="w-4 h-4 mr-2" />
          Configurar Conexión
        </Button>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "contacts", label: "Pacientes", icon: Users },
    { id: "agenda", label: "Agenda", icon: Calendar },
    { id: "messages", label: "WhatsApp IA", icon: MessageCircle },
    { id: "ai-training", label: "Entrenar IA", icon: Brain },
    { id: "settings", label: "Configuración", icon: Settings }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "contacts":
        return <Contacts />;
      case "agenda":
        return <Agenda />;
      case "messages":
        return <Messages />;
      case "ai-training":
        return <AITraining />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Toaster position="top-right" />
        <div className="flex">
          {/* Desktop Sidebar */}
          <div className="hidden lg:block w-64 bg-white shadow-sm border-r">
            <div className="p-6">
              <div className="flex items-center space-x-3">
                <img 
                  src="https://customer-assets.emergentagent.com/job_omnidesk-2/artifacts/tckikfmy_Logo%20blanco.jpeg"
                  alt="Rubio García Dental"
                  className="w-10 h-10 rounded-lg object-contain bg-blue-600 p-2"
                />
                <div>
                  <h1 className="text-lg font-bold text-blue-800">RUBIO GARCÍA</h1>
                  <p className="text-sm text-gray-600">DENTAL</p>
                </div>
              </div>
            </div>
            
            <nav className="px-4 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === item.id
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Mobile Header */}
          <div className="lg:hidden fixed top-0 left-0 right-0 bg-white border-b z-40">
            <div className="flex items-center justify-between p-4">
              <div className="flex items-center space-x-2">
                <img 
                  src="https://customer-assets.emergentagent.com/job_omnidesk-2/artifacts/tckikfmy_Logo%20blanco.jpeg"
                  alt="Rubio García Dental"
                  className="w-8 h-8 rounded-lg object-contain bg-blue-600 p-1"
                />
                <div>
                  <h1 className="text-sm font-bold text-blue-800">RUBIO GARCÍA</h1>
                  <p className="text-xs text-gray-600">DENTAL</p>
                </div>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setIsMobileMenuOpen(true)}
              >
                <Menu className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Mobile Menu */}
          <MobileMenu
            isOpen={isMobileMenuOpen}
            onClose={() => setIsMobileMenuOpen(false)}
            navigationItems={navigationItems}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />

          {/* Main Content */}
          <div className="flex-1 p-4 lg:p-8 pt-20 lg:pt-8">
            {renderContent()}
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;