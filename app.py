import os
import pty
import subprocess
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
pid, fd = pty.fork()

if pid == 0:  # Child process
    os.execlp('bash', 'bash')

process = subprocess.Popen(
    ['bash'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=0,
    preexec_fn=os.setsid,
)

@app.route('/')
def index():
    return render_template('index_terminal.html')

@socketio.on('connect_terminal')
def handle_connect_terminal(data):
    socketio.emit('output_terminal', {'output': 'Connected to terminal.'})

@socketio.on('input_terminal')
def handle_input_terminal(data):
    input_data = data['input']
    os.write(fd, input_data.encode())

def read_output():
    while True:
        output = os.read(fd, 1024)
        socketio.emit('output_terminal', {'output': output.decode()})

if __name__ == '__main__':
    socketio.start_background_task(target=read_output)
    socketio.run(app, debug=True)
