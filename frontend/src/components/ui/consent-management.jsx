import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Send, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  MessageSquare,
  Phone,
  Calendar,
  User,
  Download,
  Eye
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ConsentManagement = () => {
  const [dashboardTasks, setDashboardTasks] = useState([]);
  const [consentDeliveries, setConsentDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('tasks');
  const [selectedTask, setSelectedTask] = useState(null);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [consentFormData, setConsentFormData] = useState({
    phone_number: '',
    patient_name: '',
    treatment_code: 9,
    consent_type: 'treatment'
  });

  // Colores por prioridad y tipo
  const getTaskColor = (colorCode) => {
    const colors = {
      red: 'bg-red-100 border-red-300 text-red-800',
      yellow: 'bg-yellow-100 border-yellow-300 text-yellow-800',
      green: 'bg-green-100 border-green-300 text-green-800',
      gray: 'bg-gray-100 border-gray-300 text-gray-800'
    };
    return colors[colorCode] || colors.gray;
  };

  const getTaskIcon = (taskType) => {
    const icons = {
      consent_follow_up: AlertCircle,
      reschedule_request: Calendar,
      survey_review: MessageSquare,
      conversation_follow_up: Phone
    };
    return icons[taskType] || FileText;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'text-red-600',
      medium: 'text-yellow-600',
      low: 'text-green-600'
    };
    return colors[priority] || colors.medium;
  };

  // Cargar datos
  useEffect(() => {
    fetchDashboardTasks();
    fetchConsentDeliveries();
  }, []);

  const fetchDashboardTasks = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/tasks`);
      setDashboardTasks(response.data);
    } catch (error) {
      console.error('Error fetching dashboard tasks:', error);
      toast.error('Error cargando tareas del dashboard');
    }
  };

  const fetchConsentDeliveries = async () => {
    try {
      const response = await axios.get(`${API}/consent-deliveries`);
      setConsentDeliveries(response.data);
    } catch (error) {
      console.error('Error fetching consent deliveries:', error);
      toast.error('Error cargando entregas de consentimiento');
    } finally {
      setLoading(false);
    }
  };

  // Enviar formulario de consentimiento
  const sendConsentForm = async () => {
    try {
      setLoading(true);
      
      const response = await axios.post(`${API}/whatsapp/send-consent`, consentFormData);
      
      if (response.data.success) {
        toast.success('Formulario de consentimiento enviado correctamente');
        setShowConsentModal(false);
        setConsentFormData({
          phone_number: '',
          patient_name: '',
          treatment_code: 9,
          consent_type: 'treatment'
        });
        fetchConsentDeliveries();
      }
    } catch (error) {
      console.error('Error sending consent form:', error);
      toast.error('Error enviando formulario de consentimiento');
    } finally {
      setLoading(false);
    }
  };

  // Enviar encuesta primera visita
  const sendFirstVisitSurvey = async (phoneNumber, patientName) => {
    try {
      const response = await axios.post(`${API}/whatsapp/send-survey`, {
        phone_number: phoneNumber,
        patient_name: patientName
      });
      
      if (response.data.success) {
        toast.success('Encuesta de primera visita enviada');
        fetchDashboardTasks();
      }
    } catch (error) {
      console.error('Error sending survey:', error);
      toast.error('Error enviando encuesta');
    }
  };

  // Marcar tarea como completada
  const markTaskCompleted = async (taskId) => {
    try {
      await axios.put(`${API}/dashboard/tasks/${taskId}`, {
        status: 'completed',
        color_code: 'green'
      });
      
      toast.success('Tarea marcada como completada');
      fetchDashboardTasks();
    } catch (error) {
      console.error('Error updating task:', error);
      toast.error('Error actualizando tarea');
    }
  };

  // Formatear fecha
  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const treatmentCodes = {
    9: 'Periodoncia',
    10: 'Cirugía e Implantes',
    11: 'Ortodoncia',
    13: 'Primera cita - LOPD',
    16: 'Endodoncia'
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
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900">
          Gestión de Consentimientos
        </h1>
        
        <button
          onClick={() => setShowConsentModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Send className="w-4 h-4" />
          <span>Enviar Consentimiento</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tasks'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Tareas Pendientes ({dashboardTasks.filter(t => t.status === 'pending').length})
          </button>
          <button
            onClick={() => setActiveTab('deliveries')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'deliveries'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Entregas ({consentDeliveries.length})
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {activeTab === 'tasks' && (
          <>
            {dashboardTasks.filter(task => task.status === 'pending').length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No hay tareas pendientes</h3>
                <p className="text-gray-500">Todas las tareas han sido completadas</p>
              </div>
            ) : (
              <div className="space-y-4">
                {dashboardTasks
                  .filter(task => task.status === 'pending')
                  .sort((a, b) => {
                    const priorityOrder = { high: 0, medium: 1, low: 2 };
                    return priorityOrder[a.priority] - priorityOrder[b.priority];
                  })
                  .map((task) => {
                    const TaskIcon = getTaskIcon(task.task_type);
                    return (
                      <div
                        key={task.id}
                        className={`p-4 rounded-lg border-l-4 ${getTaskColor(task.color_code)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <TaskIcon className="w-5 h-5 mt-1" />
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h3 className="font-semibold">{task.patient_name}</h3>
                                <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                                  {task.priority.toUpperCase()}
                                </span>
                              </div>
                              
                              <p className="text-sm text-gray-700 mb-2">{task.description}</p>
                              
                              <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <div className="flex items-center space-x-1">
                                  <Phone className="w-3 h-3" />
                                  <span>{task.patient_phone}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{formatDate(task.created_at)}</span>
                                </div>
                              </div>
                              
                              {task.notes && (
                                <div className="mt-2 p-2 bg-white bg-opacity-50 rounded text-xs">
                                  <strong>Notas:</strong> {task.notes}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex space-x-2">
                            {task.task_type === 'survey_review' && (
                              <button
                                onClick={() => sendFirstVisitSurvey(task.patient_phone, task.patient_name)}
                                className="text-blue-600 hover:text-blue-800 text-sm"
                              >
                                Enviar Encuesta
                              </button>
                            )}
                            
                            <button
                              onClick={() => markTaskCompleted(task.id)}
                              className="text-green-600 hover:text-green-800 text-sm flex items-center space-x-1"
                            >
                              <CheckCircle className="w-4 h-4" />
                              <span>Completar</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}
          </>
        )}

        {activeTab === 'deliveries' && (
          <>
            {consentDeliveries.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No hay entregas de consentimiento</h3>
                <p className="text-gray-500">Las entregas aparecerán aquí cuando se envíen</p>
              </div>
            ) : (
              <div className="space-y-4">
                {consentDeliveries.map((delivery) => (
                  <div key={delivery.id} className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <FileText className="w-5 h-5 text-blue-600 mt-1" />
                        <div>
                          <h3 className="font-semibold">{delivery.patient_name}</h3>
                          <p className="text-sm text-gray-600">{delivery.treatment_name}</p>
                          
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                            <div className="flex items-center space-x-1">
                              <Phone className="w-3 h-3" />
                              <span>{delivery.patient_phone}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{formatDate(delivery.scheduled_date)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          delivery.delivery_status === 'sent' ? 'bg-green-100 text-green-800' :
                          delivery.delivery_status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {delivery.delivery_status === 'sent' ? 'Enviado' :
                           delivery.delivery_status === 'failed' ? 'Fallido' : 'Pendiente'}
                        </span>
                        
                        {delivery.sent_at && (
                          <span className="text-xs text-gray-500">
                            {formatDate(delivery.sent_at)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal para enviar consentimiento */}
      {showConsentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Enviar Formulario de Consentimiento</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre del Paciente
                </label>
                <input
                  type="text"
                  value={consentFormData.patient_name}
                  onChange={(e) => setConsentFormData({...consentFormData, patient_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nombre completo del paciente"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Teléfono (WhatsApp)
                </label>
                <input
                  type="tel"
                  value={consentFormData.phone_number}
                  onChange={(e) => setConsentFormData({...consentFormData, phone_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: 34664218253"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Tratamiento
                </label>
                <select
                  value={consentFormData.treatment_code}
                  onChange={(e) => setConsentFormData({...consentFormData, treatment_code: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  {Object.entries(treatmentCodes).map(([code, name]) => (
                    <option key={code} value={code}>{name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Consentimiento
                </label>
                <select
                  value={consentFormData.consent_type}
                  onChange={(e) => setConsentFormData({...consentFormData, consent_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="treatment">Consentimiento de Tratamiento</option>
                  <option value="lopd">Documento LOPD</option>
                </select>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowConsentModal(false)}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancelar
              </button>
              <button
                onClick={sendConsentForm}
                disabled={!consentFormData.patient_name || !consentFormData.phone_number}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Enviar</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsentManagement;