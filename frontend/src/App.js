import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Calendar, MessageCircle, Users, BarChart3, Settings, Plus, Phone, Mail, MessageSquare, Clock, CheckCircle, XCircle, Search, Filter, Tag } from "lucide-react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Panel de Control</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filtros
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700">Contactos Totales</CardTitle>
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
      </div>

      {/* Hero Section with Background Image */}
      <Card className="relative overflow-hidden bg-slate-900 text-white">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ 
            backgroundImage: 'url(https://images.unsplash.com/photo-1608222351212-18fe0ec7b13b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwyfHxidXNpbmVzcyUyMGRhc2hib2FyZHxlbnwwfHx8fDE3NTY0MjY1Nzd8MA&ixlib=rb-4.1.0&q=85)' 
          }}
        />
        <div className="relative z-10">
          <CardHeader>
            <CardTitle className="text-2xl">Gestión Omnicanal Inteligente</CardTitle>
            <CardDescription className="text-slate-300">
              Unifica todas tus conversaciones, agenda citas y automatiza tu comunicación desde un solo lugar.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-3">
              <Button variant="secondary" size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Nueva Campaña
              </Button>
              <Button variant="outline" size="sm" className="text-white border-white hover:bg-white hover:text-slate-900">
                Ver Analíticas
              </Button>
            </div>
          </CardContent>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Acciones Rápidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Contacto
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              Agendar Cita
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <MessageCircle className="w-4 h-4 mr-2" />
              Enviar Mensaje
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
                <span>Cita confirmada con María García</span>
              </div>
              <div className="flex items-center space-x-2">
                <MessageCircle className="w-4 h-4 text-blue-500" />
                <span>Nuevo mensaje de WhatsApp</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-orange-500" />
                <span>Recordatorio enviado automáticamente</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Contacts Component
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
      toast.success("Contacto creado exitosamente");
      setShowCreateDialog(false);
      setNewContact({ name: "", email: "", phone: "", whatsapp: "", notes: "", tags: [] });
      fetchContacts();
    } catch (error) {
      console.error("Error creating contact:", error);
      toast.error("Error al crear contacto");
    }
  };

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (contact.email && contact.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (contact.phone && contact.phone.includes(searchTerm))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Contactos</h1>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Contacto
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Crear Nuevo Contacto</DialogTitle>
              <DialogDescription>
                Agrega un nuevo contacto a tu lista.
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
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={createContact} disabled={!newContact.name}>
                Crear Contacto
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <div className="flex-1">
          <Input
            placeholder="Buscar contactos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
        </div>
        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-40">
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

      {/* Contacts List */}
      <div className="grid gap-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredContacts.length > 0 ? (
          filteredContacts.map((contact) => (
            <Card key={contact.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {contact.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{contact.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-slate-500">
                      {contact.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="w-3 h-3" />
                          <span>{contact.email}</span>
                        </div>
                      )}
                      {contact.phone && (
                        <div className="flex items-center space-x-1">
                          <Phone className="w-3 h-3" />
                          <span>{contact.phone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {contact.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  <Badge 
                    variant={contact.status === 'active' ? 'default' : 'secondary'}
                    className="text-xs"
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
            <h3 className="text-lg font-semibold text-slate-600 mb-2">No hay contactos</h3>
            <p className="text-slate-500">Crea tu primer contacto para comenzar.</p>
          </Card>
        )}
      </div>
    </div>
  );
};

// Appointments Component
const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API}/appointments`);
      setAppointments(response.data);
    } catch (error) {
      console.error("Error fetching appointments:", error);
      toast.error("Error loading appointments");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Citas</h1>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Nueva Cita
        </Button>
      </div>

      <Card 
        className="relative overflow-hidden"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxidXNpbmVzcyUyMGRhc2hib2FyZHxlbnwwfHx8fDE3NTY0MjY1Nzd8MA&ixlib=rb-4.1.0&q=85)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-slate-900 bg-opacity-80" />
        <CardHeader className="relative z-10 text-white">
          <CardTitle>Sistema de Citas Inteligente</CardTitle>
          <CardDescription className="text-slate-300">
            Gestiona tu agenda, envía recordatorios automáticos y mejora la puntualidad de tus clientes.
          </CardDescription>
        </CardHeader>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="text-center py-12">
          <Calendar className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">Próximamente</h3>
          <p className="text-slate-500">El calendario integrado estará disponible pronto.</p>
        </div>
      )}
    </div>
  );
};

// Messages Component
const Messages = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Mensajes</h1>
        <Button>
          <MessageCircle className="w-4 h-4 mr-2" />
          Nuevo Mensaje
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
          <CardTitle>Comunicación Omnicanal</CardTitle>
          <CardDescription className="text-slate-300">
            WhatsApp, Email, SMS y más canales unificados en una sola bandeja de entrada.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="text-center py-12">
        <MessageSquare className="w-16 h-16 text-slate-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-slate-600 mb-2">Configuración Pendiente</h3>
        <p className="text-slate-500">Conecta tus canales de comunicación para empezar.</p>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "contacts", label: "Contactos", icon: Users },
    { id: "appointments", label: "Citas", icon: Calendar },
    { id: "messages", label: "Mensajes", icon: MessageCircle },
    { id: "settings", label: "Configuración", icon: Settings }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "contacts":
        return <Contacts />;
      case "appointments":
        return <Appointments />;
      case "messages":
        return <Messages />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 bg-white shadow-sm border-r">
            <div className="p-6">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-slate-900">OmniDesk</h1>
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

          {/* Main Content */}
          <div className="flex-1 p-8">
            {renderContent()}
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;