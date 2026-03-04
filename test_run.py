from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True,
                   async_mode='threading')

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
        </head>
        <body>
            <h1>Socket Test</h1>
            <script>
                console.time('socket-connect');
                const socket = io({
                    transports: ['websocket']
                });
                
                socket.on('connect', () => {
                    console.timeEnd('socket-connect');
                    console.log('Connected!');
                });
                
                socket.on('connect_error', (error) => {
                    console.error('Connection error:', error);
                });
            </script>
        </body>
    </html>
    '''

@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)