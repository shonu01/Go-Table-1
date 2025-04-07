document.addEventListener('DOMContentLoaded', function() {
    const chatbot = document.getElementById('chatbot');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotSubmit = document.getElementById('chatbot-submit');

    // Toggle chatbot visibility
    chatbotToggle.addEventListener('click', function() {
        chatbot.classList.toggle('chatbot-minimized');
        if (chatbot.classList.contains('chatbot-minimized')) {
            chatbotToggle.innerHTML = '<i class="fas fa-comment"></i>';
        } else {
            chatbotToggle.innerHTML = '<i class="fas fa-times"></i>';
            chatbotInput.focus();
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

            // Send to backend
            fetch('/restaurants/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.type === 'restaurants') {
                    // Display restaurant cards
                    let restaurantsHtml = '<div class="chatbot-restaurants">';
                    data.content.forEach(restaurant => {
                        restaurantsHtml += `
                            <div class="chatbot-restaurant-card">
                                ${restaurant.image_url ? 
                                    `<img src="${restaurant.image_url}" alt="${restaurant.name}">` : 
                                    '<div class="no-image"><i class="fas fa-utensils"></i></div>'
                                }
                                <div class="restaurant-info">
                                    <h4>${restaurant.name}</h4>
                                    <p><i class="fas fa-map-marker-alt"></i> ${restaurant.location}</p>
                                    <p><i class="fas fa-utensils"></i> ${restaurant.cuisine}</p>
                                    <p><i class="fas fa-star"></i> ${restaurant.rating}/5</p>
                                    <a href="/restaurants/${restaurant.id}/" class="btn btn-primary btn-sm">View Details</a>
                                </div>
                            </div>
                        `;
                    });
                    restaurantsHtml += '</div>';
                    addMessage('bot', restaurantsHtml);
                } else {
                    // Display text message
                    addMessage('bot', data.content);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
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
    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        messageDiv.innerHTML = content;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
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

    // Add initial greeting
    addMessage('bot', 'Hello! I can help you find restaurants. Just tell me what cuisine you\'re looking for and/or your preferred location.');
});
