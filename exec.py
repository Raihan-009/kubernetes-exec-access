from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def exec_command(namespace, pod_name, container_name, command):
    config.load_kube_config()

    api = client.CoreV1Api()

    try:
        namespace = namespace

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

            # Use the WebSocket connection to read the output
            while exec_response.is_open():
                # Read standard output and standard error
                output = exec_response.read_stdout()
                error = exec_response.read_stderr()

                if output:
                    print(f"stdout: {output}")
                if error:
                    print(f"stderr: {error}")

            exec_response.close()

        else:
            print(f"Pod {pod_name} is not in the 'Running' phase.")

    except ApiException as e:
        print(f"Error executing command: {e}")


if __name__ == "__main__":
    namespace = 'mynamespace'
    pod_name = "hello-world-pod"
    container_name = "hello-world-container"
    command = "ls"

    exec_command(namespace, pod_name, container_name, command)
