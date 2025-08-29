import React, { useState, useEffect } from 'react';
import { MessageCircle, Smartphone, Wifi, WifiOff, QrCode, CheckCircle, AlertCircle, Send, RefreshCw } from 'lucide-react';
import axios from 'axios';
import QRCode from 'qrcode.react';

const WhatsAppManager = () => {
  const [status, setStatus] = useState({ connected: false, status: 'disconnected' });
  const [qrCode, setQrCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testMessage, setTestMessage] = useState('');
  const [testPhone, setTestPhone] = useState('');
  const [sendingTest, setSendingTest] = useState(false);
  
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

  useEffect(() => {
    fetchStatus();
    // Check status every 5 seconds
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      setStatus(response.data);
      
      // If not connected, try to get QR code
      if (!response.data.connected) {
        fetchQRCode();
      } else {
        setQrCode(null);
      }
    } catch (error) {
      console.error('Error fetching WhatsApp status:', error);
      setStatus({ connected: false, status: 'error' });
    }
  };

  const fetchQRCode = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/qr`);
      setQrCode(response.data.qr);
    } catch (error) {
      console.error('Error fetching QR code:', error);
    }
  };

  const sendTestMessage = async () => {
    if (!testPhone || !testMessage) return;
    
    setSendingTest(true);
    try {
      const response = await axios.post(`${API}/whatsapp/send`, {
        phone_number: testPhone,
        message: testMessage
      });
      
      if (response.data.success) {
        toast.success('Mensaje de prueba enviado correctamente');
        setTestMessage('');
        setTestPhone('');
      } else {
        toast.error('Error enviando mensaje de prueba');
      }
    } catch (error) {
      console.error('Error sending test message:', error);
      toast.error('Error enviando mensaje de prueba');
    } finally {
      setSendingTest(false);
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'connected': return 'text-green-600 bg-green-50 border-green-200';
      case 'disconnected': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'connected': return <CheckCircle className="w-5 h-5" />;
      case 'disconnected': return <WifiOff className="w-5 h-5" />;
      case 'error': return <AlertCircle className="w-5 h-5" />;
      default: return <Wifi className="w-5 h-5" />;
    }
  };

  const getStatusMessage = () => {
    switch (status.status) {
      case 'connected': 
        return `Conectado como: ${status.user?.name || 'Usuario WhatsApp'}`;
      case 'disconnected': 
        return 'WhatsApp no conectado. Escanee el código QR para conectar.';
      case 'error': 
        return 'Error de conexión. Verifique que el servicio esté funcionando.';
      default: 
        return 'Verificando estado de conexión...';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">WhatsApp Business</h2>
            <p className="text-gray-600">Gestión de mensajería para la clínica</p>
          </div>
        </div>
        
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Status Card */}
      <div className={`p-4 rounded-lg border-2 ${getStatusColor()}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <div>
              <h3 className="font-semibold">Estado de WhatsApp</h3>
              <p className="text-sm">{getStatusMessage()}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              status.connected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.connected ? 'Conectado' : 'Desconectado'}
            </div>
          </div>
        </div>
      </div>

      {/* QR Code Section */}
      {qrCode && (
        <div className="bg-white p-6 rounded-lg shadow border text-center">
          <div className="flex items-center justify-center mb-4">
            <QrCode className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold">Conectar WhatsApp</h3>
          </div>
          
          <div className="flex justify-center mb-4">
            <QRCode 
              value={qrCode} 
              size={256}
              bgColor="#FFFFFF"
              fgColor="#000000"
              level="M"
              includeMargin={true}
            />
          </div>
          
          <div className="text-sm text-gray-600 space-y-2">
            <p><strong>Pasos para conectar:</strong></p>
            <ol className="text-left max-w-md mx-auto space-y-1">
              <li>1. Abra WhatsApp en su teléfono</li>
              <li>2. Toque Menú ⋮ → Dispositivos vinculados</li>
              <li>3. Toque "Vincular un dispositivo"</li>
              <li>4. Escanee este código QR</li>
            </ol>
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center mb-4">
            <Smartphone className="w-6 h-6 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold">Funcionalidades Disponibles</h3>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Recordatorios automáticos de citas</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Consentimientos informados para cirugías</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Asistente IA para consultas de pacientes</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Detección automática de urgencias</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              <span>Derivación inteligente a especialistas</span>
            </div>
          </div>
        </div>

        {/* Test Message Section */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center mb-4">
            <Send className="w-6 h-6 text-green-600 mr-3" />
            <h3 className="text-lg font-semibold">Enviar Mensaje de Prueba</h3>
          </div>
          
          {status.connected ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Número de teléfono (con código de país)
                </label>
                <input
                  type="text"
                  placeholder="Ej: 34664218253"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mensaje
                </label>
                <textarea
                  placeholder="Escriba su mensaje de prueba..."
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                />
              </div>
              
              <button
                onClick={sendTestMessage}
                disabled={sendingTest || !testPhone || !testMessage}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {sendingTest ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Send className="w-4 h-4 mr-2" />
                )}
                {sendingTest ? 'Enviando...' : 'Enviar Mensaje'}
              </button>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p>Conecte WhatsApp para enviar mensajes de prueba</p>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-800 mb-3">
          Configuración de Automatizaciones
        </h3>
        <div className="text-sm text-blue-700 space-y-2">
          <p>Las automatizaciones de WhatsApp funcionan de la siguiente manera:</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li><strong>Recordatorios de citas:</strong> Se envían automáticamente el día anterior a las 16:00h</li>
            <li><strong>Consentimientos de cirugía:</strong> Se envían el día anterior a las 10:00h para implantes, cirugías y extracciones</li>
            <li><strong>Asistente IA:</strong> Responde automáticamente a mensajes de pacientes con detección de urgencias</li>
          </ul>
          <p className="text-xs text-blue-600 mt-3">
            Las automatizaciones se ejecutan mientras WhatsApp esté conectado y el servicio funcionando.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppManager;