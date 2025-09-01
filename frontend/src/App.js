import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Calendar, MessageCircle, Users, BarChart3, Settings, Plus, Phone, Mail, MessageSquare, Clock, CheckCircle, XCircle, Search, Filter, Tag, Menu, X, Bot, Brain, Smartphone, Monitor, Zap, Eye, EyeOff, RefreshCw, Database, FileText, Shield, UserPlus, UserCheck } from "lucide-react";
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
import SettingsContent from "./components/ui/settings";
import VoiceAssistantWidget from "./components/VoiceAssistantWidget";
import WhatsAppManager from "./components/WhatsAppManager";
import GesdenManagement from './components/ui/gesden-management';
import ConsentManagement from './components/ui/consent-management';
import AIAutomations from './components/ui/ai-automations';

// API Configuration
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Authentication Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Login Component
const Login = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!credentials.username || !credentials.password) {
      toast.error("Por favor ingresa usuario y contraseña");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      
      if (response.data.success) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user_data', JSON.stringify(response.data.user));
        onLogin(response.data.user, response.data.token);
        toast.success("Bienvenido al sistema");
      } else {
        toast.error(response.data.message || "Credenciales incorrectas");
      }
    } catch (error) {
      console.error("Login error:", error);
      toast.error("Error de conexión. Intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          <CardHeader className="text-center pb-8">
            {/* Logo */}
            <div className="mb-6">
              <img 
                src="https://customer-assets.emergentagent.com/job_omnidesk-2/artifacts/tckikfmy_Logo%20blanco.jpeg"
                alt="Rubio García Dental"
                className="w-16 h-16 mx-auto rounded-xl bg-blue-600 p-3"
              />
            </div>
            
            <CardTitle className="text-2xl font-bold text-gray-900">
              RUBIO GARCÍA DENTAL
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              Sistema de Gestión Dental
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="username" className="text-sm font-medium text-gray-700">
                  Usuario
                </Label>
                <Input
                  id="username"
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                  placeholder="Ingresa tu usuario"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={loading}
                />
              </div>
              
              <div>
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Contraseña
                </Label>
                <div className="relative mt-1">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={credentials.password}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    placeholder="Ingresa tu contraseña"
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Iniciando sesión...</span>
                  </div>
                ) : (
                  "Iniciar Sesión"
                )}
              </Button>
            </form>
            
            <div className="mt-6 text-center text-xs text-gray-500">
              <p>Sistema seguro para la gestión de pacientes y citas</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Auth Provider Component  
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on app start
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user_data');

      if (storedToken && storedUser) {
        try {
          // Verify token is still valid
          const response = await axios.get(`${API}/auth/verify?token=${storedToken}`);
          
          if (response.data.valid) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          } else {
            // Token expired or invalid
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
          }
        } catch (error) {
          console.error("Auth verification error:", error);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
        }
      }
      
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API}/auth/logout`, { token });
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      setUser(null);
      setToken(null);
    }
  };

  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!user && !!token
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

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

// Enhanced Conversations Component with detailed summaries
const PendingConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState("conversations");

  useEffect(() => {
    fetchPendingData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchPendingData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPendingData = async () => {
    try {
      const [conversationsRes, tasksRes] = await Promise.all([
        axios.get(`${API}/conversations/pending`),
        axios.get(`${API}/dashboard/tasks?status=pending`)
      ]);
      setConversations(conversationsRes.data);
      setTasks(tasksRes.data);
    } catch (error) {
      console.error("Error fetching pending data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (color) => {
    const colors = {
      red: "bg-red-500",
      black: "bg-gray-800", 
      yellow: "bg-yellow-500",
      gray: "bg-gray-400",
      green: "bg-green-500"
    };
    return colors[color] || colors.gray;
  };

  const getUrgencyLabel = (color) => {
    const labels = {
      red: "URGENTE",
      black: "ALTA", 
      yellow: "MEDIA",
      gray: "BAJA",
      green: "RESUELTA"
    };
    return labels[color] || "NORMAL";
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: "text-red-600 bg-red-50",
      medium: "text-yellow-600 bg-yellow-50", 
      low: "text-green-600 bg-green-50"
    };
    return colors[priority] || colors.medium;
  };

  const markAsResolved = async (conversationId) => {
    try {
      await axios.put(`${API}/conversations/${conversationId}/status`, {
        urgency_color: "green",
        pending_response: false
      });
      fetchPendingData(); // Refresh data
      toast.success("Conversación marcada como resuelta");
    } catch (error) {
      console.error("Error updating conversation:", error);
      toast.error("Error al actualizar conversación");
    }
  };

  const markTaskCompleted = async (taskId) => {
    try {
      await axios.put(`${API}/dashboard/tasks/${taskId}`, {
        status: "completed"
      });
      fetchPendingData(); // Refresh data
      toast.success("Tarea marcada como completada");
    } catch (error) {
      console.error("Error updating task:", error);
      toast.error("Error al actualizar tarea");
    }
  };

  const formatTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return "Hace menos de 1h";
    if (diffInHours < 24) return `Hace ${diffInHours}h`;
    const days = Math.floor(diffInHours / 24);
    return `Hace ${days} día${days > 1 ? 's' : ''}`;
  };

  const truncateText = (text, maxLength = 60) => {
    if (!text) return "";
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            Mensajes y Tareas Pendientes
          </CardTitle>
          <div className="flex space-x-1">
            <Button
              variant={selectedTab === "conversations" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedTab("conversations")}
            >
              Mensajes ({conversations.length})
            </Button>
            <Button
              variant={selectedTab === "tasks" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedTab("tasks")}
            >
              Tareas ({tasks.length})
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {selectedTab === "conversations" ? (
              conversations.length === 0 ? (
                <div className="text-center text-gray-500 py-4">
                  <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
                  <p className="text-sm">No hay conversaciones pendientes</p>
                </div>
              ) : (
                conversations.map((conv) => (
                  <div key={conv.id} className="border-l-4 border-red-400 bg-gray-50 p-3 rounded-r">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getUrgencyColor(conv.color_code)}`}></div>
                        <span className="font-medium text-gray-900">{conv.patient_name}</span>
                        <Badge className={`text-xs ${getUrgencyColor(conv.color_code)} text-white`}>
                          {getUrgencyLabel(conv.color_code)}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">{formatTimeAgo(conv.created_at)}</span>
                    </div>
                    
                    <div className="mb-2">
                      <p className="text-sm text-gray-700 mb-1">
                        <strong>Resumen:</strong> {truncateText(conv.description)}
                      </p>
                      {conv.pain_level && (
                        <div className="flex items-center space-x-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            Nivel de dolor: {conv.pain_level}/10
                          </Badge>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <Phone className="w-3 h-3" />
                        <span>{conv.patient_phone}</span>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => markAsResolved(conv.id)}
                        className="text-xs hover:bg-green-100 hover:text-green-700"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Resolver
                      </Button>
                    </div>
                  </div>
                ))
              )
            ) : (
              tasks.length === 0 ? (
                <div className="text-center text-gray-500 py-4">
                  <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
                  <p className="text-sm">No hay tareas pendientes</p>
                </div>
              ) : (
                tasks.map((task) => (
                  <div key={task.id} className="border rounded-lg p-3 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getUrgencyColor(task.color_code)}`}></div>
                        <span className="font-medium text-gray-900">{task.patient_name}</span>
                        <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority.toUpperCase()}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">{formatTimeAgo(task.created_at)}</span>
                    </div>
                    
                    <div className="mb-2">
                      <p className="text-sm text-gray-700 mb-1">
                        <strong>Tipo:</strong> {task.task_type.replace(/_/g, ' ').toUpperCase()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {truncateText(task.description)}
                      </p>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <Phone className="w-3 h-3" />
                        <span>{task.patient_phone}</span>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => markTaskCompleted(task.id)}
                        className="text-xs hover:bg-green-100 hover:text-green-700"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Completar
                      </Button>
                    </div>
                  </div>
                ))
              )
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// PWA Install Button Component
const PWAInstallButton = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstall, setShowInstall] = useState(false);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstall(true);
    };

    window.addEventListener('beforeinstallprompt', handler);
    
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      toast.success('¡App instalada correctamente!');
    }
    
    setDeferredPrompt(null);
    setShowInstall(false);
  };

  if (!showInstall) return null;

  return (
    <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-800">Instalar App</h3>
            <p className="text-sm text-blue-600">Acceso rápido al asistente de voz</p>
          </div>
        </div>
        <Button onClick={handleInstall} className="bg-blue-500 hover:bg-blue-600">
          Instalar
        </Button>
      </div>
    </div>
  );
};

// Calendar Component for Dashboard
const DashboardCalendar = ({ onDateSelect, selectedDate }) => {
  // Initialize with September 2025 (current month)
  const [currentMonth, setCurrentMonth] = useState(new Date(2025, 8, 1)); // September 2025

  const monthNames = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
  ];

  const weekDays = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay(); // 0 = Sunday, 1 = Monday, etc.

    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const isToday = (date) => {
    if (!date) return false;
    // Since today is Monday, September 1st, 2025
    const today = new Date(2025, 8, 1); // September 1st, 2025
    return date && 
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear();
  };

  const isSelected = (date) => {
    return date && selectedDate &&
      date.getDate() === selectedDate.getDate() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getFullYear() === selectedDate.getFullYear();
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const days = getDaysInMonth(currentMonth);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Calendario</CardTitle>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={prevMonth}>
              ←
            </Button>
            <span className="text-sm font-medium min-w-[120px] text-center">
              {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
            </span>
            <Button variant="outline" size="sm" onClick={nextMonth}>
              →
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-1 mb-2">
          {weekDays.map(day => (
            <div key={day} className="text-xs font-medium text-gray-500 text-center p-2">
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => (
            <button
              key={index}
              onClick={() => day && onDateSelect(day)}
              className={`
                p-2 text-sm rounded hover:bg-blue-50 transition-colors
                ${!day ? 'invisible' : ''}
                ${isToday(day) ? 'bg-blue-100 font-bold text-blue-700 ring-2 ring-blue-300' : ''}
                ${isSelected(day) ? 'bg-blue-500 text-white' : ''}
                ${day && !isSelected(day) && !isToday(day) ? 'hover:bg-gray-100' : ''}
              `}
              disabled={!day}
            >
              {day?.getDate()}
            </button>
          ))}
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Hoy: Lunes, 1 de Septiembre de 2025
        </div>
      </CardContent>
    </Card>
  );
};

// Daily Appointments Component
const DailyAppointments = ({ selectedDate }) => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    if (selectedDate) {
      fetchAppointments();
    }
  }, [selectedDate]);

  const fetchAppointments = async () => {
    if (!selectedDate) return;
    
    setLoading(true);
    try {
      const formattedDate = selectedDate.toISOString().split('T')[0];
      console.log('Fetching appointments for date:', formattedDate);
      console.log('API URL:', `${API}/appointments/by-date?date=${formattedDate}`);
      
      const response = await axios.get(`${API}/appointments/by-date?date=${formattedDate}`);
      console.log('Appointments response:', response.data);
      console.log('Number of appointments:', response.data ? response.data.length : 0);
      
      setAppointments(response.data || []);
    } catch (error) {
      console.error("Error fetching appointments:", error);
      console.error("API endpoint:", `${API}/appointments/by-date?date=${selectedDate.toISOString().split('T')[0]}`);
      toast.error("Error cargando citas");
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return "";
    return timeStr.substring(0, 5); // "HH:MM"
  };

  const getStatusColor = (status) => {
    const colors = {
      scheduled: "bg-blue-100 text-blue-800",
      confirmed: "bg-green-100 text-green-800", 
      completed: "bg-gray-100 text-gray-800",
      cancelled: "bg-red-100 text-red-800"
    };
    return colors[status] || colors.scheduled;
  };

  const getStatusText = (status) => {
    const texts = {
      scheduled: "Programada",
      confirmed: "Confirmada",
      completed: "Completada", 
      cancelled: "Cancelada"
    };
    return texts[status] || status;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          Citas del {selectedDate ? selectedDate.toLocaleDateString('es-ES', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          }) : 'día seleccionado'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>
        ) : !appointments || appointments.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Calendar className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">No hay citas programadas para este día</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {appointments.map((appointment) => (
              <div key={appointment.id} className="border rounded-lg p-3 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{appointment.contact_name}</h4>
                    <p className="text-sm text-gray-600">{appointment.treatment}</p>
                  </div>
                  <Badge className={`${getStatusColor(appointment.status)}`}>
                    {getStatusText(appointment.status)}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {formatTime(appointment.time)}
                    </span>
                    {appointment.doctor && (
                      <span>{appointment.doctor}</span>
                    )}
                  </div>
                  {appointment.phone && (
                    <span className="flex items-center">
                      <Phone className="w-3 h-3 mr-1" />
                      {appointment.phone}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Statistics Charts Component
const StatisticsCharts = ({ stats }) => {
  // Calculate percentages for pie charts
  const totalMessages = stats?.pending_messages + stats?.ai_conversations + 10; // +10 for resolved messages
  const messageData = [
    { name: 'Pendientes', value: stats?.pending_messages || 0, color: '#ef4444' },
    { name: 'IA Activos', value: stats?.ai_conversations || 0, color: '#3b82f6' },
    { name: 'Resueltos', value: 10, color: '#10b981' }
  ];

  const appointmentData = [
    { name: 'Hoy', value: stats?.today_appointments || 0, color: '#10b981' },
    { name: 'Próximas', value: Math.max((stats?.total_appointments || 0) - (stats?.today_appointments || 0), 0), color: '#3b82f6' }
  ];

  const createPieChart = (data, size = 120) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    if (total === 0) return null;

    let cumulativePercentage = 0;
    const radius = size / 2 - 10;
    const centerX = size / 2;
    const centerY = size / 2;

    return (
      <svg width={size} height={size} className="transform -rotate-90">
        {data.map((item, index) => {
          const percentage = (item.value / total) * 100;
          const startAngle = (cumulativePercentage / 100) * 2 * Math.PI;
          const endAngle = ((cumulativePercentage + percentage) / 100) * 2 * Math.PI;
          
          const x1 = centerX + radius * Math.cos(startAngle);
          const y1 = centerY + radius * Math.sin(startAngle);
          const x2 = centerX + radius * Math.cos(endAngle);
          const y2 = centerY + radius * Math.sin(endAngle);
          
          const largeArcFlag = percentage > 50 ? 1 : 0;
          
          const pathData = [
            `M ${centerX} ${centerY}`,
            `L ${x1} ${y1}`,
            `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
            'Z'
          ].join(' ');
          
          cumulativePercentage += percentage;
          
          return (
            <path
              key={index}
              d={pathData}
              fill={item.color}
              stroke="white"
              strokeWidth="2"
            />
          );
        })}
      </svg>
    );
  };

  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Estado de Mensajes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              {messageData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm">{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
            <div className="flex-shrink-0">
              {createPieChart(messageData)}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Estado de Citas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              {appointmentData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm">{item.name}: {item.value}</span>
                </div>
              ))}
              <div className="text-xs text-gray-500 mt-2">
                {stats?.total_appointments ? 
                  `${((stats.today_appointments / stats.total_appointments) * 100).toFixed(1)}% confirmadas hoy` :
                  'Sin datos suficientes'
                }
              </div>
            </div>
            <div className="flex-shrink-0">
              {createPieChart(appointmentData)}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date(2025, 8, 1)); // September 1st, 2025 (today)

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
          <Button variant="outline" size="sm" onClick={fetchDashboardStats}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
        </div>
      </div>

      {/* PWA Install Prompt */}
      <PWAInstallButton />

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

      {/* Calendar and Daily Appointments */}
      <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
        <DashboardCalendar 
          selectedDate={selectedDate} 
          onDateSelect={setSelectedDate} 
        />
        <DailyAppointments selectedDate={selectedDate} />
      </div>

      {/* Statistics Charts */}
      <StatisticsCharts stats={stats} />

      {/* Enhanced Pending Conversations */}
      <PendingConversations />

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Acciones Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            <Button className="justify-start" variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Paciente
            </Button>
            <Button className="justify-start" variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              Agendar Cita
            </Button>
            <Button className="justify-start" variant="outline">
              <Bot className="w-4 h-4 mr-2" />
              Entrenar IA
            </Button>
            <Button className="justify-start" variant="outline">
              <MessageSquare className="w-4 h-4 mr-2" />
              Enviar Recordatorio
            </Button>
          </div>
        </CardContent>
      </Card>

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
// User Management Component
const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newUser, setNewUser] = useState({
    username: '',
    role: 'viewer',
    email: '',
    permissions: []
  });

  const roles = [
    { value: 'admin', label: 'Administrador', description: 'Acceso completo al sistema' },
    { value: 'staff', label: 'Personal', description: 'Acceso a gestión de pacientes y citas' },
    { value: 'viewer', label: 'Visualizador', description: 'Solo lectura de datos básicos' },
    { value: 'readonly', label: 'Solo Lectura', description: 'Acceso completo de solo lectura' }
  ];

  const permissionCategories = [
    {
      category: 'read',
      label: 'Lectura',
      permissions: [
        { key: 'read_contacts', label: 'Ver pacientes' },
        { key: 'read_appointments', label: 'Ver citas' },
        { key: 'read_messages', label: 'Ver mensajes' },
        { key: 'read_stats', label: 'Ver estadísticas' }
      ]
    },
    {
      category: 'write', 
      label: 'Escritura',
      permissions: [
        { key: 'write_contacts', label: 'Gestionar pacientes' },
        { key: 'write_appointments', label: 'Gestionar citas' },
        { key: 'write_messages', label: 'Enviar mensajes' },
        { key: 'write_templates', label: 'Gestionar plantillas' }
      ]
    },
    {
      category: 'admin',
      label: 'Administración', 
      permissions: [
        { key: 'admin_users', label: 'Gestionar usuarios' },
        { key: 'admin_settings', label: 'Configuraciones del sistema' },
        { key: 'admin_ai', label: 'Configurar IA' },
        { key: 'admin_automations', label: 'Gestionar automatizaciones' }
      ]
    }
  ];

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
      toast.error("Error cargando usuarios");
    } finally {
      setLoading(false);
    }
  };

  const createUser = async () => {
    try {
      await axios.post(`${API}/users`, newUser);
      toast.success("Usuario creado exitosamente");
      setShowCreateDialog(false);
      setNewUser({ username: '', role: 'viewer', email: '', permissions: [] });
      fetchUsers();
    } catch (error) {
      console.error("Error creating user:", error);
      toast.error("Error al crear usuario");
    }
  };

  const updateUser = async () => {
    try {
      await axios.put(`${API}/users/${selectedUser.id}`, selectedUser);
      toast.success("Usuario actualizado exitosamente");
      setShowEditDialog(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (error) {
      console.error("Error updating user:", error);
      toast.error("Error al actualizar usuario");
    }
  };

  const getRoleColor = (role) => {
    const colors = {
      admin: "bg-red-100 text-red-800",
      staff: "bg-blue-100 text-blue-800",
      viewer: "bg-yellow-100 text-yellow-800",
      readonly: "bg-gray-100 text-gray-800"
    };
    return colors[role] || colors.viewer;
  };

  const getRoleLabel = (role) => {
    const roleObj = roles.find(r => r.value === role);
    return roleObj ? roleObj.label : role;
  };

  const defaultPermissionsByRole = {
    admin: ['read_contacts', 'read_appointments', 'read_messages', 'read_stats', 'write_contacts', 'write_appointments', 'write_messages', 'write_templates', 'admin_users', 'admin_settings', 'admin_ai', 'admin_automations'],
    staff: ['read_contacts', 'read_appointments', 'read_messages', 'read_stats', 'write_contacts', 'write_appointments', 'write_messages', 'write_templates'],
    viewer: ['read_contacts', 'read_appointments', 'read_messages', 'read_stats'],
    readonly: ['read_contacts', 'read_appointments', 'read_messages', 'read_stats']
  };

  const handleRoleChange = (role, isNewUser = false) => {
    const permissions = defaultPermissionsByRole[role] || [];
    if (isNewUser) {
      setNewUser({ ...newUser, role, permissions });
    } else {
      setSelectedUser({ ...selectedUser, role, permissions });
    }
  };

  return (
    <div className="space-y-4 lg:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">Gestión de Usuarios</h1>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="w-4 h-4 mr-2" />
              Nuevo Usuario
            </Button>
          </DialogTrigger>
          <DialogContent className="w-full max-w-lg mx-4">
            <DialogHeader>
              <DialogTitle>Crear Nuevo Usuario</DialogTitle>
              <DialogDescription>
                Agrega un nuevo usuario al sistema con permisos específicos
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="new_username">Nombre de Usuario *</Label>
                <Input
                  id="new_username"
                  value={newUser.username}
                  onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                  placeholder="nombre_usuario"
                />
              </div>
              <div>
                <Label htmlFor="new_email">Email</Label>
                <Input
                  id="new_email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  placeholder="usuario@ejemplo.com"
                />
              </div>
              <div>
                <Label htmlFor="new_role">Rol</Label>
                <Select value={newUser.role} onValueChange={(role) => handleRoleChange(role, true)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.value} value={role.value}>
                        <div className="flex flex-col">
                          <span className="font-medium">{role.label}</span>
                          <span className="text-xs text-gray-500">{role.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={createUser} disabled={!newUser.username}>
                Crear Usuario
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Users List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : users.length > 0 ? (
          users.map((user) => (
            <Card key={user.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                    <Shield className="w-5 h-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-slate-900">{user.username}</h3>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 text-sm text-slate-500 gap-1 sm:gap-0">
                      {user.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="w-3 h-3 flex-shrink-0" />
                          <span className="truncate">{user.email}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <UserCheck className="w-3 h-3 flex-shrink-0" />
                        <span>{user.permissions?.length || 0} permisos</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between lg:justify-end space-x-2">
                  <Badge className={`${getRoleColor(user.role)} text-xs flex-shrink-0`}>
                    {getRoleLabel(user.role)}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedUser(user);
                      setShowEditDialog(true);
                    }}
                  >
                    Editar
                  </Button>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card className="p-8 text-center">
            <Shield className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-600 mb-2">No hay usuarios</h3>
            <p className="text-slate-500">Crea el primer usuario para comenzar.</p>
          </Card>
        )}
      </div>

      {/* Edit User Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar Usuario: {selectedUser?.username}</DialogTitle>
            <DialogDescription>
              Modifica los permisos y configuración del usuario
            </DialogDescription>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit_email">Email</Label>
                <Input
                  id="edit_email"
                  type="email"
                  value={selectedUser.email || ''}
                  onChange={(e) => setSelectedUser({...selectedUser, email: e.target.value})}
                  placeholder="usuario@ejemplo.com"
                />
              </div>
              <div>
                <Label htmlFor="edit_role">Rol</Label>
                <Select value={selectedUser.role} onValueChange={(role) => handleRoleChange(role, false)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.value} value={role.value}>
                        <div className="flex flex-col">
                          <span className="font-medium">{role.label}</span>
                          <span className="text-xs text-gray-500">{role.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Permisos Personalizados</Label>
                <div className="mt-2 space-y-4">
                  {permissionCategories.map(category => (
                    <div key={category.category} className="border rounded-lg p-3">
                      <h4 className="font-medium text-sm text-gray-900 mb-2">{category.label}</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {category.permissions.map(permission => (
                          <div key={permission.key} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={permission.key}
                              checked={selectedUser.permissions?.includes(permission.key) || false}
                              onChange={(e) => {
                                const permissions = selectedUser.permissions || [];
                                if (e.target.checked) {
                                  setSelectedUser({
                                    ...selectedUser,
                                    permissions: [...permissions, permission.key]
                                  });
                                } else {
                                  setSelectedUser({
                                    ...selectedUser,
                                    permissions: permissions.filter(p => p !== permission.key)
                                  });
                                }
                              }}
                              className="rounded border-gray-300"
                            />
                            <label htmlFor={permission.key} className="text-sm text-gray-700">
                              {permission.label}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={updateUser}>
              Actualizar Usuario
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Unified WhatsApp Communications Interface (Based on WhatsApp Business)
const UnifiedWhatsAppInterface = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [patients, setPatients] = useState([]);
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [newContactPhone, setNewContactPhone] = useState('');
  const [whatsappStatus, setWhatsappStatus] = useState({ connected: false });

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  // Fetch WhatsApp status
  const fetchWhatsAppStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      setWhatsappStatus(response.data);
    } catch (error) {
      console.error("Error fetching WhatsApp status:", error);
      setWhatsappStatus({ connected: false, status: 'error' });
    }
  };

  // Fetch all conversations
  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/conversations`);
      setConversations(response.data || []);
    } catch (error) {
      console.error("Error fetching conversations:", error);
      toast.error("Error cargando conversaciones");
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch all patients for search
  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${API}/contacts`);
      setPatients(response.data || []);
    } catch (error) {
      console.error("Error fetching patients:", error);
      setPatients([]);
    }
  };

  // Fetch messages for selected conversation
  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`${API}/conversations/${conversationId}/messages`);
      setMessages(response.data || []);
    } catch (error) {
      console.error("Error fetching messages:", error);
      toast.error("Error cargando mensajes");
      setMessages([]);
    }
  };

  // Send message to selected conversation
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || sendingMessage) return;

    setSendingMessage(true);
    try {
      const response = await axios.post(`${API}/conversations/${selectedConversation.id}/send-message`, {
        message: newMessage.trim()
      });

      if (response.data.success) {
        // Add message to local state immediately
        const newMsg = {
          id: Date.now(),
          message: newMessage.trim(),
          sender: 'clinic',
          timestamp: new Date().toISOString(),
          status: 'sent'
        };
        setMessages(prev => [...prev, newMsg]);
        setNewMessage('');
        toast.success("Mensaje enviado correctamente");
        
        // Refresh conversations to update last message
        fetchConversations();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Error enviando mensaje");
    } finally {
      setSendingMessage(false);
    }
  };

  // Start new conversation
  const startNewConversation = async () => {
    if (!newContactPhone.trim()) return;

    try {
      // Check if conversation already exists
      const existingConv = conversations.find(c => c.patient_phone === newContactPhone.trim());
      if (existingConv) {
        setSelectedConversation(existingConv);
        setShowNewConversation(false);
        setNewContactPhone('');
        return;
      }

      // Send first message to create conversation
      const response = await axios.post(`${API}/whatsapp/send`, {
        phone_number: newContactPhone.trim(),
        message: "Hola, ¿en qué podemos ayudarle?"
      });

      if (response.data.success) {
        toast.success("Nueva conversación iniciada");
        setShowNewConversation(false);
        setNewContactPhone('');
        fetchConversations(); // Refresh to show new conversation
      }
    } catch (error) {
      console.error("Error starting new conversation:", error);
      toast.error("Error iniciando conversación");
    }
  };

  // Filter conversations based on search
  const filteredConversations = conversations.filter(conv => 
    conv.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.patient_phone?.includes(searchTerm) ||
    conv.last_message?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Format time for display
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('es-ES', { 
        day: '2-digit', 
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  // Get urgency color classes
  const getUrgencyColor = (color) => {
    const colors = {
      red: "border-l-red-500 bg-red-50",
      black: "border-l-gray-800 bg-gray-100",
      yellow: "border-l-yellow-500 bg-yellow-50",
      gray: "border-l-gray-300 bg-gray-50",
      green: "border-l-green-500 bg-green-50"
    };
    return colors[color] || colors.gray;
  };

  const getUrgencyBadge = (color) => {
    const badges = {
      red: "bg-red-500 text-white",
      black: "bg-gray-800 text-white",
      yellow: "bg-yellow-500 text-white",
      gray: "bg-gray-400 text-white",
      green: "bg-green-500 text-white"
    };
    return badges[color] || badges.gray;
  };

  const getUrgencyLabel = (color) => {
    const labels = {
      red: "URGENTE",
      black: "ALTA",
      yellow: "MEDIA",
      gray: "NORMAL", 
      green: "RESUELTA"
    };
    return labels[color] || "NORMAL";
  };

  useEffect(() => {
    fetchWhatsAppStatus();
    fetchConversations();
    fetchPatients();
    
    // Refresh data periodically
    const statusInterval = setInterval(fetchWhatsAppStatus, 30000);
    const conversationsInterval = setInterval(fetchConversations, 30000);
    
    return () => {
      clearInterval(statusInterval);
      clearInterval(conversationsInterval);
    };
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id);
      // Refresh messages every 10 seconds when a conversation is selected
      const messageInterval = setInterval(() => fetchMessages(selectedConversation.id), 10000);
      return () => clearInterval(messageInterval);
    }
  }, [selectedConversation]);

  return (
    <div className="h-screen flex bg-gray-100">
      {/* Left Panel - Conversations List */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 bg-green-600 text-white">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">WhatsApp Business</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${whatsappStatus.connected ? 'bg-green-300' : 'bg-red-300'}`}></div>
              <span className="text-xs">{whatsappStatus.connected ? 'Conectado' : 'Desconectado'}</span>
            </div>
          </div>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-green-300" />
            <input
              type="text"
              placeholder="Buscar conversaciones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-green-500 text-white placeholder-green-300 rounded-lg border-0 focus:ring-2 focus:ring-green-300"
            />
          </div>
        </div>

        {/* New Conversation Button */}
        <div className="p-3 border-b border-gray-100">
          <Button 
            onClick={() => setShowNewConversation(true)}
            className="w-full bg-green-600 hover:bg-green-700 text-white"
            size="sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nueva Conversación
          </Button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p className="text-sm">
                {searchTerm ? 'No se encontraron conversaciones' : 'No hay conversaciones disponibles'}
              </p>
              <p className="text-xs mt-1 text-gray-400">
                Haz clic en "Nueva Conversación" para empezar
              </p>
            </div>
          ) : (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors border-l-4 ${
                  getUrgencyColor(conversation.urgency_color)
                } ${selectedConversation?.id === conversation.id ? 'bg-blue-50' : ''}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2 flex-1">
                    <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                      {conversation.patient_name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 truncate text-sm">
                        {conversation.patient_name || 'Usuario'}
                      </h4>
                      <p className="text-xs text-gray-500 truncate">
                        {conversation.patient_phone}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500">{formatTime(conversation.last_message_time)}</span>
                    {conversation.urgency_color !== 'gray' && conversation.urgency_color !== 'green' && (
                      <div className={`mt-1 px-1 py-0.5 rounded text-xs ${getUrgencyBadge(conversation.urgency_color)}`}>
                        {getUrgencyLabel(conversation.urgency_color)}
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 truncate mb-1">
                  {conversation.last_message || 'Sin mensajes'}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{conversation.message_count || 0} mensajes</span>
                  {conversation.pending_response && (
                    <div className="flex items-center text-orange-600">
                      <Clock className="w-3 h-3 mr-1" />
                      <span>Pendiente</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Center Panel - Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="p-4 bg-white border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {selectedConversation.patient_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {selectedConversation.patient_name || 'Usuario'}
                    </h3>
                    <p className="text-sm text-gray-600">{selectedConversation.patient_phone}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Phone className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Search className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-sm">No hay mensajes en esta conversación</p>
                  <p className="text-xs text-gray-400 mt-1">Envía el primer mensaje para comenzar</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'clinic' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.sender === 'clinic'
                          ? 'bg-green-600 text-white'
                          : 'bg-white border border-gray-200 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{message.message}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'clinic' ? 'text-green-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                        {message.sender === 'clinic' && (
                          <span className="ml-2">
                            {message.status === 'sent' ? '✓' : '⏳'}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Escriba su mensaje..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  disabled={sendingMessage || !whatsappStatus.connected}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!newMessage.trim() || sendingMessage || !whatsappStatus.connected}
                  className="bg-green-600 hover:bg-green-700 text-white rounded-full px-6"
                >
                  {sendingMessage ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">Bienvenido a WhatsApp Business</h3>
              <p className="text-sm">Selecciona una conversación para comenzar a chatear</p>
              <p className="text-xs text-gray-400 mt-2">
                También puedes iniciar una nueva conversación con un paciente
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Right Panel - Contact Info */}
      {selectedConversation && (
        <div className="w-80 bg-white border-l border-gray-200 p-4">
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-2xl mx-auto mb-3">
              {selectedConversation.patient_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <h3 className="font-semibold text-lg text-gray-900">
              {selectedConversation.patient_name || 'Usuario'}
            </h3>
            <p className="text-gray-600">{selectedConversation.patient_phone}</p>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Estado de Urgencia</h4>
              <div className={`inline-flex px-3 py-1 rounded-full text-sm ${getUrgencyBadge(selectedConversation.urgency_color)}`}>
                {getUrgencyLabel(selectedConversation.urgency_color)}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Información de Contacto</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Phone className="w-4 h-4" />
                  <span>{selectedConversation.patient_phone}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MessageCircle className="w-4 h-4" />
                  <span>{selectedConversation.message_count || 0} mensajes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>Última actividad: {formatTime(selectedConversation.last_message_time)}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Acciones Rápidas</h4>
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Calendar className="w-4 h-4 mr-2" />
                  Agendar Cita
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <FileText className="w-4 h-4 mr-2" />
                  Enviar Consentimiento
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Plantillas
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Conversation Dialog */}
      {showNewConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Nueva Conversación</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Número de teléfono
                </label>
                <input
                  type="text"
                  value={newContactPhone}
                  onChange={(e) => setNewContactPhone(e.target.value)}
                  placeholder="+34 XXX XXX XXX"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Introduce el número con código de país (ej: +34648085696)
                </p>
              </div>
              
              <div className="flex space-x-3">
                <Button
                  onClick={() => {
                    setShowNewConversation(false);
                    setNewContactPhone('');
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={startNewConversation}
                  disabled={!newContactPhone.trim()}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  Iniciar Chat
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Agenda Component
const Agenda = () => {
  const [selectedDate, setSelectedDate] = useState(new Date()); // Current date by default
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(null); // Track which appointment is being updated
  const [syncStatus, setSyncStatus] = useState({ pending: 0, lastSync: null });

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
    fetchSyncStatus();
  }, [selectedDate]);

  // Fetch sync status
  const fetchSyncStatus = async () => {
    try {
      const response = await axios.get(`${API}/sync/sheets/status`);
      setSyncStatus(response.data);
    } catch (error) {
      console.error("Error fetching sync status:", error);
    }
  };

  // Update appointment status
  const updateAppointmentStatus = async (appointmentId, newStatus) => {
    setUpdating(appointmentId);
    try {
      await axios.put(`${API}/appointments/${appointmentId}`, {
        status: newStatus
      });
      
      toast.success(`Estado actualizado a ${getStatusDisplay(newStatus).text}`);
      
      // Refresh appointments and sync status
      await fetchAppointments(selectedDate);
      await fetchSyncStatus();
      
    } catch (error) {
      console.error("Error updating appointment:", error);
      toast.error("Error al actualizar el estado de la cita");
    } finally {
      setUpdating(null);
    }
  };

  // Sync all pending changes to Google Sheets
  const syncAllToSheets = async () => {
    try {
      const response = await axios.post(`${API}/sync/sheets/all`);
      toast.success("Cambios sincronizados con Google Sheets");
      await fetchSyncStatus();
    } catch (error) {
      console.error("Error syncing to sheets:", error);
      toast.error("Error al sincronizar con Google Sheets");
    }
  };

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
            <div>
              <span>Citas para {formatDateForDisplay(selectedDate)}</span>
              <div className="text-sm font-normal text-gray-500 mt-1">
                {appointments.length} cita{appointments.length !== 1 ? 's' : ''}
                {syncStatus.pending > 0 && (
                  <span className="ml-2 text-orange-600">
                    • {syncStatus.pending} cambio{syncStatus.pending !== 1 ? 's' : ''} pendiente{syncStatus.pending !== 1 ? 's' : ''} de sincronizar
                  </span>
                )}
              </div>
            </div>
            {syncStatus.pending > 0 && (
              <Button
                onClick={syncAllToSheets}
                size="sm"
                className="bg-blue-500 hover:bg-blue-600"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Sincronizar con Google Sheets
              </Button>
            )}
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
                      <div className="flex flex-wrap gap-2">
                        <button 
                          onClick={() => updateAppointmentStatus(appointment.id, 'scheduled')}
                          disabled={updating === appointment.id || appointment.status === 'scheduled'}
                          className={`px-3 py-1 text-xs rounded-full transition-colors ${
                            appointment.status === 'scheduled' 
                              ? 'bg-blue-200 text-blue-800' 
                              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                          } ${updating === appointment.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {updating === appointment.id ? '⏳' : '📅'} Planificada
                        </button>
                        <button 
                          onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                          disabled={updating === appointment.id || appointment.status === 'confirmed'}
                          className={`px-3 py-1 text-xs rounded-full transition-colors ${
                            appointment.status === 'confirmed' 
                              ? 'bg-green-200 text-green-800' 
                              : 'bg-green-100 text-green-700 hover:bg-green-200'
                          } ${updating === appointment.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {updating === appointment.id ? '⏳' : '✅'} Confirmada
                        </button>
                        <button 
                          onClick={() => updateAppointmentStatus(appointment.id, 'completed')}
                          disabled={updating === appointment.id || appointment.status === 'completed'}
                          className={`px-3 py-1 text-xs rounded-full transition-colors ${
                            appointment.status === 'completed' 
                              ? 'bg-gray-200 text-gray-800' 
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          } ${updating === appointment.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {updating === appointment.id ? '⏳' : '✔️'} Completada
                        </button>
                        <button 
                          onClick={() => updateAppointmentStatus(appointment.id, 'cancelled')}
                          disabled={updating === appointment.id || appointment.status === 'cancelled'}
                          className={`px-3 py-1 text-xs rounded-full transition-colors ${
                            appointment.status === 'cancelled' 
                              ? 'bg-red-200 text-red-800' 
                              : 'bg-red-100 text-red-700 hover:bg-red-200'
                          } ${updating === appointment.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {updating === appointment.id ? '⏳' : '❌'} Cancelada
                        </button>
                      </div>
                      
                      {/* Sync indicator */}
                      {appointment.synced_to_sheets === false && (
                        <p className="text-xs text-orange-600 mt-2 flex items-center">
                          <RefreshCw className="w-3 h-3 mr-1" />
                          Cambio pendiente de sincronizar con Google Sheets
                        </p>
                      )}
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

// Templates Component with Consent Message Templates
const Templates = () => {
  const [templates, setTemplates] = useState([]);
  const [consentMessageTemplates, setConsentMessageTemplates] = useState([]);
  const [consentMessageSettings, setConsentMessageSettings] = useState([]);
  const [activeTab, setActiveTab] = useState('reminder-templates');
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    content: '',
    variables: []
  });

  const availableVariables = [
    { name: 'nombre', description: 'Nombre del paciente', example: 'María García' },
    { name: 'fecha', description: 'Fecha de la cita', example: '15/03/2024' },
    { name: 'hora', description: 'Hora de la cita', example: '10:30' },
    { name: 'doctor', description: 'Nombre del doctor', example: 'Dr. Rubio' },
    { name: 'tratamiento', description: 'Tipo de tratamiento', example: 'Limpieza dental' },
    { name: 'clinica', description: 'Nombre de la clínica', example: 'Rubio García Dental' },
    { name: 'telefono', description: 'Teléfono de la clínica', example: '916 410 841' },
    { name: 'direccion', description: 'Dirección de la clínica', example: 'Calle Mayor 19, Alcorcón' }
  ];

  const consentTemplateTypes = [
    { value: 'appointment_confirmation', label: 'Confirmación de Cita', description: 'Mensajes para confirmar citas con botones interactivos' },
    { value: 'consent_form', label: 'Formulario de Consentimiento', description: 'Mensajes para enviar consentimientos informados' },
    { value: 'lopd_consent', label: 'Consentimiento LOPD', description: 'Mensajes para protección de datos' },
    { value: 'survey_invite', label: 'Invitación a Encuesta', description: 'Mensajes para encuestas de primera visita' }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch reminder templates
      const templatesResponse = await axios.get(`${API}/templates`);
      setTemplates(templatesResponse.data);

      // Fetch consent message templates
      const consentTemplatesResponse = await axios.get(`${API}/consent-message-templates`);
      setConsentMessageTemplates(consentTemplatesResponse.data);

      // Fetch consent message settings
      const settingsResponse = await axios.get(`${API}/consent-message-settings`);
      setConsentMessageSettings(settingsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Error cargando plantillas');
    } finally {
      setLoading(false);
    }
  };

  const previewTemplate = (content) => {
    let preview = content;
    availableVariables.forEach(variable => {
      const regex = new RegExp(`{${variable.name}}`, 'g');
      preview = preview.replace(regex, variable.example);
    });
    return preview;
  };

  const handleCreateTemplate = async () => {
    try {
      await axios.post(`${API}/templates`, newTemplate);
      toast.success('Plantilla creada exitosamente');
      setNewTemplate({ name: '', content: '', variables: [] });
      setShowCreateDialog(false);
      fetchData();
    } catch (error) {
      console.error('Error creating template:', error);
      toast.error('Error creando plantilla');
    }
  };

  const handleUpdateTemplate = async () => {
    try {
      await axios.put(`${API}/templates/${selectedTemplate.id}`, selectedTemplate);
      toast.success('Plantilla actualizada exitosamente');
      setShowEditDialog(false);
      setSelectedTemplate(null);
      fetchData();
    } catch (error) {
      console.error('Error updating template:', error);
      toast.error('Error actualizando plantilla');
    }
  };

  const handleDeleteTemplate = async () => {
    try {
      await axios.delete(`${API}/templates/${selectedTemplate.id}`);
      toast.success('Plantilla eliminada exitosamente');
      setShowDeleteDialog(false);
      setSelectedTemplate(null);
      fetchData();
    } catch (error) {
      console.error('Error deleting template:', error);
      toast.error('Error eliminando plantilla');
    }
  };

  const toggleConsentTemplate = async (templateId) => {
    try {
      const response = await axios.post(`${API}/consent-message-templates/${templateId}/toggle`);
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      console.error('Error toggling template:', error);
      toast.error('Error cambiando estado de plantilla');
    }
  };

  const updateConsentSetting = async (settingName, value) => {
    try {
      await axios.put(`${API}/consent-message-settings/${settingName}`, {
        setting_value: value
      });
      toast.success('Configuración actualizada');
      fetchData();
    } catch (error) {
      console.error('Error updating setting:', error);
      toast.error('Error actualizando configuración');
    }
  };

  const openEditDialog = (template) => {
    setSelectedTemplate({ ...template });
    setShowEditDialog(true);
  };

  const openDeleteDialog = (template) => {
    setSelectedTemplate(template);
    setShowDeleteDialog(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gestión de Plantillas</h1>
          <p className="text-gray-600 mt-2">Administra plantillas de mensajes y configuraciones de consentimiento</p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="reminder-templates">Plantillas de Recordatorios</TabsTrigger>
          <TabsTrigger value="consent-templates">Mensajes de Consentimiento</TabsTrigger>
          <TabsTrigger value="consent-settings">Configuración</TabsTrigger>
        </TabsList>

        {/* Reminder Templates Tab */}
        <TabsContent value="reminder-templates" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Plantillas de Recordatorios</h2>
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
                <div className="text-center py-8 text-gray-500">
                  <Tag className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No hay plantillas creadas</p>
                  <p className="text-sm">Crea tu primera plantilla para comenzar</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Consent Message Templates Tab */}
        <TabsContent value="consent-templates" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Plantillas de Mensajes de Consentimiento</h2>
            <p className="text-sm text-gray-600">Gestiona los mensajes que se envían para consentimientos</p>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Cargando plantillas de consentimiento...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {consentTemplateTypes.map(type => {
                const typeTemplates = consentMessageTemplates.filter(t => t.template_type === type.value);
                
                return (
                  <Card key={type.value}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <div>
                          <h3>{type.label}</h3>
                          <p className="text-sm text-gray-600 font-normal">{type.description}</p>
                        </div>
                        <Badge variant="outline">
                          {typeTemplates.length} plantilla{typeTemplates.length !== 1 ? 's' : ''}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {typeTemplates.length > 0 ? (
                        <div className="space-y-4">
                          {typeTemplates.map(template => (
                            <div key={template.id} className="border rounded-lg p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-2">
                                    <h4 className="font-semibold">{template.template_name}</h4>
                                    {template.treatment_code && (
                                      <Badge variant="secondary">
                                        Código {template.treatment_code}
                                      </Badge>
                                    )}
                                    <Badge variant={template.is_active ? "default" : "secondary"}>
                                      {template.is_active ? "Activo" : "Inactivo"}
                                    </Badge>
                                  </div>
                                  
                                  <div className="mb-3">
                                    <Label className="text-sm font-medium text-gray-700">Mensaje:</Label>
                                    <div className="text-sm text-gray-800 bg-gray-50 p-3 rounded mt-1 whitespace-pre-wrap">
                                      {template.message_text}
                                    </div>
                                  </div>
                                  
                                  {template.variables && template.variables.length > 0 && (
                                    <div className="mb-2">
                                      <Label className="text-sm font-medium text-gray-700">Variables disponibles:</Label>
                                      <div className="flex flex-wrap gap-1 mt-1">
                                        {template.variables.map(variable => (
                                          <code key={variable} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                            {`{${variable}}`}
                                          </code>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                                
                                <div className="flex space-x-2 ml-4">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => toggleConsentTemplate(template.id)}
                                    className={template.is_active ? "text-orange-600 hover:text-orange-700" : "text-green-600 hover:text-green-700"}
                                  >
                                    {template.is_active ? "Desactivar" : "Activar"}
                                  </Button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-center py-4 text-gray-500">
                          No hay plantillas de este tipo
                        </p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>

        {/* Consent Settings Tab */}
        <TabsContent value="consent-settings" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Configuración de Consentimientos</h2>
            <p className="text-sm text-gray-600">Ajusta la configuración automática de mensajes</p>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Cargando configuración...</p>
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Configuraciones Automáticas</CardTitle>
                <CardDescription>
                  Controla el comportamiento automático del sistema de consentimientos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {consentMessageSettings.map(setting => (
                    <div key={setting.setting_name} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-semibold">{setting.description}</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {setting.setting_name}
                        </p>
                      </div>
                      <div className="ml-4">
                        {typeof setting.setting_value === 'boolean' ? (
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              className="sr-only peer"
                              checked={setting.setting_value}
                              onChange={(e) => updateConsentSetting(setting.setting_name, e.target.checked)}
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                          </label>
                        ) : (
                          <Input
                            type="number"
                            value={setting.setting_value}
                            onChange={(e) => updateConsentSetting(setting.setting_name, parseInt(e.target.value))}
                            className="w-20"
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

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
            <div>
              <Label htmlFor="name">Nombre de la Plantilla</Label>
              <Input
                id="name"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                placeholder="Ej: Recordatorio Cita Urgente"
              />
            </div>
            
            <div>
              <Label htmlFor="content">Contenido de la Plantilla</Label>
              <Textarea
                id="content"
                value={newTemplate.content}
                onChange={(e) => setNewTemplate({ ...newTemplate, content: e.target.value })}
                placeholder="Hola {nombre}, te recordamos tu cita el {fecha} a las {hora}..."
                className="h-32"
              />
            </div>

            {newTemplate.content && (
              <div>
                <Label className="text-sm font-medium">Vista Previa:</Label>
                <div className="p-3 bg-blue-50 rounded-lg mt-2">
                  <p className="text-sm text-gray-800">
                    {previewTemplate(newTemplate.content)}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreateTemplate}>
              Crear Plantilla
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
            <div>
              <Label htmlFor="edit-name">Nombre de la Plantilla</Label>
              <Input
                id="edit-name"
                value={selectedTemplate?.name || ''}
                onChange={(e) => setSelectedTemplate({ ...selectedTemplate, name: e.target.value })}
                placeholder="Ej: Recordatorio Cita Urgente"
              />
            </div>
            
            <div>
              <Label htmlFor="edit-content">Contenido de la Plantilla</Label>
              <Textarea
                id="edit-content"
                value={selectedTemplate?.content || ''}
                onChange={(e) => setSelectedTemplate({ ...selectedTemplate, content: e.target.value })}
                placeholder="Hola {nombre}, te recordamos tu cita el {fecha} a las {hora}..."
                className="h-32"
              />
            </div>

            {selectedTemplate?.content && (
              <div>
                <Label className="text-sm font-medium">Vista Previa:</Label>
                <div className="p-3 bg-blue-50 rounded-lg mt-2">
                  <p className="text-sm text-gray-800">
                    {previewTemplate(selectedTemplate.content)}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdateTemplate}>
              Actualizar Plantilla
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
              onClick={handleDeleteTemplate} 
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Eliminar Plantilla
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

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

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

  // Refresh function for contacts
  const refreshContacts = async () => {
    await fetchContacts();
    toast.success("Pacientes actualizados");
  };
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
      console.log('Reminders: Fetching appointments for date:', dateStr);
      console.log('Reminders: API URL:', `${API}/appointments/by-date?date=${dateStr}`);
      
      const response = await axios.get(`${API}/appointments/by-date?date=${dateStr}`);
      console.log('Reminders: Appointments response:', response.data);
      console.log('Reminders: Number of appointments:', response.data ? response.data.length : 0);
      
      setAppointments(response.data || []);
      setSelectedAppointments([]); // Reset selections
    } catch (error) {
      console.error("Error fetching appointments:", error);
      console.error("Reminders: API endpoint:", `${API}/appointments/by-date?date=${formatDateForAPI(date)}`);
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
                {templates.find(t => t.id === selectedTemplate)?.content}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
            <div className="flex space-x-2">
              <Button
                onClick={allSelected ? deselectAllAppointments : selectAllAppointments}
                variant={allSelected ? "default" : "outline"}
                disabled={appointments.length === 0}
                className={allSelected ? "bg-green-600 hover:bg-green-700" : "border-blue-500 text-blue-600 hover:bg-blue-50"}
              >
                {appointments.length > 0 ? (
                  allSelected ? `✓ Todas seleccionadas (${appointments.length})` : `Seleccionar todas (${appointments.length})`
                ) : (
                  'Seleccionar todas'
                )}
              </Button>
              
              {selectedAppointments.length > 0 && (
                <Button
                  onClick={deselectAllAppointments}
                  variant="ghost"
                  className="text-gray-600 hover:text-gray-800"
                >
                  ✕ Limpiar selección
                </Button>
              )}
            </div>
            
            <div className="text-sm text-gray-600">
              {appointments.length > 0 ? (
                `${selectedAppointments.length} de ${appointments.length} citas seleccionadas`
              ) : (
                'No hay citas para esta fecha'
              )}
            </div>
          </div>
          
          <div className="flex space-x-2">
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

// Settings Component - Complete Configuration System
const SettingsPage = () => {
  const [activeConfigTab, setActiveConfigTab] = useState("clinic");
  const [clinicSettings, setClinicSettings] = useState(null);
  const [aiSettings, setAiSettings] = useState(null);
  const [automationRules, setAutomationRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testingAI, setTestingAI] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceResponse, setVoiceResponse] = useState("");
  const [testMessage, setTestMessage] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  
  // Voice recognition
  const [recognition, setRecognition] = useState(null);
  
  // Initialize voice recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'es-ES';
      
      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        handleVoiceCommand(transcript);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
      setVoiceEnabled(true);
    }
  }, []);
  
  // Fetch settings on component mount
  useEffect(() => {
    fetchAllSettings();
  }, []);
  
  const fetchAllSettings = async () => {
    setLoading(true);
    try {
      const [clinicRes, aiRes, automationRes] = await Promise.all([
        axios.get(`${API}/settings/clinic`),
        axios.get(`${API}/settings/ai`),
        axios.get(`${API}/settings/automations`)
      ]);
      
      setClinicSettings(clinicRes.data);
      setAiSettings(aiRes.data);
      setAutomationRules(automationRes.data);
    } catch (error) {
      console.error("Error fetching settings:", error);
      toast.error("Error loading settings");
    } finally {
      setLoading(false);
    }
  };

  // Available AI models
  const aiModels = [
    { value: "gpt-4o-mini", label: "GPT-4o Mini (Recomendado)", description: "Rápido y eficiente, ideal para uso general" },
    { value: "gpt-4o", label: "GPT-4o", description: "Modelo más avanzado de OpenAI" },
    { value: "claude-3-7-sonnet-20250219", label: "Claude 3.7 Sonnet", description: "Excelente para conversaciones médicas" },
    { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash", description: "Modelo de Google con capacidades avanzadas" }
  ];
  
  const modelProviders = {
    "gpt-4o-mini": "openai",
    "gpt-4o": "openai",
    "claude-3-7-sonnet-20250219": "anthropic",
    "gemini-2.0-flash": "gemini"
  };

  // Save clinic settings
  const saveClinicSettings = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/settings/clinic`, clinicSettings);
      toast.success("Configuración de clínica guardada");
    } catch (error) {
      console.error("Error saving clinic settings:", error);
      toast.error("Error guardando configuración de clínica");
    } finally {
      setLoading(false);
    }
  };
  
  // Save AI settings
  const saveAiSettings = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/settings/ai`, aiSettings);
      toast.success("Configuración de IA guardada");
    } catch (error) {
      console.error("Error saving AI settings:", error);
      toast.error("Error guardando configuración de IA");
    } finally {
      setLoading(false);
    }
  };
  
  // Voice command handler
  const handleVoiceCommand = async (transcript) => {
    setVoiceResponse("Procesando comando...");
    try {
      const response = await axios.post(`${API}/ai/voice-assistant`, {
        message: transcript,
        session_id: "settings_voice"
      });
      
      setVoiceResponse(response.data.response);
      
      // Handle specific actions
      if (response.data.action_type) {
        toast.success(`Comando detectado: ${response.data.action_type}`);
      }
      
    } catch (error) {
      console.error("Error processing voice command:", error);
      setVoiceResponse("Error procesando comando de voz");
    }
  };
  
  // Start voice recognition
  const startListening = () => {
    if (recognition && !isListening) {
      setIsListening(true);
      setVoiceResponse("Escuchando...");
      recognition.start();
    }
  };
  
  // Stop voice recognition
  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
      setIsListening(false);
    }
  };

  // Test AI functionality
  const testAI = async () => {
    if (!testMessage.trim()) {
      toast.error("Por favor escribe un mensaje de prueba");
      return;
    }

    setTestingAI(true);
    try {
      const response = await axios.post(`${API}/ai/test`, {
        message: testMessage,
        model: aiSettings.model_name,
        temperature: aiSettings.temperature,
        maxTokens: aiSettings.max_tokens,
        systemPrompt: aiSettings.system_prompt
      });

      setAiResponse(response.data.response);
      toast.success("Prueba de IA completada");
    } catch (error) {
      console.error("Error testing AI:", error);
      toast.error("Error probando IA");
      setAiResponse("Error en la conexión con IA");
    } finally {
      setTestingAI(false);
    }
  };

  // Update setting value
  const updateSetting = (category, key, value) => {
    if (category === 'ai') {
      setAiSettings(prev => ({
        ...prev,
        [key]: value
      }));
    } else if (category === 'clinic') {
      setClinicSettings(prev => ({
        ...prev,
        [key]: value
      }));
    }
  };

  const configTabs = [
    { id: "clinic", label: "Información Clínica", icon: Users },
    { id: "ai", label: "Asistente de IA", icon: Brain },
    { id: "automations", label: "Automatizaciones", icon: Zap },
    { id: "voice", label: "Asistente de Voz", icon: MessageCircle }
  ];
  
  if (loading && !clinicSettings) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Configuración</h1>
          <p className="text-gray-600 mt-2">Gestiona la información, IA y automatizaciones de tu clínica</p>
        </div>
        
        {/* Voice Assistant Button - Floating */}
        {voiceEnabled && (
          <div className="fixed bottom-6 right-6 z-50">
            <Button
              onClick={isListening ? stopListening : startListening}
              className={`w-16 h-16 rounded-full shadow-lg ${
                isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              <MessageCircle className={`w-6 h-6 ${isListening ? 'animate-pulse' : ''}`} />
            </Button>
          </div>
        )}
      </div>

      <SettingsContent 
        activeConfigTab={activeConfigTab}
        setActiveConfigTab={setActiveConfigTab}
        configTabs={configTabs}
        clinicSettings={clinicSettings}
        setClinicSettings={setClinicSettings}
        aiSettings={aiSettings}
        setAiSettings={setAiSettings}
        automationRules={automationRules}
        setAutomationRules={setAutomationRules}
        saveClinicSettings={saveClinicSettings}
        saveAiSettings={saveAiSettings}
        aiModels={aiModels}
        modelProviders={modelProviders}
        loading={loading}
        voiceEnabled={voiceEnabled}
        isListening={isListening}
        startListening={startListening}
        stopListening={stopListening}
        voiceResponse={voiceResponse}
      />
    </div>
  );
};

// Messages Component (Updated)
const Messages = () => {
  return <WhatsAppManager />;
};

// Main App Component with Authentication
function App() {
  useEffect(() => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then((registration) => {
            console.log('SW registered: ', registration);
          })
          .catch((registrationError) => {
            console.log('SW registration failed: ', registrationError);
          });
      });
    }

    // Handle PWA install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // Show install button or notification
      console.log('PWA install prompt available');
    });
  }, []);

  // Check if this is the voice assistant widget route
  const isVoiceWidget = window.location.pathname === '/voice-assistant';
  
  if (isVoiceWidget) {
    return (
      <div className="App">
        <Toaster position="top-center" />
        <VoiceAssistantWidget />
      </div>
    );
  }

  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
}

// Authenticated App Wrapper
function AuthenticatedApp() {
  const { isAuthenticated, login } = useAuth();

  if (!isAuthenticated) {
    return <Login onLogin={login} />;
  }

  return <MainDashboard />;
}

// Main Dashboard Component (Protected)
function MainDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "contacts", label: "Pacientes", icon: Users },
    { id: "agenda", label: "Agenda", icon: Calendar },
    { id: "communications", label: "Comunicaciones", icon: MessageCircle },
    { id: "whatsapp", label: "WhatsApp", icon: Smartphone },
    { id: "reminders", label: "Recordatorios", icon: MessageSquare },
    { id: "templates", label: "Plantillas", icon: Tag },
    { id: "messages", label: "WhatsApp IA", icon: MessageCircle },
    { id: "ai-training", label: "Entrenar IA", icon: Brain },
    { id: "user-management", label: "Usuarios", icon: Shield },
    { id: "consents", label: "Consentimientos", icon: FileText },
    { id: "automations", label: "Automatizaciones IA", icon: Bot },
    { id: "gesden", label: "Gestión Gesden", icon: Database },
    { id: "settings", label: "Configuración", icon: Settings }
  ];

  const handleLogout = async () => {
    await logout();
    toast.success("Sesión cerrada correctamente");
  };

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "contacts":
        return <Contacts />;
      case "agenda":
        return <Agenda />;
      case "communications":
        return <UnifiedWhatsAppInterface />;
      case "reminders":
        return <Reminders />;
      case "templates":
        return <Templates />;
      case "messages":
        return <UnifiedWhatsAppInterface />;
      case "ai-training":
        return <AITraining />;
      case "user-management":
        return <UserManagement />;
      case "consents":
        return <ConsentManagement />;
      case "automations":
        return <AIAutomations />;
      case "gesden":
        return <GesdenManagement />;
      case "settings":
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  // Mobile Menu Component
  const MobileMenu = ({ isOpen, onClose, navigationItems, activeTab, onTabChange }) => {
    return (
      <div className={`fixed inset-0 z-50 ${isOpen ? 'block' : 'hidden'}`}>
        <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
        <div className="absolute left-0 top-0 bottom-0 w-64 bg-white shadow-xl">
          <div className="p-4 border-b border-gray-200">
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
          
          <nav className="p-4 space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onTabChange(item.id);
                    onClose();
                  }}
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

          {/* User info and logout in mobile */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">@{user?.username}</p>
              </div>
              <Button size="sm" variant="outline" onClick={handleLogout}>
                Salir
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
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

            {/* User info and logout in desktop */}
            <div className="absolute bottom-0 left-0 w-64 p-4 border-t border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                  <p className="text-xs text-gray-500">@{user?.username}</p>
                </div>
                <Button size="sm" variant="outline" onClick={handleLogout}>
                  Salir
                </Button>
              </div>
            </div>
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
              <div className="flex items-center space-x-2">
                <Button size="sm" variant="outline" onClick={handleLogout}>
                  Salir
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setIsMobileMenuOpen(true)}
                >
                  <Menu className="w-5 h-5" />
                </Button>
              </div>
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
          <div className="flex-1 p-4 lg:p-8 pt-20 lg:pt-8 pb-20 lg:pb-8">
            {renderContent()}
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;