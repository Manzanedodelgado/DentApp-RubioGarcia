import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Zap, 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Users,
  Calendar,
  FileText,
  Phone,
  TrendingUp,
  Link,
  Play,
  Pause,
  Plus,
  Edit,
  Trash2,
  Brain,
  Network,
  Clock,
  Target
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAutomations = () => {
  const [automations, setAutomations] = useState([]);
  const [executionHistory, setExecutionHistory] = useState([]);
  const [dependencies, setDependencies] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('automations');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTrainingModal, setShowTrainingModal] = useState(false);
  const [selectedAutomation, setSelectedAutomation] = useState(null);

  // Categories for automation classification
  const categories = [
    { value: 'all', label: 'Todas las Categorías', icon: Zap, color: 'bg-gray-100' },
    { value: 'triage', label: 'Triaje Inteligente', icon: AlertTriangle, color: 'bg-red-100' },
    { value: 'appointment_management', label: 'Gestión de Citas', icon: Calendar, color: 'bg-blue-100' },
    { value: 'patient_communication', label: 'Comunicación', icon: Phone, color: 'bg-green-100' },
    { value: 'consent_management', label: 'Consentimientos', icon: FileText, color: 'bg-yellow-100' },
    { value: 'follow_up', label: 'Seguimiento', icon: TrendingUp, color: 'bg-purple-100' }
  ];

  // Priority colors
  const getPriorityColor = (priority) => {
    if (priority >= 9) return 'bg-red-500';
    if (priority >= 7) return 'bg-orange-500';
    if (priority >= 5) return 'bg-yellow-500';
    if (priority >= 3) return 'bg-blue-500';
    return 'bg-gray-500';
  };

  const getPriorityLabel = (priority) => {
    if (priority >= 9) return 'Crítica';
    if (priority >= 7) return 'Alta';
    if (priority >= 5) return 'Media';
    if (priority >= 3) return 'Baja';
    return 'Muy Baja';
  };

  // Load data
  useEffect(() => {
    fetchData();
  }, [selectedCategory]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch automations
      const automationsParams = selectedCategory !== 'all' ? `?category=${selectedCategory}` : '';
      const automationsResponse = await axios.get(`${API}/ai-automations${automationsParams}`);
      setAutomations(automationsResponse.data);
      
      // Fetch dependencies
      const dependenciesResponse = await axios.get(`${API}/ai-automations/dependencies`);
      setDependencies(dependenciesResponse.data.dependency_graph || {});
      
      // Fetch execution history
      const historyResponse = await axios.get(`${API}/ai-automations/execution-history?limit=20`);
      setExecutionHistory(historyResponse.data);
      
    } catch (error) {
      console.error('Error fetching automations data:', error);
      toast.error('Error cargando automatizaciones');
    } finally {
      setLoading(false);
    }
  };

  // Toggle automation status
  const toggleAutomation = async (automationId, currentStatus) => {
    try {
      const response = await axios.post(`${API}/ai-automations/${automationId}/toggle`);
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      console.error('Error toggling automation:', error);
      toast.error(error.response?.data?.detail || 'Error cambiando estado de automatización');
    }
  };

  // Get automation icon
  const getAutomationIcon = (category) => {
    const categoryData = categories.find(cat => cat.value === category);
    return categoryData ? categoryData.icon : Bot;
  };

  // Get category color
  const getCategoryColor = (category) => {
    const categoryData = categories.find(cat => cat.value === category);
    return categoryData ? categoryData.color : 'bg-gray-100';
  };

  // Format execution time
  const formatExecutionTime = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  // Get dependency status
  const getDependencyStatus = (automation) => {
    const deps = dependencies[automation.id];
    if (!deps) return { canActivate: true, issues: [] };
    
    const issues = [];
    
    // Check if dependencies are active
    if (deps.dependencies) {
      deps.dependencies.forEach(dep => {
        const depAutomation = automations.find(a => a.id === dep.id);
        if (depAutomation && !depAutomation.is_active) {
          issues.push(`Depende de: ${depAutomation.name} (inactiva)`);
        }
      });
    }
    
    // Check for conflicts
    automation.conflicts_with?.forEach(conflictName => {
      const conflictAutomation = automations.find(a => a.name === conflictName && a.is_active);
      if (conflictAutomation) {
        issues.push(`Conflicto con: ${conflictName} (activa)`);
      }
    });
    
    return {
      canActivate: issues.length === 0,
      issues
    };
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
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Bot className="w-8 h-8 text-blue-600" />
            Automatizaciones IA
          </h1>
          <p className="text-gray-600 mt-2">Gestiona automatizaciones inteligentes con IA entrenable y dependencias</p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Nueva Automatización</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('automations')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'automations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4" />
              <span>Automatizaciones ({automations.length})</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('dependencies')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'dependencies'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4" />
              <span>Dependencias</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('execution')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'execution'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Historial</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Category Filter */}
      {activeTab === 'automations' && (
        <div className="flex flex-wrap gap-2">
          {categories.map(category => {
            const Icon = category.icon;
            const isSelected = selectedCategory === category.value;
            
            return (
              <button
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isSelected
                    ? 'bg-blue-100 text-blue-800 border border-blue-200'
                    : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{category.label}</span>
                {category.value !== 'all' && (
                  <span className="bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                    {automations.filter(a => a.category === category.value).length}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Content */}
      <div className="space-y-4">
        {activeTab === 'automations' && (
          <>
            {automations.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No hay automatizaciones</h3>
                <p className="text-gray-500 mb-4">Crea tu primera automatización inteligente</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Crear Automatización
                </button>
              </div>
            ) : (
              <div className="grid gap-6">
                {automations.map(automation => {
                  const Icon = getAutomationIcon(automation.category);
                  const dependencyStatus = getDependencyStatus(automation);
                  
                  return (
                    <div key={automation.id} className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                      <div className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4 flex-1">
                            <div className={`p-3 rounded-lg ${getCategoryColor(automation.category)}`}>
                              <Icon className="w-6 h-6 text-gray-700" />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="text-lg font-semibold text-gray-900 truncate">
                                  {automation.name}
                                </h3>
                                
                                <div className="flex items-center space-x-2">
                                  <div className={`w-2 h-2 rounded-full ${getPriorityColor(automation.priority)}`}></div>
                                  <span className="text-xs text-gray-500 font-medium">
                                    {getPriorityLabel(automation.priority)}
                                  </span>
                                </div>
                                
                                {automation.ai_behavior && (
                                  <div className="flex items-center text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                                    <Brain className="w-3 h-3 mr-1" />
                                    IA Entrenada
                                  </div>
                                )}
                              </div>
                              
                              <p className="text-gray-600 text-sm mb-4">{automation.description}</p>
                              
                              <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <div className="flex items-center space-x-1">
                                  <Target className="w-3 h-3" />
                                  <span>Activaciones: {automation.success_count}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <XCircle className="w-3 h-3" />
                                  <span>Fallos: {automation.failure_count}</span>
                                </div>
                                {automation.last_execution && (
                                  <div className="flex items-center space-x-1">
                                    <Clock className="w-3 h-3" />
                                    <span>Última: {new Date(automation.last_execution).toLocaleDateString('es-ES')}</span>
                                  </div>
                                )}
                              </div>
                              
                              {/* Dependencies and conflicts */}
                              {(automation.dependencies?.length > 0 || automation.conflicts_with?.length > 0) && (
                                <div className="mt-3 pt-3 border-t border-gray-100">
                                  {automation.dependencies?.length > 0 && (
                                    <div className="text-xs text-blue-600 mb-1">
                                      <Link className="w-3 h-3 inline mr-1" />
                                      Depende de: {automation.dependencies.length} automatización(es)
                                    </div>
                                  )}
                                  {automation.conflicts_with?.length > 0 && (
                                    <div className="text-xs text-orange-600">
                                      <AlertTriangle className="w-3 h-3 inline mr-1" />
                                      Conflictos: {automation.conflicts_with.join(', ')}
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Dependency issues */}
                              {!dependencyStatus.canActivate && automation.is_active && (
                                <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                                  <AlertTriangle className="w-3 h-3 inline mr-1" />
                                  Problemas: {dependencyStatus.issues.join(', ')}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2 ml-4">
                            {/* Status indicator */}
                            <div className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                              automation.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {automation.is_active ? (
                                <>
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Activa
                                </>
                              ) : (
                                <>
                                  <Pause className="w-3 h-3 mr-1" />
                                  Inactiva
                                </>
                              )}
                            </div>
                            
                            {/* Actions */}
                            <div className="flex space-x-1">
                              {automation.ai_behavior && (
                                <button
                                  onClick={() => {
                                    setSelectedAutomation(automation);
                                    setShowTrainingModal(true);
                                  }}
                                  className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                                  title="Entrenar IA"
                                >
                                  <Brain className="w-4 h-4" />
                                </button>
                              )}
                              
                              <button
                                onClick={() => toggleAutomation(automation.id, automation.is_active)}
                                className={`p-2 rounded-lg ${
                                  automation.is_active
                                    ? 'text-red-600 hover:bg-red-50'
                                    : 'text-green-600 hover:bg-green-50'
                                }`}
                                title={automation.is_active ? 'Desactivar' : 'Activar'}
                                disabled={!automation.is_active && !dependencyStatus.canActivate}
                              >
                                {automation.is_active ? (
                                  <Pause className="w-4 h-4" />
                                ) : (
                                  <Play className="w-4 h-4" />
                                )}
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}

        {activeTab === 'dependencies' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Mapa de Dependencias</h3>
            
            {Object.keys(dependencies).length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Network className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No hay dependencias configuradas</p>
              </div>
            ) : (
              <div className="space-y-4">
                {automations.map(automation => {
                  const deps = dependencies[automation.id];
                  if (!deps || (deps.dependencies.length === 0 && deps.dependents.length === 0)) return null;
                  
                  return (
                    <div key={automation.id} className="border rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3">{automation.name}</h4>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        {deps.dependencies.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                              <Link className="w-4 h-4 mr-1" />
                              Depende de:
                            </h5>
                            <div className="space-y-1">
                              {deps.dependencies.map(dep => {
                                const depAutomation = automations.find(a => a.id === dep.id);
                                return (
                                  <div key={dep.id} className="text-sm text-gray-600 flex items-center justify-between">
                                    <span>{depAutomation?.name || dep.id}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${
                                      depAutomation?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                    }`}>
                                      {depAutomation?.is_active ? 'Activa' : 'Inactiva'}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        
                        {deps.dependents.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                              <Users className="w-4 h-4 mr-1" />
                              Dependientes:
                            </h5>
                            <div className="space-y-1">
                              {deps.dependents.map(dep => {
                                const depAutomation = automations.find(a => a.id === dep.id);
                                return (
                                  <div key={dep.id} className="text-sm text-gray-600 flex items-center justify-between">
                                    <span>{depAutomation?.name || dep.id}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${
                                      depAutomation?.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                                    }`}>
                                      {depAutomation?.is_active ? 'Activa' : 'Inactiva'}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'execution' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Historial de Ejecuciones</h3>
            
            {executionHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No hay ejecuciones registradas</p>
              </div>
            ) : (
              <div className="space-y-3">
                {executionHistory.map(execution => {
                  const automation = automations.find(a => a.id === execution.automation_id);
                  
                  return (
                    <div key={execution.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          execution.execution_status === 'completed' ? 'bg-green-500' :
                          execution.execution_status === 'failed' ? 'bg-red-500' :
                          execution.execution_status === 'running' ? 'bg-blue-500' :
                          'bg-gray-500'
                        }`}></div>
                        
                        <div>
                          <div className="font-medium text-sm">
                            {automation?.name || 'Automatización desconocida'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(execution.started_at).toLocaleString('es-ES')}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className={`px-2 py-1 rounded ${
                          execution.execution_status === 'completed' ? 'bg-green-100 text-green-800' :
                          execution.execution_status === 'failed' ? 'bg-red-100 text-red-800' :
                          execution.execution_status === 'running' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {execution.execution_status}
                        </span>
                        
                        {execution.execution_time_ms && (
                          <span>{formatExecutionTime(execution.execution_time_ms)}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Modal Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-semibold mb-4">Crear Nueva Automatización</h3>
            <p className="text-gray-600 mb-4">
              Esta funcionalidad estará disponible próximamente. Las automatizaciones por defecto ya están creadas y funcionando.
            </p>
            <button 
              onClick={() => setShowCreateModal(false)}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Training Modal Placeholder */}
      {showTrainingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-purple-600" />
              Entrenar IA: {selectedAutomation?.name}
            </h3>
            <p className="text-gray-600 mb-4">
              El entrenamiento de IA personalizado estará disponible próximamente. 
              Las automatizaciones ya incluyen configuraciones de IA optimizadas.
            </p>
            <button 
              onClick={() => setShowTrainingModal(false)}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAutomations;