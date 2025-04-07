document.addEventListener('DOMContentLoaded', function() {
    const chatbot = document.getElementById('chatbot');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotSubmit = document.getElementById('chatbot-submit');
    let isTyping = false;
    let isInitialized = false;
    let csrfToken = null;
    
    // Get CSRF token
    function updateCsrfToken() {
        const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenElement) {
            csrfToken = tokenElement.value;
            return true;
        }
        return false;
    }
    
    // Add typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    chatbotMessages.appendChild(typingIndicator);
    typingIndicator.style.display = 'none';

    // Initially minimize chatbot
    chatbot.classList.add('chatbot-minimized');
    chatbotToggle.innerHTML = '<i class="fas fa-comment"></i>';
    
    // Add welcome message styles
    const style = document.createElement('style');
    style.textContent = `
        .typing-indicator {
            display: flex;
            padding: 10px;
            margin: 5px;
            background: #f0f0f0;
            border-radius: 15px;
            width: fit-content;
            margin-right: auto;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            background: #606060;
            border-radius: 50%;
            margin: 0 2px;
            animation: bounce 1.3s linear infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.15s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.3s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-4px); }
        }
        .chatbot-message {
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        .bot-message {
            background: #f8f9fa;
            padding: 12px 15px;
            border-radius: 15px;
            margin: 5px;
            max-width: 80%;
            margin-right: auto;
            border-left: 3px solid transparent;
        }
        .user-message {
            background: #007bff;
            color: white;
            padding: 12px 15px;
            border-radius: 15px;
            margin: 5px;
            max-width: 80%;
            margin-left: auto;
        }
        .cuisine-question {
            border-left-color: #28a745;
        }
        .location-question {
            border-left-color: #ffc107;
        }
        .results-message {
            border-left-color: #17a2b8;
        }
        .chatbot-input:disabled {
            background-color: #f8f9fa;
            cursor: not-allowed;
        }
        .chatbot-submit:disabled {
            opacity: 0.65;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(style);

    // Toggle chatbot visibility
    chatbotToggle.addEventListener('click', function() {
        chatbot.classList.toggle('chatbot-minimized');
        if (chatbot.classList.contains('chatbot-minimized')) {
            chatbotToggle.innerHTML = '<i class="fas fa-comment"></i>';
        } else {
            chatbotToggle.innerHTML = '<i class="fas fa-times"></i>';
            chatbotInput.focus();
            
            // Initialize chatbot if not done yet
            if (!isInitialized) {
                if (!updateCsrfToken()) {
                    console.error('CSRF token not found');
                    addMessage('bot', 'I\'m having trouble initializing. Please refresh the page.');
                    return;
                }
                
                isInitialized = true;
                fetch('/restaurants/chatbot/', {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.type === 'text') {
                        addMessage('bot', data.content);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    isInitialized = false; // Allow retry
                    addMessage('bot', 'I\'m having trouble connecting. Please try again later.');
                });
            }
        }
    });

    // Handle message submission
    function sendMessage(e) {
        e.preventDefault();
        const message = chatbotInput.value.trim();
        if (message) {
            // Add user message
            addMessage('user', message);
            chatbotInput.value = '';

            // Disable input while processing
            chatbotInput.disabled = true;
            chatbotSubmit.disabled = true;
            
            if (!updateCsrfToken()) {
                console.error('CSRF token not found');
                addMessage('bot', 'I\'m having trouble processing your request. Please refresh the page.');
                return;
            }
            
            // Send to backend
            fetch('/restaurants/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Re-enable input
                chatbotInput.disabled = false;
                chatbotSubmit.disabled = false;
                chatbotInput.focus();
                
                if (data.type === 'restaurants') {
                    // Display restaurant cards
                    let restaurantsHtml = '<div class="chatbot-restaurants">';
                    if (!data.content || data.content.length === 0) {
                        if (data.message) {
                            addMessage('bot', data.message);
                        } else {
                            addMessage('bot', 'I couldn\'t find any restaurants matching your criteria. Try different keywords!');
                        }
                    } else {
                        if (data.message) {
                            addMessage('bot', data.message);
                        }
                        data.content.forEach(restaurant => {
                            restaurantsHtml += `
                                <div class="chatbot-restaurant-card">
                                    ${restaurant.image_url ? 
                                        `<img src="${restaurant.image_url}" alt="${restaurant.name}" onerror="this.onerror=null;this.src='/static/images/default-restaurant.png';">` : 
                                        '<div class="no-image"><i class="fas fa-utensils"></i></div>'
                                    }
                                    <div class="restaurant-info">
                                        <h4>${restaurant.name}</h4>
                                        <p><i class="fas fa-map-marker-alt"></i> ${restaurant.location}</p>
                                        <p><i class="fas fa-utensils"></i> ${restaurant.cuisine}</p>
                                        <p><i class="fas fa-star"></i> ${restaurant.rating}/5</p>
                                        ${restaurant.price_range ? 
                                            `<p><i class="fas fa-dollar-sign"></i> ${'$'.repeat(restaurant.price_range)}</p>` :
                                            ''
                                        }
                                        <a href="/restaurants/${restaurant.id}/" class="btn btn-primary btn-sm">View Details</a>
                                    </div>
                                </div>
                            `;
                        });
                        restaurantsHtml += '</div>';
                        addMessage('bot', restaurantsHtml);
                    }
                } else if (data.type === 'text') {
                    // Display text message
                    addMessage('bot', data.content);
                } else {
                    throw new Error('Invalid response type from server');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Re-enable input
                chatbotInput.disabled = false;
                chatbotSubmit.disabled = false;
                chatbotInput.focus();
                
                addMessage('bot', 'I apologize, but I\'m having trouble processing your request right now. Please try asking in a different way or try again later.');
            });
        }
    }

    chatbotSubmit.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(e);
        }
    });

    // Add message to chat
    function showTypingIndicator() {
        if (!isTyping) {
            isTyping = true;
            typingIndicator.style.display = 'flex';
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    }

    function hideTypingIndicator() {
        if (isTyping) {
            isTyping = false;
            typingIndicator.style.display = 'none';
        }
    }

    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        if (sender === 'bot') {
            showTypingIndicator();
            // Vary typing delay based on content length
            const typingDelay = Math.min(Math.max(content.length * 20, 500), 2000);
            
            setTimeout(() => {
                hideTypingIndicator();
                messageDiv.innerHTML = content;
                chatbotMessages.appendChild(messageDiv);
                
                // Add visual cue for conversation flow
                if (content.includes('What type of cuisine')) {
                    messageDiv.classList.add('cuisine-question');
                } else if (content.includes('Which location')) {
                    messageDiv.classList.add('location-question');
                } else if (content.includes('Here are some restaurants')) {
                    messageDiv.classList.add('results-message');
                }
                
                // Animate message appearance
                setTimeout(() => {
                    messageDiv.style.opacity = '1';
                    messageDiv.style.transform = 'translateY(0)';
                }, 100);
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                chatbotInput.focus();
            }, typingDelay);
        } else {
            messageDiv.innerHTML = content;
            chatbotMessages.appendChild(messageDiv);
            // Animate message appearance
            setTimeout(() => {
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            }, 100);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
