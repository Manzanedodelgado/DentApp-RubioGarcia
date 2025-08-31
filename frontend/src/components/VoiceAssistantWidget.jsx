import React, { useState, useEffect } from 'react';
import { Mic, MicOff, MessageCircle, Phone, Calendar, User, Clock, Waves } from 'lucide-react';
import axios from 'axios';

const VoiceAssistantWidget = () => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    // Initialize voice recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'es-ES';
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
        setTranscript('');
        setResponse('');
      };
      
      recognitionInstance.onresult = async (event) => {
        const spokenText = event.results[0][0].transcript;
        setTranscript(spokenText);
        await processVoiceCommand(spokenText);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setResponse('Error en el reconocimiento de voz. Inténtalo de nuevo.');
      };
      
      setRecognition(recognitionInstance);
      setVoiceSupported(true);
    }
  }, []);

  const processVoiceCommand = async (text) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/ai/voice-assistant`, {
        message: text,
        session_id: 'widget_session'
      });
      
      setResponse(response.data.response);
      
      // Speak the response if available
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.data.response);
        utterance.lang = 'es-ES';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
      
    } catch (error) {
      console.error('Error processing voice command:', error);
      setResponse('Error al procesar tu solicitud. Por favor, inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const startListening = () => {
    if (recognition && !isListening) {
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const quickActions = [
    {
      icon: Calendar,
      label: 'Agendar Cita',
      command: 'Quiero agendar una cita',
      color: 'bg-blue-500'
    },
    {
      icon: Phone,
      label: 'Información',
      command: '¿Cuáles son los horarios de la clínica?',
      color: 'bg-green-500'
    },
    {
      icon: User,
      label: 'Urgencia',
      command: 'Tengo una urgencia dental',
      color: 'bg-red-500'
    },
    {
      icon: Clock,
      label: 'Horarios',
      command: 'Dime los horarios de atención',
      color: 'bg-purple-500'
    }
  ];

  const handleQuickAction = (command) => {
    setTranscript(command);
    processVoiceCommand(command);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="p-4 text-center">
          <h1 className="text-xl font-bold text-gray-800">RUBIO GARCÍA DENTAL</h1>
          <p className="text-sm text-gray-600">Asistente Virtual con IA</p>
        </div>
      </div>

      {/* Main Voice Interface */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        {voiceSupported ? (
          <>
            {/* Voice Button */}
            <div className="relative mb-8">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={isLoading}
                className={`w-32 h-32 rounded-full flex items-center justify-center text-white font-semibold transition-all duration-300 shadow-lg ${
                  isListening 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse scale-110' 
                    : isLoading
                    ? 'bg-gray-400'
                    : 'bg-blue-500 hover:bg-blue-600 hover:scale-105'
                }`}
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
                ) : isListening ? (
                  <Waves className="w-12 h-12 animate-bounce" />
                ) : (
                  <Mic className="w-12 h-12" />
                )}
              </button>
              
              {/* Status Indicator */}
              <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-center">
                <p className="text-sm font-medium text-gray-700">
                  {isLoading 
                    ? 'Procesando...' 
                    : isListening 
                    ? 'Escuchando...' 
                    : 'Pulsa para hablar'
                  }
                </p>
                {isListening && (
                  <div className="flex justify-center mt-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Transcript Display */}
            {transcript && (
              <div className="w-full max-w-md mb-4">
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
                  <p className="text-sm text-gray-600 mb-1">Tu consulta:</p>
                  <p className="text-gray-800">{transcript}</p>
                </div>
              </div>
            )}

            {/* Response Display */}
            {response && (
              <div className="w-full max-w-md mb-6">
                <div className="bg-blue-50 rounded-lg shadow p-4 border-l-4 border-blue-500">
                  <div className="flex items-start space-x-2">
                    <MessageCircle className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div>
                      <p className="text-sm text-blue-600 mb-1">Asistente:</p>
                      <p className="text-gray-800 text-sm leading-relaxed">{response}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="w-full max-w-md">
              <p className="text-sm font-medium text-gray-700 mb-3 text-center">Acciones rápidas:</p>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={index}
                      onClick={() => handleQuickAction(action.command)}
                      disabled={isLoading || isListening}
                      className={`p-3 rounded-lg text-white font-medium text-sm transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:scale-100 ${action.color} hover:shadow-lg`}
                    >
                      <Icon className="w-5 h-5 mx-auto mb-1" />
                      {action.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center">
            <MicOff className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Micrófono no disponible</h2>
            <p className="text-gray-600 text-sm">
              Tu navegador no soporta reconocimiento de voz o no has dado permisos al micrófono.
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t p-4">
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">
            📞 916 410 841 • 📱 664 218 253
          </p>
          <p className="text-xs text-gray-500">
            Calle Mayor 19, Alcorcón • Lun-Jue 10-14 y 16-20h | Vie 10-14h
          </p>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistantWidget;