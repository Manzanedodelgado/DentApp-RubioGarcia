import React from "react";
import { Settings, Brain, Zap, Users, MessageCircle, Save, Mic, MicOff } from "lucide-react";

// Componente completo de configuración que será usado en App.js
const SettingsContent = ({ 
  activeConfigTab, 
  setActiveConfigTab, 
  configTabs, 
  clinicSettings, 
  setClinicSettings, 
  aiSettings, 
  setAiSettings, 
  automationRules, 
  setAutomationRules,
  saveClinicSettings,
  saveAiSettings,
  aiModels,
  loading,
  voiceEnabled,
  isListening,
  startListening,
  stopListening,
  voiceResponse
}) => {
  const modelProviders = {
    "gpt-4o-mini": "openai",
    "gpt-4o": "openai",
    "claude-3-7-sonnet-20250219": "anthropic",
    "gemini-2.0-flash": "gemini"
  };
  return (
    <>
      {/* Configuration Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            {configTabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveConfigTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeConfigTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* Clinic Settings Tab */}
          {activeConfigTab === "clinic" && clinicSettings && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Información de la Clínica</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre de la Clínica
                    </label>
                    <input
                      type="text"
                      value={clinicSettings.name || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Teléfono
                    </label>
                    <input
                      type="text"
                      value={clinicSettings.phone || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, phone: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Dirección
                    </label>
                    <input
                      type="text"
                      value={clinicSettings.address || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, address: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      WhatsApp
                    </label>
                    <input
                      type="text"
                      value={clinicSettings.whatsapp || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, whatsapp: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={clinicSettings.email || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Horarios de Atención
                    </label>
                    <input
                      type="text"
                      value={clinicSettings.schedule || ""}
                      onChange={(e) => setClinicSettings(prev => ({ ...prev, schedule: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Ej: Lun-Jue 10:00-14:00 y 16:00-20:00 | Vie 10:00-14:00"
                    />
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="text-md font-medium mb-3">Equipo Médico</h4>
                  <div className="space-y-3">
                    {clinicSettings.team && clinicSettings.team.map((member, index) => (
                      <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {member.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-medium">{member.name}</div>
                          <div className="text-sm text-gray-600">{member.specialty}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <button
                  onClick={saveClinicSettings}
                  disabled={loading}
                  className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{loading ? "Guardando..." : "Guardar Información"}</span>
                </button>
              </div>
            </div>
          )}
          
          {/* AI Settings Tab */}
          {activeConfigTab === "ai" && aiSettings && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Configuración del Asistente de IA</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Modelo de IA
                    </label>
                    <select
                      value={aiSettings.model_name || "gpt-4o-mini"}
                      onChange={(e) => {
                        const modelName = e.target.value;
                        const provider = modelProviders[modelName] || "openai";
                        setAiSettings(prev => ({ 
                          ...prev, 
                          model_name: modelName,
                          model_provider: provider
                        }));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      {aiModels.map(model => (
                        <option key={model.value} value={model.value}>
                          {model.label}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      {aiModels.find(m => m.value === aiSettings.model_name)?.description}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Temperatura: {aiSettings.temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={aiSettings.temperature}
                      onChange={(e) => setAiSettings(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Conservadora</span>
                      <span>Creativa</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt del Sistema
                  </label>
                  <textarea
                    value={aiSettings.system_prompt || ""}
                    onChange={(e) => setAiSettings(prev => ({ ...prev, system_prompt: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Describe cómo debe comportarse la IA..."
                  />
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="ai-enabled"
                      checked={aiSettings.enabled}
                      onChange={(e) => setAiSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="ai-enabled" className="ml-2 text-sm text-gray-700">
                      IA Habilitada
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="voice-enabled"
                      checked={aiSettings.voice_enabled}
                      onChange={(e) => setAiSettings(prev => ({ ...prev, voice_enabled: e.target.checked }))}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="voice-enabled" className="ml-2 text-sm text-gray-700">
                      Asistente de Voz
                    </label>
                  </div>
                </div>
                
                <button
                  onClick={saveAiSettings}
                  disabled={loading}
                  className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{loading ? "Guardando..." : "Guardar Configuración IA"}</span>
                </button>
              </div>
            </div>
          )}
          
          {/* Automations Tab */}
          {activeConfigTab === "automations" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Automatizaciones</h3>
                
                <div className="space-y-4">
                  {automationRules.map((rule, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{rule.name}</h4>
                          <p className="text-sm text-gray-600">{rule.description}</p>
                          <p className="text-xs text-gray-500">
                            Tipo: {rule.trigger_type} | Horario: {rule.trigger_time}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={rule.enabled}
                            onChange={(e) => {
                              const updatedRules = [...automationRules];
                              updatedRules[index].enabled = e.target.checked;
                              setAutomationRules(updatedRules);
                            }}
                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-600">
                            {rule.enabled ? "Activa" : "Inactiva"}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Automatizaciones Disponibles</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Recordatorios de cita (día anterior a las 16:00h)</li>
                    <li>• Mensaje automático para nuevas citas</li>
                    <li>• Consentimiento informado para cirugías</li>
                    <li>• Recordatorios de revisión anual</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
          
          {/* Voice Assistant Tab */}
          {activeConfigTab === "voice" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Asistente de Voz</h3>
                
                {voiceEnabled ? (
                  <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <div className="flex items-center space-x-2">
                        <Mic className="w-5 h-5 text-green-600" />
                        <span className="text-green-800 font-medium">Micrófono disponible</span>
                      </div>
                      <p className="text-sm text-green-700 mt-1">
                        El asistente de voz está listo para usar
                      </p>
                    </div>
                    
                    {/* Permission Status */}
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <h4 className="font-medium text-blue-800 mb-2">Estado del Micrófono</h4>
                      <button
                        onClick={async () => {
                          try {
                            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                            stream.getTracks().forEach(track => track.stop());
                            alert('✅ Micrófono funcionando correctamente');
                          } catch (error) {
                            alert('❌ Error con el micrófono: ' + error.message);
                          }
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Probar Micrófono
                      </button>
                      <p className="text-sm text-blue-700 mt-2">
                        Haz clic para verificar si el micrófono tiene permisos y funciona correctamente.
                      </p>
                    </div>
                    
                    <div className="border rounded-lg p-6 text-center">
                      <button
                        onClick={isListening ? stopListening : startListening}
                        className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-medium transition-all ${
                          isListening 
                            ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                            : 'bg-blue-500 hover:bg-blue-600'
                        }`}
                      >
                        {isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                      </button>
                      
                      <h4 className="mt-4 font-medium">
                        {isListening ? "Escuchando..." : "Pulsa para hablar"}
                      </h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {isListening 
                          ? "Di tu comando, por ejemplo: 'Hola asistente, muéstrame las citas de hoy'" 
                          : "Haz clic para activar el micrófono y dar un comando de voz"
                        }
                      </p>
                    </div>
                    
                    {voiceResponse && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="font-medium mb-2">Respuesta del Asistente:</h5>
                        <p className="text-sm text-gray-700">{voiceResponse}</p>
                      </div>
                    )}
                    
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-800 mb-2">Comandos Disponibles</h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• "Hola asistente, ¿cómo puedes ayudarme?"</li>
                        <li>• "Muéstrame las citas de hoy"</li>
                        <li>• "¿Qué pacientes tengo pendientes?"</li>
                        <li>• "Agenda una cita para mañana"</li>
                        <li>• "Envía un recordatorio a todos los pacientes"</li>
                      </ul>
                    </div>
                    
                    {/* Troubleshooting Tips */}
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <h4 className="font-medium text-yellow-800 mb-2">¿No funciona el micrófono?</h4>
                      <ul className="text-sm text-yellow-700 space-y-1">
                        <li>1. Verifica que has dado permisos de micrófono al navegador</li>
                        <li>2. Revisa que tu micrófono no esté silenciado</li>
                        <li>3. Prueba en otro navegador (Chrome recomendado)</li>
                        <li>4. Verifica que estés usando HTTPS (protocolo seguro)</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                      <div className="flex items-center space-x-2">
                        <MicOff className="w-5 h-5 text-red-600" />
                        <span className="text-red-800 font-medium">Micrófono no disponible</span>
                      </div>
                      <p className="text-sm text-red-700 mt-1">
                        Tu navegador no soporta reconocimiento de voz o no has dado permisos al micrófono
                      </p>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <h4 className="font-medium text-blue-800 mb-2">Cómo activar el micrófono:</h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>1. <strong>Chrome:</strong> Haz clic en el icono de candado → Permisos → Micrófono → Permitir</li>
                        <li>2. <strong>Firefox:</strong> Haz clic en el icono de micrófono en la barra de direcciones → Permitir</li>
                        <li>3. <strong>Safari:</strong> Safari → Preferencias → Sitios web → Micrófono → Permitir</li>
                        <li>4. Actualiza la página después de cambiar los permisos</li>
                      </ul>
                    </div>
                    
                    <div className="text-center">
                      <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Recargar Página
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default SettingsContent;