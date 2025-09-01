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

// Handle incoming messages with AI integration and button responses
async function handleIncomingMessage(message) {
    try {
        const phoneNumber = message.key.remoteJid.replace('@s.whatsapp.net', '');
        const messageText = extractMessageText(message);
        
        if (!messageText) return;

        console.log(`📨 Message from ${phoneNumber}: ${messageText}`);

        // Check if it's a button response
        if (message.message.buttonsResponseMessage) {
            await handleButtonResponse(phoneNumber, message.message.buttonsResponseMessage);
            return;
        }

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

// Handle button responses
async function handleButtonResponse(phoneNumber, buttonResponse) {
    try {
        const buttonId = buttonResponse.selectedButtonId;
        const selectedText = buttonResponse.selectedDisplayText;
        
        console.log(`🔘 Button pressed by ${phoneNumber}: ${buttonId} (${selectedText})`);

        // Process the button response through backend
        const response = await axios.post(`${FASTAPI_URL}/api/whatsapp/button-response`, {
            phone_number: phoneNumber,
            button_id: buttonId,
            selected_text: selectedText,
            timestamp: new Date().toISOString()
        });

        if (response.data.reply_message) {
            await sendMessage(phoneNumber, response.data.reply_message);
        }

        // Handle specific button actions
        switch (buttonId) {
            case 'confirm_appointment':
                await sendMessage(phoneNumber, '✅ Su cita ha sido confirmada. ¡Le esperamos!');
                break;
                
            case 'cancel_appointment':
                await sendMessage(phoneNumber, '❌ Su cita ha sido cancelada. ¿Desea reprogramar? Responda BUSCAR CITA o CONTACTAR DESPUÉS');
                break;
                
            case 'reschedule_appointment':
                await sendMessage(phoneNumber, '📅 Para reprogramar su cita, ¿prefiere horario de MAÑANA o TARDE?');
                break;
                
            case 'consent_accept':
                await sendMessage(phoneNumber, '✅ Consentimiento registrado correctamente. Gracias por su confianza.');
                break;
                
            case 'consent_explain':
                await sendMessage(phoneNumber, '👨‍⚕️ Nuestro equipo se pondrá en contacto para explicarle el tratamiento detalladamente.');
                break;
                
            case 'lopd_accept':
                await sendMessage(phoneNumber, '✅ Consentimiento LOPD registrado. Sus datos están protegidos según la normativa vigente.');
                break;
                
            case 'lopd_info':
                await sendMessage(phoneNumber, '📞 Nuestro equipo le proporcionará más información sobre el tratamiento de sus datos.');
                break;
        }

    } catch (error) {
        console.error('❌ Error handling button response:', error);
        await sendMessage(phoneNumber, 'Error procesando su respuesta. Contacte con la clínica: 916 410 841');
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

// Send appointment reminder with interactive buttons
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

Por favor, confirme su asistencia:`;

        // Send message with interactive buttons
        return await sendMessageWithButtons(phoneNumber, reminderMessage, [
            { id: 'confirm_appointment', title: '✅ CONFIRMO' },
            { id: 'cancel_appointment', title: '❌ CANCELO' },
            { id: 'reschedule_appointment', title: '📅 CAMBIO' }
        ]);
        
    } catch (error) {
        console.error('❌ Error sending reminder:', error);
        return { success: false, error: error.message };
    }
}

// Send message with interactive buttons
async function sendMessageWithButtons(phoneNumber, text, buttons) {
    try {
        if (!sock || connectionStatus !== 'connected') {
            throw new Error('WhatsApp not connected');
        }

        const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`;
        
        // Prepare buttons in the correct format for Baileys
        const buttonMessage = {
            text: text,
            buttons: buttons.map(btn => ({
                buttonId: btn.id,
                buttonText: { displayText: btn.title },
                type: 1
            })),
            headerType: 1
        };

        await sock.sendMessage(jid, buttonMessage);

        console.log(`✅ Interactive message sent to ${phoneNumber}`);
        return { success: true };

    } catch (error) {
        console.error('❌ Error sending interactive message:', error);
        return { success: false, error: error.message };
    }
}

// Send message with PDF attachment
async function sendMessageWithDocument(phoneNumber, text, documentPath, fileName) {
    try {
        if (!sock || connectionStatus !== 'connected') {
            throw new Error('WhatsApp not connected');
        }

        const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`;
        const fs = require('fs');
        
        // Check if document exists
        if (!fs.existsSync(documentPath)) {
            throw new Error('Document not found');
        }

        await sock.sendMessage(jid, {
            document: fs.readFileSync(documentPath),
            fileName: fileName,
            mimetype: 'application/pdf',
            caption: text
        });

        console.log(`✅ Document sent to ${phoneNumber}: ${fileName}`);
        return { success: true };

    } catch (error) {
        console.error('❌ Error sending document:', error);
        return { success: false, error: error.message };
    }
}

// Send consent form with interactive buttons and PDF
async function sendConsentForm(phoneNumber, consentData) {
    try {
        const { patient_name, treatment_name, consent_type, pdf_path } = consentData;
        
        let consentMessage = '';
        let buttons = [];
        
        if (consent_type === 'treatment') {
            consentMessage = `🦷 CONSENTIMIENTO INFORMADO - RUBIO GARCÍA DENTAL

👤 Paciente: ${patient_name}
🩺 Tratamiento: ${treatment_name}

📋 Adjunto encontrará el consentimiento informado para su tratamiento de ${treatment_name}.

Por favor, lea detenidamente el documento y responda:`;

            buttons = [
                { id: 'consent_accept', title: '✅ He leído y doy mi consentimiento' },
                { id: 'consent_explain', title: '❓ Prefiero que me lo expliquen de nuevo' }
            ];
        } else if (consent_type === 'lopd') {
            consentMessage = `🦷 PROTECCIÓN DE DATOS - RUBIO GARCÍA DENTAL

👤 Paciente: ${patient_name}

📋 Como es su primera visita, necesitamos su consentimiento para el tratamiento de sus datos personales según la LOPD.

Adjunto encontrará el documento informativo.`;

            buttons = [
                { id: 'lopd_accept', title: '✅ Acepto el tratamiento de mis datos' },
                { id: 'lopd_info', title: '❓ Necesito más información' }
            ];
        }

        // Send document first, then interactive message
        if (pdf_path) {
            await sendMessageWithDocument(phoneNumber, '', pdf_path, `${consent_type}_${patient_name}.pdf`);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
        }
        
        return await sendMessageWithButtons(phoneNumber, consentMessage, buttons);
        
    } catch (error) {
        console.error('❌ Error sending consent form:', error);
        return { success: false, error: error.message };
    }
}

// Send first visit survey
async function sendFirstVisitSurvey(phoneNumber, patientData) {
    try {
        const { patient_name } = patientData;
        
        const surveyMessage = `🦷 ENCUESTA PRIMERA VISITA - RUBIO GARCÍA DENTAL

👤 Paciente: ${patient_name}

Para brindarle la mejor atención, por favor complete esta breve encuesta:

1️⃣ ¿Cuál es el motivo principal de su consulta?
2️⃣ ¿Siente dolor actualmente? (1-10)
3️⃣ ¿Tiene alguna alergia conocida?
4️⃣ ¿Toma algún medicamento actualmente?

Responda con un mensaje describiendo cada punto.`;

        return await sendMessage(phoneNumber, surveyMessage);
        
    } catch (error) {
        console.error('❌ Error sending survey:', error);
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

// Add new endpoints for consent forms and surveys
app.post('/send-consent', async (req, res) => {
    const { phone_number, consent_data } = req.body;
    
    if (!phone_number || !consent_data) {
        return res.status(400).json({ error: 'Phone number and consent data are required' });
    }
    
    const result = await sendConsentForm(phone_number, consent_data);
    res.json(result);
});

app.post('/send-survey', async (req, res) => {
    const { phone_number, patient_data } = req.body;
    
    if (!phone_number || !patient_data) {
        return res.status(400).json({ error: 'Phone number and patient data are required' });
    }
    
    const result = await sendFirstVisitSurvey(phone_number, patient_data);
    res.json(result);
});

app.post('/send-interactive', async (req, res) => {
    const { phone_number, message, buttons } = req.body;
    
    if (!phone_number || !message || !buttons) {
        return res.status(400).json({ error: 'Phone number, message and buttons are required' });
    }
    
    const result = await sendMessageWithButtons(phone_number, message, buttons);
    res.json(result);
});

app.post('/send-document', async (req, res) => {
    const { phone_number, message, document_path, file_name } = req.body;
    
    if (!phone_number || !document_path || !file_name) {
        return res.status(400).json({ error: 'Phone number, document path and file name are required' });
    }
    
    const result = await sendMessageWithDocument(phone_number, message || '', document_path, file_name);
    res.json(result);
});

// Force reconnection
app.post('/reconnect', async (req, res) => {
    try {
        console.log('🔄 Force reconnection requested...');
        
        // Close current connection if exists
        if (sock) {
            try {
                sock.end();
            } catch (e) {
                console.log('Previous connection closed with error:', e.message);
            }
        }
        
        // Reset connection status
        connectionStatus = 'disconnected';
        qrCodeData = null;
        sock = null;
        
        // Reinitialize WhatsApp connection
        setTimeout(() => {
            initWhatsApp();
        }, 1000);
        
        res.json({ 
            success: true, 
            message: 'Reconnection initiated',
            status: 'reconnecting'
        });
        
    } catch (error) {
        console.error('❌ Error during reconnection:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
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