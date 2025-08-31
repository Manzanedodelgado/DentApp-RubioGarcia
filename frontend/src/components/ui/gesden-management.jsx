import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Badge } from './badge';
import { AlertCircle, CheckCircle, Clock, Database, FileText, Phone, User, Calendar, Users, RefreshCw, Activity, Download, Upload, Settings, Eye } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = import.meta.env.VITE_API_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

const GesdenManagement = () => {
  const [gesdenStatus, setGesdenStatus] = useState(null);
  const [consentDeliveries, setConsentDeliveries] = useState([]);
  const [consentTemplates, setConsentTemplates] = useState([]);
  const [treatmentCodes, setTreatmentCodes] = useState([]);
  const [loading, setLoading] = useState({
    status: true,
    consents: true,
    templates: true,
    sync: false
  });
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [gesdenAppointments, setGesdenAppointments] = useState([]);
  const [selectedTab, setSelectedTab] = useState('status');

  // Fetch Gesden status
  const fetchGesdenStatus = async () => {
    try {
      setLoading(prev => ({ ...prev, status: true }));
      const response = await axios.get(`${API}/gesden/status`);
      setGesdenStatus(response.data);
    } catch (error) {
      console.error("Error fetching Gesden status:", error);
      toast.error("Error al obtener estado de Gesden");
    } finally {
      setLoading(prev => ({ ...prev, status: false }));
    }
  };

  // Fetch consent deliveries
  const fetchConsentDeliveries = async () => {
    try {
      setLoading(prev => ({ ...prev, consents: true }));
      const response = await axios.get(`${API}/consent-deliveries`);
      setConsentDeliveries(response.data);
    } catch (error) {
      console.error("Error fetching consent deliveries:", error);
    } finally {
      setLoading(prev => ({ ...prev, consents: false }));
    }
  };

  // Fetch consent templates  
  const fetchConsentTemplates = async () => {
    try {
      setLoading(prev => ({ ...prev, templates: true }));
      const response = await axios.get(`${API}/consent-templates`);
      setConsentTemplates(response.data);
    } catch (error) {
      console.error("Error fetching consent templates:", error);
    } finally {
      setLoading(prev => ({ ...prev, templates: false }));
    }
  };

  // Fetch treatment codes
  const fetchTreatmentCodes = async () => {
    try {
      const response = await axios.get(`${API}/treatment-codes`);
      setTreatmentCodes(response.data);
    } catch (error) {
      console.error("Error fetching treatment codes:", error);
    }
  };

  // Fetch Gesden appointments for selected date
  const fetchGesdenAppointments = async (date) => {
    try {
      const response = await axios.get(`${API}/gesden/appointments?date=${date}`);
      setGesdenAppointments(response.data);
    } catch (error) {
      console.error("Error fetching Gesden appointments:", error);
      setGesdenAppointments([]);
    }
  };

  // Trigger Gesden sync
  const triggerSync = async () => {
    try {
      setLoading(prev => ({ ...prev, sync: true }));
      const response = await axios.post(`${API}/gesden/sync`);
      toast.success("Sincronización iniciada correctamente");
      // Refresh status after a delay
      setTimeout(() => {
        fetchGesdenStatus();
      }, 2000);
    } catch (error) {
      console.error("Error triggering sync:", error);
      toast.error("Error al iniciar sincronización");
    } finally {
      setLoading(prev => ({ ...prev, sync: false }));
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'sent':
      case 'delivered':
      case 'connected':
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'pending':
      case 'running':
        return 'text-yellow-600 bg-yellow-50';
      case 'failed':
      case 'disconnected':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  // Get status text
  const getStatusText = (status) => {
    const statusMap = {
      'pending': 'Pendiente',
      'sent': 'Enviado',
      'delivered': 'Entregado',
      'failed': 'Error',
      'connected': 'Conectado',
      'disconnected': 'Desconectado',
      'running': 'Ejecutándose',
      'completed': 'Completado'
    };
    return statusMap[status] || status;
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get treatment code info
  const getTreatmentInfo = (code) => {
    const treatment = treatmentCodes.find(t => t.code === code);
    return treatment || { name: 'Desconocido', requires_consent: false };
  };

  useEffect(() => {
    fetchGesdenStatus();
    fetchConsentDeliveries();
    fetchConsentTemplates();
    fetchTreatmentCodes();
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchGesdenAppointments(selectedDate);
    }
  }, [selectedDate]);

  if (loading.status && loading.consents && loading.templates) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900">Gestión Gesden</h1>
        <Button 
          onClick={triggerSync}
          disabled={loading.sync}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {loading.sync ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          Sincronizar
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'status', label: 'Estado General', icon: Activity },
          { id: 'appointments', label: 'Citas Gesden', icon: Calendar },
          { id: 'consents', label: 'Consentimientos', icon: FileText },
          { id: 'templates', label: 'Plantillas', icon: Settings }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex-1 flex items-center justify-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedTab === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {selectedTab === 'status' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Connection Status */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  gesdenStatus?.connection_status === 'connected' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <div>
                  <p className="text-sm text-gray-600">Estado Conexión</p>
                  <p className="text-2xl font-bold">
                    {gesdenStatus?.connection_status === 'connected' ? 'Conectado' : 'Desconectado'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Total Appointments */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Database className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">Citas Gesden</p>
                  <p className="text-2xl font-bold">{gesdenStatus?.gesden_appointments || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Synced Appointments */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Sincronizadas</p>
                  <p className="text-2xl font-bold">{gesdenStatus?.synced_appointments || 0}</p>
                  <p className="text-xs text-gray-500">
                    {Math.round(gesdenStatus?.sync_percentage || 0)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pending Consents */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <FileText className="w-8 h-8 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">Consentimientos Pendientes</p>
                  <p className="text-2xl font-bold">{gesdenStatus?.pending_consents || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {selectedTab === 'appointments' && (
        <div className="space-y-4">
          {/* Date Selector */}
          <Card>
            <CardHeader>
              <CardTitle>Citas Gesden por Fecha</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4 mb-4">
                <Input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-48"
                />
                <p className="text-sm text-gray-600">
                  {gesdenAppointments.length} cita{gesdenAppointments.length !== 1 ? 's' : ''} encontrada{gesdenAppointments.length !== 1 ? 's' : ''}
                </p>
              </div>

              {/* Appointments List */}
              <div className="space-y-3">
                {gesdenAppointments.length > 0 ? (
                  gesdenAppointments.map((appointment, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                            {appointment.patient_name.split(' ').map(n => n.charAt(0)).join('').slice(0,2)}
                          </div>
                          <div>
                            <h3 className="font-semibold">{appointment.patient_name}</h3>
                            <p className="text-sm text-gray-600">
                              NumPac: {appointment.patient_number}
                            </p>
                          </div>
                        </div>
                        <Badge className={`${appointment.synced_to_app ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {appointment.synced_to_app ? 'Sincronizada' : 'Pendiente'}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span>{appointment.time}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-500" />
                          <span>{appointment.doctor_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-gray-500" />
                          <span>{appointment.treatment_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Phone className="w-4 h-4 text-gray-500" />
                          <span>{appointment.phone || 'Sin teléfono'}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No hay citas para la fecha seleccionada</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {selectedTab === 'consents' && (
        <div className="space-y-4">
          {/* Consent Deliveries */}
          <Card>
            <CardHeader>
              <CardTitle>Estado de Consentimientos</CardTitle>
            </CardHeader>
            <CardContent>
              {loading.consents ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : consentDeliveries.length > 0 ? (
                <div className="space-y-3">
                  {consentDeliveries.map((delivery, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="font-semibold">{delivery.patient_name}</h3>
                          <p className="text-sm text-gray-600">{delivery.treatment_name}</p>
                        </div>
                        <Badge className={getStatusColor(delivery.delivery_status)}>
                          {getStatusText(delivery.delivery_status)}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Programado:</span>
                          <br />
                          {formatDate(delivery.scheduled_date)}
                        </div>
                        <div>
                          <span className="font-medium">Teléfono:</span>
                          <br />
                          {delivery.patient_phone}
                        </div>
                        <div>
                          <span className="font-medium">Método:</span>
                          <br />
                          {delivery.delivery_method}
                        </div>
                      </div>

                      {delivery.sent_at && (
                        <div className="mt-2 text-sm text-gray-600">
                          <span className="font-medium">Enviado:</span> {formatDate(delivery.sent_at)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No hay consentimientos programados</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {selectedTab === 'templates' && (
        <div className="space-y-4">
          {/* Treatment Codes */}
          <Card>
            <CardHeader>
              <CardTitle>Códigos de Tratamiento</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {treatmentCodes.map((treatment, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="font-semibold">Código {treatment.code}</h3>
                        <p className="text-sm text-gray-600">{treatment.name}</p>
                      </div>
                      <div className="flex space-x-2">
                        {treatment.requires_consent && (
                          <Badge className="bg-orange-100 text-orange-800">
                            Requiere Consentimiento
                          </Badge>
                        )}
                        {treatment.requires_lopd && (
                          <Badge className="bg-blue-100 text-blue-800">
                            Requiere LOPD
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Consent Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Plantillas de Consentimiento</CardTitle>
            </CardHeader>
            <CardContent>
              {loading.templates ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : consentTemplates.length > 0 ? (
                <div className="space-y-3">
                  {consentTemplates.map((template, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="font-semibold">{template.name}</h3>
                          <p className="text-sm text-gray-600">
                            Código {template.treatment_code} - {template.treatment_name}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={template.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {template.active ? 'Activa' : 'Inactiva'}
                          </Badge>
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="text-sm text-gray-600">
                        <p><span className="font-medium">Envío:</span> {template.send_timing === 'day_before' ? 'Día anterior' : 'Mismo día'} a las {template.send_hour}</p>
                        <p><span className="font-medium">Variables:</span> {template.variables.join(', ')}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No hay plantillas configuradas</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default GesdenManagement;