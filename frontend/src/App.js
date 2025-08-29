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

// Communications Component - WhatsApp-style interface with patient chat and AI
const Communications = () => {
  const [contacts, setContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [aiEnabled, setAiEnabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [patientHistory, setPatientHistory] = useState([]);

  // Fetch contacts (patients)
  const fetchContacts = async () => {
    try {
      const response = await axios.get(`${API}/contacts`);
      setContacts(response.data);
    } catch (error) {
      console.error("Error fetching contacts:", error);
    }
  };

  // Fetch patient appointment history
  const fetchPatientHistory = async (contactId) => {
    try {
      const response = await axios.get(`${API}/appointments`);
      const patientAppointments = response.data.filter(apt => apt.contact_id === contactId);
      // Sort by date, most recent first
      patientAppointments.sort((a, b) => new Date(b.date) - new Date(a.date));
      setPatientHistory(patientAppointments.slice(0, 10)); // Last 10 appointments
    } catch (error) {
      console.error("Error fetching patient history:", error);
      setPatientHistory([]);
    }
  };

  // Send message to patient
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedContact) return;

    setLoading(true);
    try {
      // Here you would integrate with WhatsApp API
      const messageData = {
        contact_id: selectedContact.id,
        message: newMessage,
        type: 'outbound',
        timestamp: new Date().toISOString()
      };

      // Add to local messages (simulate sending)
      setMessages(prev => [...prev, {
        id: Date.now(),
        ...messageData,
        status: 'sent'
      }]);

      setNewMessage('');
      toast.success("Mensaje enviado correctamente");
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Error enviando mensaje");
    } finally {
      setLoading(false);
    }
  };

  // Format time
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format treatment status
  const getStatusColor = (status) => {
    const colors = {
      'scheduled': 'text-blue-600',
      'confirmed': 'text-green-600',
      'cancelled': 'text-red-600',
      'completed': 'text-gray-600'
    };
    return colors[status] || 'text-gray-600';
  };

  const getStatusText = (status) => {
    const texts = {
      'scheduled': 'Programada',
      'confirmed': 'Confirmada',
      'cancelled': 'Cancelada',
      'completed': 'Completada'
    };
    return texts[status] || status;
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  useEffect(() => {
    if (selectedContact) {
      fetchPatientHistory(selectedContact.id);
    }
  }, [selectedContact]);

  return (
    <div className="h-screen flex">
      {/* Left Sidebar - Contact List */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Comunicaciones</h2>
          </div>
          
          {/* AI Toggle */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Bot className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">IA Activa</span>
            </div>
            <button
              onClick={() => setAiEnabled(!aiEnabled)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                aiEnabled ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                  aiEnabled ? 'translate-x-5' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar paciente..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Contact List */}
        <div className="flex-1 overflow-y-auto">
          {contacts.map(contact => (
            <div
              key={contact.id}
              onClick={() => setSelectedContact(contact)}
              className={`p-4 cursor-pointer hover:bg-gray-50 border-b border-gray-100 ${
                selectedContact?.id === contact.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  {contact.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {contact.name}
                  </h3>
                  <p className="text-xs text-gray-500 truncate">
                    {contact.phone || 'Sin teléfono'}
                  </p>
                  <p className="text-xs text-green-600">
                    {aiEnabled ? 'IA activa' : 'Manual'}
                  </p>
                </div>
                <div className="text-xs text-gray-400">
                  10:30
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Center - Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedContact ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 bg-white">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {selectedContact.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedContact.name}</h3>
                  <p className="text-sm text-gray-500">{selectedContact.phone}</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
              {messages.length > 0 ? (
                <div className="space-y-4">
                  {messages.map(message => (
                    <div key={message.id} className={`flex ${message.type === 'outbound' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs px-4 py-2 rounded-lg ${
                        message.type === 'outbound'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border'
                      }`}>
                        <p className="text-sm">{message.message}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'outbound' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p>Selecciona un paciente para iniciar la conversación</p>
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Escribe un mensaje..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <Button
                  onClick={sendMessage}
                  disabled={loading || !newMessage.trim()}
                  className="rounded-full px-6"
                >
                  {loading ? '...' : 'Enviar'}
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">Selecciona un paciente para comenzar</p>
            </div>
          </div>
        )}
      </div>

      {/* Right Sidebar - Patient Info */}
      {selectedContact && (
        <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
          {/* Patient Summary */}
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-lg mb-4">Información del Paciente</h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</label>
                <p className="text-sm font-medium">{selectedContact.name}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">Teléfono</label>
                <p className="text-sm">{selectedContact.phone || 'No especificado'}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</label>
                <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  {selectedContact.status || 'Activo'}
                </span>
              </div>
            </div>
          </div>

          {/* Appointment History */}
          <div className="p-4">
            <h4 className="font-semibold mb-3">Historial de Citas</h4>
            
            {patientHistory.length > 0 ? (
              <div className="space-y-3">
                {patientHistory.map((appointment, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium">
                        {new Date(appointment.date).toLocaleDateString('es-ES')}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(appointment.status)}`}>
                        {getStatusText(appointment.status)}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-1">
                      <strong>Doctor:</strong> {appointment.doctor || 'No especificado'}
                    </p>
                    
                    <p className="text-sm text-gray-600 mb-1">
                      <strong>Tratamiento:</strong> {appointment.treatment || 'No especificado'}
                    </p>
                    
                    <p className="text-xs text-gray-500">
                      Hora: {appointment.time || 'No especificada'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No hay historial de citas</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
const Agenda = () => {
  const [selectedDate, setSelectedDate] = useState(new Date(2025, 0, 1)); // January 1, 2025
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);

  // Format date for API (YYYY-MM-DD)
  const formatDateForAPI = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Format date for display 
  const formatDateForDisplay = (date) => {
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    });
  };

  // Get status icon and color for appointment status
  const getStatusDisplay = (status) => {
    const statusMap = {
      'scheduled': { text: 'Planificada', color: 'text-blue-600', bg: 'bg-blue-50', icon: '📅' },
      'confirmed': { text: 'Confirmada', color: 'text-green-600', bg: 'bg-green-50', icon: '✅' },
      'cancelled': { text: 'Cancelada', color: 'text-red-600', bg: 'bg-red-50', icon: '❌' },
      'completed': { text: 'Completada', color: 'text-gray-600', bg: 'bg-gray-50', icon: '✔️' }
    };
    return statusMap[status] || statusMap['scheduled'];
  };

  // Fetch appointments for selected date
  const fetchAppointments = async (date) => {
    setLoading(true);
    try {
      const dateStr = formatDateForAPI(date);
      console.log(`Fetching appointments for: ${dateStr}`);
      
      const response = await axios.get(`${API}/appointments/by-date?date=${dateStr}`);
      
      // Sort by time (Hora column) within the selected date
      const sortedAppointments = response.data.sort((a, b) => {
        const timeA = a.time || a.date.split('T')[1] || '00:00';
        const timeB = b.time || b.date.split('T')[1] || '00:00';
        return timeA.localeCompare(timeB);
      });
      
      setAppointments(sortedAppointments);
      console.log(`Found ${sortedAppointments.length} appointments for ${dateStr}`);
    } catch (error) {
      console.error("Error fetching appointments:", error);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  // Load appointments when date changes
  useEffect(() => {
    fetchAppointments(selectedDate);
  }, [selectedDate]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Agenda - {formatDateForDisplay(selectedDate)}</h1>
      
      {/* Date Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Seleccionar Fecha</CardTitle>
        </CardHeader>
        <CardContent>
          <input 
            type="date" 
            value={formatDateForAPI(selectedDate)}
            onChange={(e) => setSelectedDate(new Date(e.target.value))}
            className="w-full p-3 border rounded-lg text-lg"
            min="2025-01-01"
          />
        </CardContent>
      </Card>

      {/* Appointments List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Citas para {formatDateForDisplay(selectedDate)}</span>
            <span className="text-sm font-normal text-gray-500">
              {appointments.length} cita{appointments.length !== 1 ? 's' : ''}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Cargando citas...</p>
            </div>
          ) : appointments.length > 0 ? (
            <div className="space-y-4">
              {appointments.map((appointment, index) => {
                const statusDisplay = getStatusDisplay(appointment.status);
                return (
                  <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    
                    {/* Header with Name, Patient Number and Status */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {appointment.contact_name.split(' ').map(n => n.charAt(0)).join('').slice(0,2)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">
                            {appointment.contact_name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            NumPac: {appointment.patient_number || 'N/A'}
                          </p>
                        </div>
                      </div>
                      
                      {/* Status Check */}
                      <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${statusDisplay.bg}`}>
                        <span className="text-lg">{statusDisplay.icon}</span>
                        <span className={`text-sm font-medium ${statusDisplay.color}`}>
                          {statusDisplay.text}
                        </span>
                      </div>
                    </div>

                    {/* Appointment Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 p-3 rounded-lg">
                      
                      {/* Time */}
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-medium">Hora:</span>
                        <span className="text-sm">
                          {appointment.time || new Date(appointment.date).toLocaleTimeString('es-ES', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>

                      {/* Phone */}
                      <div className="flex items-center space-x-2">
                        <Phone className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-medium">Teléfono:</span>
                        <span className="text-sm">{appointment.phone || 'No especificado'}</span>
                      </div>

                      {/* Treatment */}
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-medium">Tratamiento:</span>
                        <span className="text-sm">{appointment.treatment || 'No especificado'}</span>
                      </div>

                      {/* Doctor */}
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-medium">Doctor:</span>
                        <span className="text-sm">{appointment.doctor || 'No asignado'}</span>
                      </div>

                    </div>

                    {/* Status Change Options */}
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-gray-500 mb-2">Cambiar estado:</p>
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => {/* TODO: Update status */}}
                          className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200"
                        >
                          📅 Planificada
                        </button>
                        <button 
                          onClick={() => {/* TODO: Update status */}}
                          className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200"
                        >
                          ✅ Confirmada
                        </button>
                        <button 
                          onClick={() => {/* TODO: Update status */}}
                          className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full hover:bg-red-200"
                        >
                          ❌ Cancelada
                        </button>
                      </div>
                    </div>

                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No hay citas programadas</h3>
              <p>No se encontraron citas para la fecha seleccionada.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Templates Component - CRUD management for message templates
const Templates = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [formData, setFormData] = useState({ name: '', content: '' });

  // Available variables for templates
  const availableVariables = [
    { name: 'nombre', description: 'Nombre completo del paciente', example: 'Juan Pérez' },
    { name: 'fecha', description: 'Fecha de la cita', example: '15 de enero de 2025' },
    { name: 'hora', description: 'Hora de la cita', example: '10:30' },
    { name: 'doctor', description: 'Nombre del doctor asignado', example: 'Dr. Mario Rubio' },
    { name: 'tratamiento', description: 'Tipo de tratamiento', example: 'Revisión' },
    { name: 'telefono', description: 'Teléfono del paciente', example: '+34 666 555 444' },
    { name: 'numpac', description: 'Número de paciente', example: '12345' }
  ];

  // Fetch templates from backend
  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error("Error fetching templates:", error);
      toast.error("Error cargando plantillas");
    } finally {
      setLoading(false);
    }
  };

  // Create new template
  const handleCreate = async () => {
    if (!formData.name.trim() || !formData.content.trim()) {
      toast.error("Nombre y contenido son obligatorios");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/templates`, formData);
      toast.success("Plantilla creada exitosamente");
      setShowCreateDialog(false);
      setFormData({ name: '', content: '' });
      fetchTemplates();
    } catch (error) {
      console.error("Error creating template:", error);
      toast.error("Error creando plantilla");
    } finally {
      setLoading(false);
    }
  };

  // Update existing template
  const handleUpdate = async () => {
    if (!formData.name.trim() || !formData.content.trim()) {
      toast.error("Nombre y contenido son obligatorios");
      return;
    }

    setLoading(true);
    try {
      await axios.put(`${API}/templates/${selectedTemplate.id}`, formData);
      toast.success("Plantilla actualizada exitosamente");
      setShowEditDialog(false);
      setSelectedTemplate(null);
      setFormData({ name: '', content: '' });
      fetchTemplates();
    } catch (error) {
      console.error("Error updating template:", error);
      toast.error("Error actualizando plantilla");
    } finally {
      setLoading(false);
    }
  };

  // Delete template
  const handleDelete = async () => {
    setLoading(true);
    try {
      await axios.delete(`${API}/templates/${selectedTemplate.id}`);
      toast.success("Plantilla eliminada exitosamente");
      setShowDeleteDialog(false);
      setSelectedTemplate(null);
      fetchTemplates();
    } catch (error) {
      console.error("Error deleting template:", error);
      toast.error("Error eliminando plantilla");
    } finally {
      setLoading(false);
    }
  };

  // Open edit dialog
  const openEditDialog = (template) => {
    setSelectedTemplate(template);
    setFormData({ name: template.name, content: template.content });
    setShowEditDialog(true);
  };

  // Open delete dialog
  const openDeleteDialog = (template) => {
    setSelectedTemplate(template);
    setShowDeleteDialog(true);
  };

  // Insert variable into content
  const insertVariable = (variable) => {
    const newContent = formData.content + `{${variable.name}}`;
    setFormData({ ...formData, content: newContent });
  };

  // Preview template with sample data
  const previewTemplate = (content) => {
    return content
      .replace(/{nombre}/g, 'Juan Pérez')
      .replace(/{fecha}/g, '15 de enero de 2025')
      .replace(/{hora}/g, '10:30')
      .replace(/{doctor}/g, 'Dr. Mario Rubio')
      .replace(/{tratamiento}/g, 'Revisión')
      .replace(/{telefono}/g, '+34 666 555 444')
      .replace(/{numpac}/g, '12345');
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gestión de Plantillas</h1>
          <p className="text-gray-600 mt-2">Crea y administra plantillas de mensajes para recordatorios</p>
        </div>
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nueva Plantilla
        </Button>
      </div>

      {/* Available Variables Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Variables Disponibles</CardTitle>
          <CardDescription>
            Usa estas variables en tus plantillas para personalizar los mensajes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableVariables.map(variable => (
              <div key={variable.name} className="p-3 border rounded-lg bg-gray-50">
                <div className="flex items-center space-x-2 mb-2">
                  <code className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                    {`{${variable.name}}`}
                  </code>
                </div>
                <p className="text-sm text-gray-600 mb-1">{variable.description}</p>
                <p className="text-xs text-gray-500">Ejemplo: {variable.example}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Templates List */}
      <Card>
        <CardHeader>
          <CardTitle>Plantillas Creadas ({templates.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Cargando plantillas...</p>
            </div>
          ) : templates.length > 0 ? (
            <div className="space-y-4">
              {templates.map(template => (
                <div key={template.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {template.name}
                      </h3>
                      
                      {/* Original Content */}
                      <div className="mb-3">
                        <Label className="text-sm font-medium text-gray-700">Plantilla:</Label>
                        <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded mt-1 font-mono">
                          {template.content}
                        </p>
                      </div>
                      
                      {/* Preview */}
                      <div className="mb-3">
                        <Label className="text-sm font-medium text-gray-700">Vista previa:</Label>
                        <p className="text-sm text-gray-800 bg-blue-50 p-2 rounded mt-1">
                          {previewTemplate(template.content)}
                        </p>
                      </div>
                      
                      <p className="text-xs text-gray-500">
                        Creada: {new Date(template.created_at).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditDialog(template)}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openDeleteDialog(template)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Eliminar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Tag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No hay plantillas</h3>
              <p>Crea tu primera plantilla para empezar a enviar recordatorios personalizados.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Template Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Crear Nueva Plantilla</DialogTitle>
            <DialogDescription>
              Crea una plantilla personalizada para tus mensajes de recordatorio
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Template Name */}
            <div>
              <Label htmlFor="name">Nombre de la Plantilla</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ej: Recordatorio Cita Urgente"
              />
            </div>

            {/* Quick Insert Variables */}
            <div>
              <Label className="text-sm font-medium">Insertar Variables Rápidas:</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {availableVariables.map(variable => (
                  <Button
                    key={variable.name}
                    variant="outline"
                    size="sm"
                    type="button"
                    onClick={() => insertVariable(variable)}
                    className="text-xs"
                  >
                    {`{${variable.name}}`}
                  </Button>
                ))}
              </div>
            </div>
            
            {/* Template Content */}
            <div>
              <Label htmlFor="content">Contenido de la Plantilla</Label>
              <Textarea
                id="content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Hola {nombre}, te recordamos tu cita el {fecha} a las {hora}..."
                className="h-32"
              />
            </div>

            {/* Preview */}
            {formData.content && (
              <div>
                <Label className="text-sm font-medium">Vista Previa:</Label>
                <div className="p-3 bg-blue-50 rounded-lg mt-2">
                  <p className="text-sm text-gray-800">
                    {previewTemplate(formData.content)}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={loading}>
              {loading ? 'Creando...' : 'Crear Plantilla'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Template Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Plantilla</DialogTitle>
            <DialogDescription>
              Modifica la plantilla existente
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Template Name */}
            <div>
              <Label htmlFor="edit-name">Nombre de la Plantilla</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ej: Recordatorio Cita Urgente"
              />
            </div>

            {/* Quick Insert Variables */}
            <div>
              <Label className="text-sm font-medium">Insertar Variables Rápidas:</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {availableVariables.map(variable => (
                  <Button
                    key={variable.name}
                    variant="outline"
                    size="sm"
                    type="button"
                    onClick={() => insertVariable(variable)}
                    className="text-xs"
                  >
                    {`{${variable.name}}`}
                  </Button>
                ))}
              </div>
            </div>
            
            {/* Template Content */}
            <div>
              <Label htmlFor="edit-content">Contenido de la Plantilla</Label>
              <Textarea
                id="edit-content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Hola {nombre}, te recordamos tu cita el {fecha} a las {hora}..."
                className="h-32"
              />
            </div>

            {/* Preview */}
            {formData.content && (
              <div>
                <Label className="text-sm font-medium">Vista Previa:</Label>
                <div className="p-3 bg-blue-50 rounded-lg mt-2">
                  <p className="text-sm text-gray-800">
                    {previewTemplate(formData.content)}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdate} disabled={loading}>
              {loading ? 'Actualizando...' : 'Actualizar Plantilla'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eliminar Plantilla</DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que quieres eliminar la plantilla "{selectedTemplate?.name}"? 
              Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleDelete} 
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? 'Eliminando...' : 'Eliminar Plantilla'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
const Reminders = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [appointments, setAppointments] = useState([]);
  const [selectedAppointments, setSelectedAppointments] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [loading, setLoading] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [sentReminders, setSentReminders] = useState({});

  // Format date for API
  const formatDateForAPI = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Format date for display
  const formatDateForDisplay = (date) => {
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Fetch templates from backend
  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error("Error fetching templates:", error);
      toast.error("Error cargando plantillas");
    }
  };

  // Fetch appointments for selected date
  const fetchAppointments = async (date) => {
    setLoading(true);
    try {
      const dateStr = formatDateForAPI(date);
      const response = await axios.get(`${API}/appointments/by-date?date=${dateStr}`);
      setAppointments(response.data);
      setSelectedAppointments([]); // Reset selections
    } catch (error) {
      console.error("Error fetching appointments:", error);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  // Toggle appointment selection
  const toggleAppointmentSelection = (appointmentId) => {
    setSelectedAppointments(prev => {
      if (prev.includes(appointmentId)) {
        return prev.filter(id => id !== appointmentId);
      } else {
        return [...prev, appointmentId];
      }
    });
  };

  // Select all appointments
  const selectAllAppointments = () => {
    const allIds = appointments.map(apt => apt.id);
    setSelectedAppointments(allIds);
  };

  // Deselect all appointments
  const deselectAllAppointments = () => {
    setSelectedAppointments([]);
  };

  // Send reminders
  const sendReminders = async () => {
    if (!selectedTemplate || selectedAppointments.length === 0) {
      toast.error("Selecciona una plantilla y al menos una cita");
      return;
    }

    setLoading(true);
    try {
      const template = templates.find(t => t.id === selectedTemplate);
      const selectedApts = appointments.filter(apt => selectedAppointments.includes(apt.id));

      for (const appointment of selectedApts) {
        // Personalize message
        let personalizedMessage = template.content
          .replace(/{nombre}/g, appointment.contact_name)
          .replace(/{fecha}/g, new Date(appointment.date).toLocaleDateString('es-ES'))
          .replace(/{hora}/g, appointment.time || '10:00')
          .replace(/{doctor}/g, appointment.doctor || 'Doctor')
          .replace(/{tratamiento}/g, appointment.treatment || 'Consulta')
          .replace(/{telefono}/g, appointment.phone || '')
          .replace(/{numpac}/g, appointment.patient_number || '');

        // Send message
        await axios.post(`${API}/communications/send-message`, {
          contact_id: appointment.contact_id,
          message: personalizedMessage
        });

        // Mark as sent
        setSentReminders(prev => ({
          ...prev,
          [appointment.id]: new Date().toISOString()
        }));
      }

      toast.success(`Recordatorios enviados a ${selectedApts.length} pacientes`);
      setSelectedAppointments([]);
    } catch (error) {
      console.error("Error sending reminders:", error);
      toast.error("Error enviando recordatorios");
    } finally {
      setLoading(false);
    }
  };

  // Handle CSV file upload
  const handleCsvUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      toast.success("Archivo CSV cargado correctamente");
    } else {
      toast.error("Por favor selecciona un archivo CSV válido");
    }
  };

  // Process CSV reminders
  const processCsvReminders = async () => {
    if (!csvFile || !selectedTemplate) {
      toast.error("Selecciona un archivo CSV y una plantilla");
      return;
    }

    setLoading(true);
    try {
      const text = await csvFile.text();
      const lines = text.split('\n').filter(line => line.trim());
      const header = lines[0].split(',');
      
      const template = templates.find(t => t.id === selectedTemplate);
      let processedCount = 0;

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const record = {};
        
        header.forEach((col, index) => {
          record[col.trim()] = values[index]?.trim() || '';
        });

        if (record.nombre && record.telefono) {
          // Process CSV reminder
          let message = template.content
            .replace(/{nombre}/g, record.nombre)
            .replace(/{fecha}/g, record.fecha || '')
            .replace(/{hora}/g, record.hora || '')
            .replace(/{doctor}/g, record.doctor || '')
            .replace(/{tratamiento}/g, record.tratamiento || '')
            .replace(/{telefono}/g, record.telefono || '')
            .replace(/{numpac}/g, record.numpac || '');

          console.log(`Sending CSV reminder to ${record.nombre}: ${message}`);
          processedCount++;
        }
      }

      toast.success(`Procesados ${processedCount} recordatorios del CSV`);
      setCsvFile(null);
    } catch (error) {
      console.error("Error processing CSV:", error);
      toast.error("Error procesando archivo CSV");
    } finally {
      setLoading(false);
    }
  };

  // Load appointments and templates when date changes
  useEffect(() => {
    fetchAppointments(selectedDate);
  }, [selectedDate]);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const allSelected = selectedAppointments.length === appointments.length && appointments.length > 0;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Recordatorios</h1>
        <div className="text-sm text-gray-500">
          {selectedAppointments.length} de {appointments.length} citas seleccionadas
        </div>
      </div>

      {/* Date Selection and Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Selección de Fecha y Plantilla</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Date Picker */}
          <div className="flex items-center space-x-4">
            <Label className="w-32">Fecha:</Label>
            <input
              type="date"
              value={formatDateForAPI(selectedDate)}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          {/* Template Selection */}
          <div className="flex items-center space-x-4">
            <Label className="w-32">Plantilla:</Label>
            <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Seleccionar plantilla..." />
              </SelectTrigger>
              <SelectContent>
                {templates.map(template => (
                  <SelectItem key={template.id} value={template.id}>
                    {template.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Template Preview */}
          {selectedTemplate && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <Label className="text-sm font-medium">Vista previa:</Label>
              <p className="text-sm text-gray-600 mt-1">
                {templates.find(t => t.id.toString() === selectedTemplate)?.content}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <Button
              onClick={allSelected ? deselectAllAppointments : selectAllAppointments}
              variant="outline"
              disabled={appointments.length === 0}
            >
              {allSelected ? 'Deseleccionar todas' : 'Seleccionar todas'}
            </Button>
            
            <Button
              onClick={sendReminders}
              disabled={loading || selectedAppointments.length === 0 || !selectedTemplate}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Enviando...' : `Enviar Recordatorios (${selectedAppointments.length})`}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* CSV Import Section */}
      <Card>
        <CardHeader>
          <CardTitle>Importar Recordatorios desde CSV</CardTitle>
          <CardDescription>
            Sube un archivo CSV con columnas: nombre, telefono, fecha, hora, doctor, tratamiento
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <input
              type="file"
              accept=".csv"
              onChange={handleCsvUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          
          {csvFile && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-green-600">✅ {csvFile.name}</span>
              <Button
                onClick={processCsvReminders}
                disabled={loading || !selectedTemplate}
                size="sm"
              >
                Procesar CSV
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Appointments List */}
      <Card>
        <CardHeader>
          <CardTitle>
            Citas del {formatDateForDisplay(selectedDate)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Cargando citas...</p>
            </div>
          ) : appointments.length > 0 ? (
            <div className="space-y-3">
              {appointments.map(appointment => {
                const isSelected = selectedAppointments.includes(appointment.id);
                const isSent = sentReminders[appointment.id];
                
                return (
                  <div
                    key={appointment.id}
                    className={`p-4 border rounded-lg transition-colors cursor-pointer ${
                      isSelected ? 'bg-blue-50 border-blue-200' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => toggleAppointmentSelection(appointment.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleAppointmentSelection(appointment.id)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                          {appointment.contact_name.charAt(0).toUpperCase()}
                        </div>
                        
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {appointment.contact_name}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {appointment.time || '10:00'} - {appointment.treatment || 'Consulta'}
                          </p>
                          <p className="text-xs text-gray-500">
                            Dr: {appointment.doctor || 'No asignado'} | Tel: {appointment.phone || 'No especificado'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {isSent ? (
                          <div className="flex items-center space-x-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-xs">Enviado</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-1 text-gray-400">
                            <Clock className="w-4 h-4" />
                            <span className="text-xs">Pendiente</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No hay citas</h3>
              <p>No se encontraron citas para la fecha seleccionada.</p>
            </div>
          )}
        </CardContent>
      </Card>
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
    { id: "communications", label: "Comunicaciones", icon: MessageCircle },
    { id: "reminders", label: "Recordatorios", icon: MessageSquare },
    { id: "templates", label: "Plantillas", icon: Tag },
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
      case "communications":
        return <Communications />;
      case "reminders":
        return <Reminders />;
      case "templates":
        return <Templates />;
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