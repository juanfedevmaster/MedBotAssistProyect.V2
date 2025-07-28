import React, { useState, useEffect, useRef, useCallback } from 'react';
import { API_ENDPOINTS } from '../config/endpoints';
import ApiService from '../services/apiService';
import TokenManager from '../utils/tokenManager';

interface ChatMessage {
  id: string;
  message: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  agent_used_tools: boolean;
  available_tools: string[];
  status: string;
  timestamp: string;
}

const FloatingChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generar un conversation ID único
  const generateConversationId = () => {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Inicializar conversation ID al montar el componente
  useEffect(() => {
    const initializeChat = async () => {
      const existingConvId = sessionStorage.getItem('chatConversationId');
      if (existingConvId) {
        setConversationId(existingConvId);
      } else {
        const newConvId = generateConversationId();
        setConversationId(newConvId);
        sessionStorage.setItem('chatConversationId', newConvId);
      }
    };

    initializeChat();
  }, []);

  // Scroll automático al final de los mensajes
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const clearChat = useCallback(async () => {
    setMessages([]);
    setInputMessage('');
    const newConvId = generateConversationId();
    setConversationId(newConvId);
    sessionStorage.setItem('chatConversationId', newConvId);
  }, []);

  // Limpiar chat cuando el usuario hace logout
  useEffect(() => {
    const handleStorageChange = async () => {
      const token = TokenManager.getToken();
      if (!token) {
        // Usuario hizo logout, limpiar chat
        await clearChat();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [clearChat]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      message: inputMessage.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await ApiService.aiApiFetch(API_ENDPOINTS.AI_CHAT, {
        method: 'POST',
        body: JSON.stringify({
          message: userMessage.message,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        message: data.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Actualizar conversation_id si el servidor envía uno nuevo
      if (data.conversation_id && data.conversation_id !== conversationId) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('chatConversationId', data.conversation_id);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        message: 'Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo.',
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Botón flotante */}
      <div
        className="position-fixed"
        style={{
          bottom: '20px',
          right: '20px',
          zIndex: 1000,
        }}
      >
        <button
          className="btn btn-primary rounded-circle shadow-lg d-flex align-items-center justify-content-center"
          style={{
            width: '60px',
            height: '60px',
            backgroundColor: '#405de6',
            border: 'none',
            transition: 'all 0.3s ease',
          }}
          onClick={() => setIsOpen(!isOpen)}
          title="Chat con IA"
        >
          <i className={`bi ${isOpen ? 'bi-x-lg' : 'bi-chat-dots'} fs-4`}></i>
        </button>
      </div>

      {/* Ventana de chat */}
      {isOpen && (
        <div
          className="position-fixed bg-white rounded-3 shadow-lg"
          style={{
            bottom: '90px',
            right: '20px',
            width: '420px',
            height: '600px',
            zIndex: 999,
            border: '1px solid #dee2e6',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header del chat */}
          <div
            className="d-flex align-items-center justify-content-between p-3 rounded-top"
            style={{ backgroundColor: '#405de6', color: 'white' }}
          >
            <div className="d-flex align-items-center">
              <i className="bi bi-robot me-2 fs-5"></i>
              <h6 className="mb-0 fw-bold">MedBot Assistant</h6>
            </div>
            <div className="d-flex align-items-center gap-2">
              <button
                className="btn btn-sm btn-outline-light"
                onClick={clearChat}
                title="Limpiar chat"
                style={{ padding: '2px 6px' }}
              >
                <i className="bi bi-trash3 fs-6"></i>
              </button>
              <button
                className="btn btn-sm btn-outline-light"
                onClick={() => setIsOpen(false)}
                title="Cerrar chat"
                style={{ padding: '2px 6px' }}
              >
                <i className="bi bi-x-lg fs-6"></i>
              </button>
            </div>
          </div>

          {/* Área de mensajes */}
          <div
            className="flex-grow-1 overflow-auto p-3"
            style={{ backgroundColor: '#f8f9fa' }}
          >
            {messages.length === 0 ? (
              <div className="text-center text-muted mt-5">
                <i className="bi bi-chat-heart display-4 mb-3"></i>
                <p>¡Hola! Soy tu asistente médico virtual.</p>
                <p className="small">Escribe un mensaje para comenzar.</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-3 d-flex ${msg.isUser ? 'justify-content-end' : 'justify-content-start'}`}
                >
                  <div
                    className={`rounded-3 px-3 py-2 max-w-75 ${
                      msg.isUser
                        ? 'bg-primary text-white'
                        : 'bg-white border'
                    }`}
                    style={{
                      maxWidth: '80%',
                      wordWrap: 'break-word',
                    }}
                  >
                    <div className="small mb-1">{msg.message}</div>
                    <div
                      className={`text-end small ${
                        msg.isUser ? 'text-white-50' : 'text-muted'
                      }`}
                      style={{ fontSize: '0.75rem' }}
                    >
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="d-flex justify-content-start mb-3">
                <div className="bg-white border rounded-3 px-3 py-2">
                  <div className="d-flex align-items-center">
                    <div className="spinner-border spinner-border-sm me-2" role="status">
                      <span className="visually-hidden">Escribiendo...</span>
                    </div>
                    <span className="small text-muted">Escribiendo...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input de mensaje */}
          <div className="p-3 border-top bg-white rounded-bottom">
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder="Escribe tu mensaje..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                style={{ border: '1px solid #ced4da' }}
              />
              <button
                className="btn"
                style={{ backgroundColor: '#405de6', color: 'white' }}
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
              >
                <i className="bi bi-send-fill"></i>
              </button>
            </div>
            <div className="text-center mt-2">
              <small className="text-muted">
                ID: {conversationId.split('_')[1]}...
              </small>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChat;
