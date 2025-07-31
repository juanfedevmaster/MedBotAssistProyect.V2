import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
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

interface ChatHistoryItem {
  interactionId: number;
  userId: number;
  timestamp: string;
  interactionType: string | null;
  userMessage: string;
  botResponse: string;
  userName: string;
}

const FloatingChat: React.FC = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if we're on login or register pages
  const isOnAuthPage = location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/';

  // Generate a unique conversation ID
  const generateConversationId = () => {
    return TokenManager.generateNewConversationId();
  };

  // Function to convert server timestamp to local date
  const convertToLocalTime = (timestamp: string): Date => {
    
    // Handle empty or null timestamp
    if (!timestamp) {
      return new Date();
    }
    
    // Create a date from the timestamp
    let date = new Date(timestamp);
    
    if (!isNaN(date.getTime())) {
      // SPECIFIC CORRECTION: Detect server timezone problem
      // Problem analysis:
      // - Current date: 29/07/2025
      // - You sent at 7:16 PM on 29/07/2025 (19:16) GMT-5
      // - Correct UTC should be: 29/07/2025 19:16 + 5 hours = 30/07/2025 00:16 UTC
      // - Server saved: 30/07/2025 05:16 UTC (correct date but incorrect time)
      // - Correction needed: Subtract 5 hours to return to 29/07/2025 19:16 local
      
      const originalHour = date.getUTCHours();
      
      // Subtract 5 hours to correct from 05:16 UTC to 00:16 UTC, 
      // which in your GMT-5 timezone will be 19:16 of the previous day
      const correctionHours = -5;
      const correctedDate = new Date(date.getTime() + (correctionHours * 60 * 60 * 1000));
      
      return correctedDate;
    }
    
    // If there are problems with parsing, try different formats
    try {
      // Try with ISO format if it doesn't have timezone information
      if (!timestamp.includes('Z') && !timestamp.includes('+') && !timestamp.includes('-')) {
        date = new Date(timestamp + 'Z');
        if (!isNaN(date.getTime())) {
          return date;
        }
      }
      
      // Try direct parsing
      date = new Date(timestamp);
      if (!isNaN(date.getTime())) {
        return date;
      }
      
    } catch (error) {
      console.error('Error parsing timestamp:', timestamp, error);
    }
    
    return new Date(); // Fallback to current date
  };

  // Load chat history from server
  const loadChatHistory = useCallback(async () => {
    try {
      const token = TokenManager.getToken();
      const username = TokenManager.getUsername();
      const convId = TokenManager.getConversationId();
      
      if (!token) {
        return;
      }

      if (!username || !convId) {
        return;
      }

      // Build URL with parameters
      const historyUrl = `${API_ENDPOINTS.CHAT_HISTORY}?userName=${encodeURIComponent(username)}&conversationId=${encodeURIComponent(convId)}`;
      
      const response = await fetch(historyUrl, {
        method: 'GET',
        headers: TokenManager.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const historyData: ChatHistoryItem[] = await response.json();
      
      // Convert history to chat message format
      const historyMessages: ChatMessage[] = [];
      
      historyData.forEach((item) => {
        // Convert timestamp to browser local date
        const localTimestamp = convertToLocalTime(item.timestamp);
        
        // Add user message
        historyMessages.push({
          id: `history_user_${item.interactionId}`,
          message: item.userMessage,
          isUser: true,
          timestamp: localTimestamp
        });
        
        // Add bot response
        historyMessages.push({
          id: `history_bot_${item.interactionId}`,
          message: item.botResponse,
          isUser: false,
          timestamp: localTimestamp
        });
      });

      // Ensure all timestamps are Date objects before setting messages
      const messagesWithValidDates = historyMessages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp instanceof Date ? msg.timestamp : new Date(msg.timestamp)
      }));
            
      // Set history messages
      setMessages(messagesWithValidDates);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Initialize conversation ID when component mounts and check authentication
  useEffect(() => {
    const initializeChat = async () => {
      // Only proceed if not on authentication pages
      if (isOnAuthPage) {
        console.log('On authentication page, skipping chat initialization');
        setIsAuthenticated(false);
        return;
      }
      
      const existingConvId = TokenManager.getConversationId();
      const token = TokenManager.getToken();
      const username = TokenManager.getUsername();
      const doctorId = TokenManager.getDoctorId();
      
      console.log('Auth check details:', {
        token: token ? `${token.substring(0, 10)}...` : 'null',
        tokenExists: !!token,
        username: username || 'null',
        doctorId: doctorId || 'null',
        conversationId: existingConvId || 'null'
      });
      
      // Simple authentication check - require token and username
      const isUserAuthenticated = !!(token && username);
      console.log('Authentication result:', isUserAuthenticated);
      
      setIsAuthenticated(isUserAuthenticated);
      
      if (isUserAuthenticated && existingConvId) {
        setConversationId(existingConvId);
        console.log('Loading history because user is authenticated and conversation_id exists');
        await loadChatHistory();
      } else if (isUserAuthenticated) {
        console.log('User authenticated but no conversation_id, generating new one');
        const newConvId = generateConversationId();
        setConversationId(newConvId);
      } else {
        console.log('User not authenticated, chat will be hidden');
      }
    };

    initializeChat();
  }, [loadChatHistory, location.pathname, isOnAuthPage]);

  // Auto scroll to end of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clear only chat messages (for logout, keeps conversation_id)
  const clearChatMessages = useCallback(() => {
    setMessages([]);
    setInputMessage('');
    // DO NOT generate new conversation_id, keep current one for recovery
  }, []);

  const clearChat = useCallback(async () => {
    setMessages([]);
    setInputMessage('');
    const newConvId = generateConversationId();
    setConversationId(newConvId);
  }, []);

  // Clear chat when user logs out or logs in
  useEffect(() => {
    const handleStorageChange = async () => {
      const token = TokenManager.getToken();
      setIsAuthenticated(!!token);
      
      if (!token) {
        // User logged out, only clear messages (keep conversation_id)
        setIsOpen(false); // Close the chat
        clearChatMessages();
      }
    };

    const handleUserLogout = async () => {
      // User logged out, clear chat messages and hide
      setIsAuthenticated(false);
      setIsOpen(false); // Close the chat
      clearChatMessages();
    };

    const handleUserLogin = async () => {
      // User logged in
      console.log('User logged in');
      
      // Update authentication state
      setIsAuthenticated(true);
      
      // Only generate new conversation_id if there's no previous one
      const existingConvId = TokenManager.getConversationId();
      if (!existingConvId) {
        // No previous conversation_id, generate a new one
        const newConvId = generateConversationId();
        setConversationId(newConvId);
        // Clear messages for new conversation
        clearChatMessages();
      } else {
        setConversationId(existingConvId);
        // Load chat history
        await loadChatHistory();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('userLogout', handleUserLogout);
    window.addEventListener('userLoginSuccess', handleUserLogin);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('userLogout', handleUserLogout);
      window.removeEventListener('userLoginSuccess', handleUserLogin);
    };
  }, [clearChat, clearChatMessages, loadChatHistory]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const currentTime = new Date();

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      message: inputMessage.trim(),
      isUser: true,
      timestamp: currentTime
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

      const botResponseTime = new Date();

      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        message: data.response,
        isUser: false,
        timestamp: botResponseTime
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update conversation_id if server sends a new one
      if (data.conversation_id && data.conversation_id !== conversationId) {
        setConversationId(data.conversation_id);
        TokenManager.saveConversationId(data.conversation_id);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorTime = new Date();
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        message: 'Sorry, an error occurred while processing your message. Please try again.',
        isUser: false,
        timestamp: errorTime
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
    // If receiving a string, convert to Date
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    // Ensure the date is valid
    if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
      return '00:00';
    }
    
    // Format complete date with day, month, year and time
    const formattedDateTime = date.toLocaleString('es-CO', {
      day: '2-digit',
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
    
    return formattedDateTime;
  };

  console.log('=== RENDER CHECK ===');
  console.log('Current path:', location.pathname);
  console.log('Is on auth page:', isOnAuthPage);
  console.log('isAuthenticated:', isAuthenticated);
  console.log('Will show chat:', !isOnAuthPage && isAuthenticated);

  // Don't render chat on login/register pages or if not authenticated
  if (isOnAuthPage || !isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Floating button */}
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
          title="AI Chat"
        >
          <i className={`bi ${isOpen ? 'bi-x-lg' : 'bi-chat-dots'} fs-4`}></i>
        </button>
      </div>

      {/* Chat window */}
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
          {/* Chat header */}
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
                title="Clear chat"
                style={{ padding: '2px 6px' }}
              >
                <i className="bi bi-trash3 fs-6"></i>
              </button>
              <button
                className="btn btn-sm btn-outline-light"
                onClick={() => setIsOpen(false)}
                title="Close chat"
                style={{ padding: '2px 6px' }}
              >
                <i className="bi bi-x-lg fs-6"></i>
              </button>
            </div>
          </div>

          {/* Message area */}
          <div
            className="flex-grow-1 overflow-auto p-3"
            style={{ backgroundColor: '#f8f9fa' }}
          >
            {messages.length === 0 ? (
              <div className="text-center text-muted mt-5">
                <i className="bi bi-chat-heart display-4 mb-3"></i>
                <p>Hello! I'm your virtual medical assistant.</p>
                <p className="small">Write a message to get started.</p>
              </div>
            ) : (
              messages.map((msg) => {
                // Log for rendering debugging
                console.log('Rendering message:', {
                  id: msg.id,
                  timestamp: msg.timestamp,
                  timestampType: typeof msg.timestamp,
                  isDate: msg.timestamp instanceof Date
                });
                
                return (
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
                      style={{ fontSize: '0.7rem', lineHeight: '1.2' }}
                    >
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
                );
              })
            )}
            
            {isLoading && (
              <div className="d-flex justify-content-start mb-3">
                <div className="bg-white border rounded-3 px-3 py-2">
                  <div className="d-flex align-items-center">
                    <div className="spinner-border spinner-border-sm me-2" role="status">
                      <span className="visually-hidden">Writing...</span>
                    </div>
                    <span className="small text-muted">Writing...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Message input */}
          <div className="p-3 border-top bg-white rounded-bottom">
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder="Type your message..."
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
