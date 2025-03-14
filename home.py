import asyncio
from flask import Flask
from flask_socketio import SocketIO, emit
from x_agent_v2 import main as main_v2

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

class StateManager:
    def __init__(self):
        self.agent_state = None
        self.selected_agent = "Policy_Agent"
    def get_state(self):
        return self.agent_state
    def set_state(self, state):
        self.agent_state = state
    def get_selected_agent(self):
        return self.selected_agent
    def set_selected_agent(self, agent):
        self.selected_agent = agent
        
state_manager = StateManager()

@socketio.on('select_agent')
def handle_select_agent(data):
    selected_agent = data['selected_agent']
    state_manager.set_selected_agent(selected_agent)
    emit('agent_selected', {'selected_agent': selected_agent})

@socketio.on('message')
def handle_message(data):
    user_message = data['message']
    # Get the current state
    agent_state = state_manager.get_state()
    # Run the main function asynchronously
    result = asyncio.run(main_v2(user_message, agent_state, state_manager.get_selected_agent()))
    # Emit the response
    emit('response', {'message': result["response"]})
    # Update the state
    state_manager.set_state(result["agent_state"])
    
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            var socket = io();
            socket.on('connect', function() {});
            socket.on('response', function(data) {
                console.log('Received:', data.message);
                var chatWindow = document.getElementById('chat-window');
                chatWindow.innerHTML += '<p>Agent: ' + data.message + '</p>';
            });
            socket.on('agent_selected', function(data) {
                console.log('Selected Agent:', data.selected_agent);
            });
            function sendMessage() {
                var input = document.getElementById('message-input');
                var message = input.value.trim();
                if (message) {
                    socket.emit('message', {message: message});
                    var chatWindow = document.getElementById('chat-window');
                    chatWindow.innerHTML += '<p>You: ' + message + '</p>';
                    input.value = '';
                }
            }
            function selectAgent() {
                var agentSelector = document.getElementById('agent-selector');
                var selectedAgent = agentSelector.value;
                socket.emit('select_agent', {selected_agent: selectedAgent});
            }
        </script>
        <style>
            #chat-window { border: 1px solid #ccc; padding: 10px; height: 500px; overflow-y: auto; }
            #message-input { width: 70%; padding: 5px; }
            button { padding: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>Chat with the Assistant</h1>
        <label for="agent-selector">Choose an Agent:</label>
        <select id="agent-selector" onchange="selectAgent()">
            <option value="Policy_Agent">Policy Agent</option>
            <option value="Product_Agent">Product Agent</option>
        </select>
        <br/><br/>
        <div id="chat-window"></div>
        <br/><br/>
        <input type="text" id="message-input" onkeypress="if(event.key === 'Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </body>
    </html>
    '''

if __name__ == '__main__':
  print("Running updated script with improved selector logic")
  socketio.run(app, debug=True)
