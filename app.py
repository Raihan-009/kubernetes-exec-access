from flask import Flask, render_template
from flask_socketio import SocketIO
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import threading

app = Flask(__name__)
socketio = SocketIO(app)
namespace = 'mynamespace'
pod_name = "hello-world-pod"
container_name = "hello-world-container"

def exec_command(command):
    config.load_kube_config()
    api = client.CoreV1Api()

    try:
        exec_command = [
            "/bin/sh",
            "-c",
            command
        ]

        resp = api.read_namespaced_pod(name=pod_name, namespace=namespace)

        if resp.status.phase == 'Running':
            exec_response = stream(api.connect_get_namespaced_pod_exec,
                                   name=pod_name,
                                   namespace=namespace,
                                   command=exec_command,
                                   container=container_name,
                                   stdin=False,
                                   stdout=True,
                                   stderr=True,
                                   tty=False,
                                   _preload_content=False)

            # Use the WebSocket connection to emit output
            while exec_response.is_open():
                output = exec_response.read_stdout()
                if output:
                    socketio.emit('output', {'output': output})
            exec_response.close()

        else:
            socketio.emit('output', {'output': f"Pod {pod_name} is not in the 'Running' phase."})

    except ApiException as e:
        socketio.emit('output', {'output': f"Error executing command: {e}"})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('command')
def handle_command(data):
    command = data['command']
    socketio.start_background_task(exec_command, command)

if __name__ == '__main__':
    socketio.run(app, debug=True)
