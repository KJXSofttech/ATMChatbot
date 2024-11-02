let currentTag = "start_conversation";
let userData = {};
let typingTimeout;

/**
 * Function to add a message to the chat box with typing effect
 * @param {string} message - The message to display
 * @param {string} className - The CSS class for styling
 * @param {function} callback - Callback function after message is displayed
 */
function addMessage(message, className, callback = null) {
    const chatBox = document.getElementById('chat-box');
    const messageContainer = document.createElement('div');
    messageContainer.className = 'chat-message-container ' + (className === 'user-message' ? 'user-message-container' : 'bot-message-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message ' + className;
    
    const emojiSpan = document.createElement('span');
    emojiSpan.className = 'emoji';
    
    if (className === 'user-message') {
        emojiSpan.innerText = '👤';
        messageContainer.appendChild(messageDiv);
        messageContainer.appendChild(emojiSpan);
    } else if (className === 'bot-message') {
        emojiSpan.innerText = '🤖';
        messageContainer.appendChild(emojiSpan);
        messageContainer.appendChild(messageDiv);
    }
    
    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Typing effect
    let index = 0;
    function typeNextChar() {
        if (index < message.length) {
            messageDiv.innerHTML += message[index];
            index++;
            chatBox.scrollTop = chatBox.scrollHeight;
            typingTimeout = setTimeout(typeNextChar, 10);
        } else if (callback) {
            callback();
        }
    }
    typeNextChar();
}

/**
 * Function to add an option button to the chat
 * @param {string} optionText - The text on the button
 * @param {string} optionValue - The value sent to the server
 */
function addOption(optionText, optionValue) {
    const chatBox = document.getElementById('chat-box');
    const optionButton = document.createElement('button');
    optionButton.className = 'option-button';
    optionButton.innerText = optionText;
    optionButton.onclick = () => handleOptionClick(optionValue, optionText);
    chatBox.appendChild(optionButton);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Function to add a dropdown menu to the chat
 * @param {Array} options - List of options for the dropdown
 */
function addDropdown(options) {
    const chatBox = document.getElementById('chat-box');
    const dropdownContainer = document.createElement('div');
    dropdownContainer.className = 'dropdown-container';
    
    const select = document.createElement('select');
    select.className = 'dropdown';
    
    // Add a default disabled option
    const defaultOption = document.createElement('option');
    defaultOption.value = "";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    defaultOption.textContent = "Select an option";
    select.appendChild(defaultOption);
    
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        select.appendChild(optionElement);
    });
    
    select.onchange = () => {
        const selectedValue = select.value;
        const selectedText = select.options[select.selectedIndex].text;
    
        // Remove the dropdown after selection
        dropdownContainer.remove();
    
        // Add the selected option as a user message
        addMessage(selectedText, 'user-message');
    
        // Process the selected option
        processUserInput(selectedValue, false);
    };
    
    dropdownContainer.appendChild(select);
    chatBox.appendChild(dropdownContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Function to handle clicks on option buttons
 * @param {string} optionValue - The value to send to the server
 * @param {string} optionText - The text to display as user message
 */
function handleOptionClick(optionValue, optionText) {
    // Remove all option buttons
    const optionButtons = document.querySelectorAll('.option-button');
    optionButtons.forEach(button => button.remove());

    // Remove any existing dropdowns
    const existingDropdowns = document.querySelectorAll('.dropdown-container');
    existingDropdowns.forEach(dropdown => dropdown.remove());

    // Add the selected option as a user message
    addMessage(optionText, 'user-message');

    if (optionValue === "close_chat") {
        toggleChatbox(); // Close the chatbot
    } else if (optionValue === "ask_more_questions") {
        addMessage("Ask me anything!", 'bot-message');
        currentTag = "open_questions";
        // Show the input field
        document.getElementById('user-input').style.display = 'inline-block';
        document.querySelector('.send-button').style.display = 'flex';
    } else {
        // Process other user inputs
        processUserInput(optionValue, false);
    }
}

/**
 * Function to send the user's message to the server
 */
function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput) {
        addMessage(userInput, 'user-message');
        document.getElementById('user-input').value = '';
        processUserInput(userInput, true);
    }
}

// Send message on Enter key press
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

/**
 * Function to process user input and communicate with the server
 * @param {string} userInput - The user's input
 * @param {boolean} isManual - Whether the input was typed manually
 */
function processUserInput(userInput, isManual) {
    const payload = {
        message: userInput,
        current_tag: currentTag,
        user_data: userData,
        is_manual: isManual
    };

    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage(data.error, 'bot-message');
        } else {
            userData = data.user_data; // Update user data
            displayMessages(data.response, 0, data.options, data.tag, data.input_type);
        }
    })
    .catch(error => {
        addMessage(`An error occurred: ${error.message}`, 'bot-message');
    });
}

/**
 * Function to display messages from the bot
 * @param {Array} messages - List of messages to display
 * @param {number} index - Current index in messages array
 * @param {Array} options - Options or dropdown items
 * @param {string} newTag - The next tag for conversation flow
 * @param {string} inputType - Type of input expected ('options', 'dropdown')
 */
function displayMessages(messages, index, options, newTag, inputType) {
    if (index < messages.length) {
        addMessage(messages[index], 'bot-message', () => displayMessages(messages, index + 1, options, newTag, inputType));
    } else {
        currentTag = newTag;

        // Clear existing options and dropdowns before adding new ones
        const existingOptions = document.querySelectorAll('.option-button');
        existingOptions.forEach(button => button.remove());

        const existingDropdowns = document.querySelectorAll('.dropdown-container');
        existingDropdowns.forEach(dropdown => dropdown.remove());

        if (inputType === 'dropdown') {
            addDropdown(options);
            // Hide the input field when dropdown is available
            document.getElementById('user-input').style.display = 'none';
            document.querySelector('.send-button').style.display = 'none';
        } else if (options && options.length > 0) {
            options.forEach(option => {
                addOption(option.text, option.value);
            });
            // Hide the input field when options are available
            document.getElementById('user-input').style.display = 'none';
            document.querySelector('.send-button').style.display = 'none';
        } else {
            // If there are no options, show the input field
            document.getElementById('user-input').style.display = 'inline-block';
            document.querySelector('.send-button').style.display = 'flex';
        }

        // Handle "Close Chat" and "Ask More Questions" options
        if (newTag === "end_conversation" && !(options && options.some(opt => opt.value === "close_chat"))) {
            addOption("Close Chat", "close_chat");
            addOption("Ask More Questions", "ask_more_questions");
        }
    }
}

/**
 * Function to toggle the chatbot visibility
 */
function toggleChatbox() {
    const phoneContainer = document.getElementById('phone-container');
    const chatIcon = document.getElementById('chat-icon');
    if (phoneContainer.style.display === "none") {
        phoneContainer.style.display = "flex";
        chatIcon.style.display = "none";
        if (currentTag === "start_conversation") {
            startConversation();
        }
    } else {
        phoneContainer.style.display = "none";
        chatIcon.style.display = "block";
        resetChat(); // Reset the chat when closing
    }
}

/**
 * Function to initiate the conversation with the bot
 */
function startConversation() {
    fetch("/start_conversation", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: "", current_tag: "start_conversation" })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage(data.error, 'bot-message');
        } else {
            userData = {}; // Reset user data
            displayMessages(data.response, 0, data.options, data.tag, data.input_type);
        }
    })
    .catch(error => {
        addMessage(`An error occurred: ${error.message}`, 'bot-message');
    });
}

/**
 * Function to reset the chat conversation
 */
function resetChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
    currentTag = "start_conversation";
    userData = {};
    clearTimeout(typingTimeout); // Clear any existing typing timeout
}

/**
 * Function to handle the close icon click
 */
function handleCrossClick() {
    const phoneContainer = document.getElementById('phone-container');
    const chatIcon = document.getElementById('chat-icon');
    phoneContainer.style.display = "none";
    chatIcon.style.display = "block";
    resetChat(); // Reset the chat when closing
}

/**
 * Function to handle the reset icon click
 */
function handleResetClick() {
    resetChat(); // Reset the chat
    startConversation(); // Start a new conversation
}

/**
 * Function to show the chat after a delay
 */
function showChatAfterDelay() {
    setTimeout(() => {
        toggleChatbox();
    }, 5000); // 5000 milliseconds = 5 seconds
}

// Initialize the chat when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    showChatAfterDelay(); // Show the chat after 5 seconds
});
