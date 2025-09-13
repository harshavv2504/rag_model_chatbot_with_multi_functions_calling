/**
 * ChatClient - Handles WebSocket communication and UI interactions
 */
class ChatClient {
    constructor() {
        this.websocket = null;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.inputHint = document.getElementById('inputHint');
        
        this.currentAiMessage = null;
        this.sessionEnded = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connect();
    }
    
    setupEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.handleSendMessage();
        });
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        // Input validation
        this.messageInput.addEventListener('input', () => {
            this.validateInput();
        });
        
        // Focus input when page loads
        window.addEventListener('load', () => {
            if (!this.sessionEnded) {
                this.messageInput.focus();
            }
        });
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.onConnectionOpen();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleIncomingMessage(JSON.parse(event.data));
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.onConnectionClose();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onConnectionError();
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.onConnectionError();
        }
    }
    
    onConnectionOpen() {
        this.updateStatus('connected', 'Connected');
        this.enableInput();
        this.hideLoadingOverlay();
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
    }
    
    onConnectionClose() {
        this.updateStatus('connecting', 'Disconnected');
        this.disableInput();
        
        if (!this.sessionEnded && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
        }
    }
    
    onConnectionError() {
        this.updateStatus('error', 'Connection Error');
        this.disableInput();
        
        if (!this.sessionEnded && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        this.reconnectAttempts++;
        this.updateStatus('connecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.sessionEnded) {
                this.connect();
            }
        }, this.reconnectDelay);
        
        // Exponential backoff
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
    }
    
    updateStatus(type, text) {
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        const statusText = this.statusIndicator.querySelector('.status-text');
        
        statusDot.className = `status-dot ${type}`;
        statusText.textContent = text;
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.focus();
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
    }
    
    hideLoadingOverlay() {
        this.loadingOverlay.classList.add('hidden');
        setTimeout(() => {
            this.loadingOverlay.style.display = 'none';
        }, 300);
    }
    
    validateInput() {
        const message = this.messageInput.value.trim();
        const isValid = message.length > 0 && message.length <= 1000;
        
        this.sendButton.disabled = !isValid || this.sessionEnded || 
                                   this.websocket?.readyState !== WebSocket.OPEN;
        
        // Update character count hint
        if (message.length > 900) {
            this.inputHint.textContent = `${message.length}/1000 characters`;
            this.inputHint.style.color = message.length > 1000 ? 'var(--error-color)' : 'var(--warning-color)';
        } else {
            this.inputHint.textContent = "Press Enter to send • Type 'exit', 'quit', or 'bye' to end chat";
            this.inputHint.style.color = 'var(--text-muted)';
        }
    }
    
    handleSendMessage() {
        if (this.sessionEnded || this.websocket?.readyState !== WebSocket.OPEN) {
            return;
        }
        
        const message = this.messageInput.value.trim();
        
        if (!message) {
            this.showError('💭 Please enter a message.');
            return;
        }
        
        if (message.length > 1000) {
            this.showError('Message is too long. Please keep it under 1000 characters.');
            return;
        }
        
        // Display user message immediately
        this.displayMessage(message, true);
        
        // Send message via WebSocket
        const messageData = {
            type: 'user_message',
            content: message,
            metadata: {
                timestamp: Date.now()
            }
        };
        
        try {
            this.websocket.send(JSON.stringify(messageData));
            this.messageInput.value = '';
            this.validateInput();
        } catch (error) {
            console.error('Failed to send message:', error);
            this.showError('Failed to send message. Please try again.');
        }
    }
    
    handleIncomingMessage(data) {
        const { type, content, metadata } = data;
        
        switch (type) {
            case 'system_message':
                this.displaySystemMessage(content);
                break;
                
            case 'ai_message':
                // Handle complete AI messages (like initial greeting)
                this.displayMessage(content, false);
                break;
                
            case 'ai_typing':
                this.showTypingIndicator();
                break;
                
            case 'ai_chunk':
                this.appendToAiMessage(content, metadata);
                break;
                
            case 'ai_complete':
                this.completeAiMessage();
                break;
                
            case 'error':
                this.hideTypingIndicator();
                this.showError(content);
                break;
                
            case 'session_end':
                this.handleSessionEnd(content);
                break;
                
            default:
                console.warn('Unknown message type:', type);
        }
    }
    
    displayMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
        messageDiv.textContent = content;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    displaySystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        
        // Handle multiline system messages
        const lines = content.split('\n');
        lines.forEach((line, index) => {
            if (index > 0) {
                messageDiv.appendChild(document.createElement('br'));
            }
            messageDiv.appendChild(document.createTextNode(line));
        });
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.hideTypingIndicator(); // Remove any existing indicator
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <span>AI is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    appendToAiMessage(content, metadata = {}) {
        // Check if this is a sentence chunk based on metadata
        const isSentence = metadata && (metadata.is_sentence === true || metadata.is_sentence === "true");
        
        if (isSentence) {
            // Create a new message bubble for each sentence
            this.hideTypingIndicator();
            const messageDiv = this.displayMessage(content.trim(), false);
            
            // Add sentence chunk styling
            messageDiv.classList.add('sentence-chunk');
            
            // Add first/last chunk classes for better spacing
            if (metadata.chunk_index === 0) {
                messageDiv.classList.add('first-chunk');
            }
            
            this.scrollToBottom();
        } else {
            // For non-sentence chunks, append to current message
            if (!this.currentAiMessage) {
                this.hideTypingIndicator();
                this.currentAiMessage = this.displayMessage('', false);
            }
            
            this.currentAiMessage.textContent += content;
            this.scrollToBottom();
        }
    }
    
    completeAiMessage() {
        this.hideTypingIndicator();
        this.currentAiMessage = null;
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error-message';
        errorDiv.textContent = message;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    handleSessionEnd(content) {
        this.sessionEnded = true;
        this.disableInput();
        this.updateStatus('error', 'Session Ended');
        
        // Display goodbye message
        const goodbyeDiv = document.createElement('div');
        goodbyeDiv.className = 'message system-message';
        
        // Handle multiline goodbye messages
        const lines = content.split('\n\n');
        lines.forEach((line, index) => {
            if (index > 0) {
                goodbyeDiv.appendChild(document.createElement('br'));
                goodbyeDiv.appendChild(document.createElement('br'));
            }
            goodbyeDiv.appendChild(document.createTextNode(line));
        });
        
        this.chatMessages.appendChild(goodbyeDiv);
        this.scrollToBottom();
        
        // Update input hint
        this.inputHint.textContent = 'Chat session ended. Refresh the page to start a new conversation.';
        this.inputHint.style.color = 'var(--text-muted)';
        
        // Close WebSocket connection
        if (this.websocket) {
            this.websocket.close();
        }
    }
    
    scrollToBottom() {
        // Use requestAnimationFrame for smooth scrolling
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        });
    }
}

// Initialize the chat client when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatClient();
});