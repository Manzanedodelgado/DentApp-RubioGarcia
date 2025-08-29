const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const moment = require('moment-timezone');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8001';
const PORT = process.env.PORT || 3001;

let sock = null;
let qrCodeData = null;
let connectionStatus = 'disconnected';

// Initialize WhatsApp connection
async function initWhatsApp() {
    try {
        console.log('🚀 Initializing WhatsApp for RUBIO GARCÍA DENTAL...');
        
        const { state, saveCreds } = await useMultiFileAuthState('./auth_info');

        sock = makeWASocket({
            auth: state,
            printQRInTerminal: false,
            browser: ['RUBIO GARCÍA DENTAL', 'Chrome', '1.0.0'],
            generateHighQualityLinkPreview: true,
            markOnlineOnConnect: true
        });

        // Connection events
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                console.log('📱 QR Code generated for WhatsApp connection');
                qrCodeData = qr;
                qrcode.generate(qr, { small: true });
            }

            if (connection === 'close') {
                connectionStatus = 'disconnected';
                const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
                
                console.log('❌ Connection closed:', lastDisconnect?.error, 'Reconnecting:', shouldReconnect);
                
                if (shouldReconnect) {
                    setTimeout(initWhatsApp, 5000);
                }
            } else if (connection === 'open') {
                connectionStatus = 'connected';
                qrCodeData = null;
                console.log('✅ WhatsApp connected successfully!');
                console.log('📞 Connected as:', sock.user?.name || 'Unknown');
            }
        });

        // Message handling
        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const message of messages) {
                    if (!message.key.fromMe && message.message) {
                        await handleIncomingMessage(message);
                    }
                }
            }
        });

        // Save credentials
        sock.ev.on('creds.update', saveCreds);

    } catch (error) {
        console.error('❌ WhatsApp initialization error:', error);
        setTimeout(initWhatsApp, 10000);
    }
}

// Handle incoming messages with AI integration
async function handleIncomingMessage(message) {
    try {
        const phoneNumber = message.key.remoteJid.replace('@s.whatsapp.net', '');
        const messageText = extractMessageText(message);
        
        if (!messageText) return;

        console.log(`📨 Message from ${phoneNumber}: ${messageText}`);

        // Send typing indicator
        await sock.sendPresenceUpdate('composing', message.key.remoteJid);

        // Process with AI backend
        const response = await processWithAI(phoneNumber, messageText);
        
        if (response) {
            await sendMessage(phoneNumber, response);
        }

    } catch (error) {
        console.error('❌ Error handling message:', error);
        
        // Send error message to user
        const errorMsg = 'Disculpe, hubo un error procesando su mensaje. Por favor, intente nuevamente o llame al 916 410 841.';
        await sendMessage(phoneNumber, errorMsg);
    }
}

// Extract text from different message types
function extractMessageText(message) {
    if (message.message.conversation) {
        return message.message.conversation;
    }
    if (message.message.extendedTextMessage?.text) {
        return message.message.extendedTextMessage.text;
    }
    if (message.message.buttonsResponseMessage?.selectedDisplayText) {
        return message.message.buttonsResponseMessage.selectedDisplayText;
    }
    return null;
}

// Process message with AI backend
async function processWithAI(phoneNumber, messageText) {
    try {
        const response = await axios.post(`${FASTAPI_URL}/api/ai/voice-assistant`, {
            message: messageText,
            session_id: `whatsapp_${phoneNumber}`,
            phone_number: phoneNumber,
            platform: 'whatsapp'
        });

        const aiResponse = response.data.response;
        const actionType = response.data.action_type;
        const extractedData = response.data.extracted_data;

        console.log(`🤖 AI Response: ${aiResponse}`);
        console.log(`🎯 Action Type: ${actionType}`);

        // Handle specific actions
        if (actionType === 'URGENCIA') {
            return `🚨 ${aiResponse}\n\n⚡ URGENCIA DETECTADA\n📞 Llame INMEDIATAMENTE al 916 410 841\n📱 WhatsApp: 664 218 253`;
        }
        
        if (actionType === 'CITA_REGULAR') {
            return `${aiResponse}\n\n📅 Para agendar su cita:\n📞 Teléfono: 916 410 841\n📱 WhatsApp: 664 218 253\n🕐 Horarios: Lun-Jue 10-14h y 16-20h | Vie 10-14h`;
        }

        return aiResponse;

    } catch (error) {
        console.error('❌ AI processing error:', error);
        return `Hola, soy el asistente virtual de RUBIO GARCÍA DENTAL 🦷\n\nPara consultas urgentes:\n📞 916 410 841\n📱 664 218 253\n\n🕐 Horarios:\nLun-Jue: 10:00-14:00 y 16:00-20:00\nVie: 10:00-14:00\n\n📍 Calle Mayor 19, Alcorcón`;
    }
}

// Send message to WhatsApp
async function sendMessage(phoneNumber, text) {
    try {
        if (!sock || connectionStatus !== 'connected') {
            throw new Error('WhatsApp not connected');
        }

        const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`;
        
        await sock.sendMessage(jid, { 
            text: text,
            mentions: []
        });

        console.log(`✅ Message sent to ${phoneNumber}`);
        return { success: true };

    } catch (error) {
        console.error('❌ Error sending message:', error);
        return { success: false, error: error.message };
    }
}

// Send appointment reminder
async function sendAppointmentReminder(phoneNumber, appointmentData) {
    try {
        const { contact_name, date, time, doctor, treatment } = appointmentData;
        
        const formattedDate = moment(date).format('DD/MM/YYYY');
        const dayName = moment(date).locale('es').format('dddd');
        
        const reminderMessage = `🦷 RECORDATORIO DE CITA - RUBIO GARCÍA DENTAL

👤 Paciente: ${contact_name}
📅 Fecha: ${dayName} ${formattedDate}
🕐 Hora: ${time}
👨‍⚕️ Doctor: ${doctor}
🩺 Tratamiento: ${treatment}

📍 Calle Mayor 19, Alcorcón
📞 916 410 841 | 📱 664 218 253

⚡ Responda con:
✅ "CONFIRMO" para confirmar
❌ "CANCELO" para cancelar
📅 "CAMBIO" para reprogramar

¡Le esperamos mañana!`;

        return await sendMessage(phoneNumber, reminderMessage);
        
    } catch (error) {
        console.error('❌ Error sending reminder:', error);
        return { success: false, error: error.message };
    }
}

// Send surgery consent reminder
async function sendSurgeryConsent(phoneNumber, appointmentData) {
    try {
        const { contact_name, date, time, treatment } = appointmentData;
        
        const formattedDate = moment(date).format('DD/MM/YYYY');
        
        const consentMessage = `🦷 RECORDATORIO CIRUGÍA - RUBIO GARCÍA DENTAL

👤 Paciente: ${contact_name}
🩺 Cirugía: ${treatment}
📅 Mañana ${formattedDate} a las ${time}

⚠️ RECORDATORIO IMPORTANTE:
• Venir en AYUNAS (si requiere sedación)
• Traer ACOMPAÑANTE
• Leer el CONSENTIMIENTO INFORMADO

📞 Para dudas: 916 410 841
📱 WhatsApp: 664 218 253

¡Nos vemos mañana en Calle Mayor 19, Alcorcón!`;

        return await sendMessage(phoneNumber, consentMessage);
        
    } catch (error) {
        console.error('❌ Error sending consent:', error);
        return { success: false, error: error.message };
    }
}

// REST API Endpoints
app.get('/status', (req, res) => {
    res.json({
        connected: connectionStatus === 'connected',
        status: connectionStatus,
        user: sock?.user || null,
        timestamp: new Date().toISOString()
    });
});

app.get('/qr', (req, res) => {
    res.json({
        qr: qrCodeData,
        status: connectionStatus,
        message: qrCodeData ? 'Scan QR code with WhatsApp' : 'No QR code available'
    });
});

app.post('/send', async (req, res) => {
    const { phone_number, message } = req.body;
    
    if (!phone_number || !message) {
        return res.status(400).json({ error: 'Phone number and message are required' });
    }
    
    const result = await sendMessage(phone_number, message);
    res.json(result);
});

app.post('/send-reminder', async (req, res) => {
    const { phone_number, appointment_data } = req.body;
    
    if (!phone_number || !appointment_data) {
        return res.status(400).json({ error: 'Phone number and appointment data are required' });
    }
    
    const result = await sendAppointmentReminder(phone_number, appointment_data);
    res.json(result);
});

app.post('/send-consent', async (req, res) => {
    const { phone_number, appointment_data } = req.body;
    
    if (!phone_number || !appointment_data) {
        return res.status(400).json({ error: 'Phone number and appointment data are required' });
    }
    
    const result = await sendSurgeryConsent(phone_number, appointment_data);
    res.json(result);
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        service: 'RUBIO GARCÍA DENTAL WhatsApp Service',
        version: '1.0.0',
        uptime: process.uptime()
    });
});

// Start server and WhatsApp connection
app.listen(PORT, () => {
    console.log(`🚀 RUBIO GARCÍA DENTAL WhatsApp Service running on port ${PORT}`);
    console.log(`📡 FastAPI Backend: ${FASTAPI_URL}`);
    
    // Initialize WhatsApp connection
    initWhatsApp();
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('👋 Shutting down WhatsApp service...');
    if (sock) {
        sock.end();
    }
    process.exit(0);
});