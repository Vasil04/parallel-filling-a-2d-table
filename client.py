import socket
import json


def receive_all(sock):
    buffer = b""
    while True:
        part = sock.recv(4096)
        if not part:  # End of data
            break
        buffer += part
    return buffer.decode()


def client_request(host='127.0.0.1', port=65432):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((host, port))

            # Input parameters
            rows = int(input("Enter number of rows: "))
            cols = int(input("Enter number of columns: "))
            num_threads = int(input("Enter number of threads: "))
            # Send request to server
            request = {
                "rows": rows,
                "cols": cols,
                "num_threads": num_threads
            }
            client.sendall(json.dumps(request).encode())

            # Receive response from server
            data = receive_all(client)
            response = json.loads(data)
            # Display results
            print("\nResults:")
            for row in response['table']:
                print(row)
            print(f"Single-threaded time: {response['single_thread_time']:.4f} seconds")
            print(f"Multi-threaded time: {response['multi_thread_time']:.4f} seconds")
            print(f"Time saved with multithreading: {response['time_difference']:.4f} seconds")
            print("\nFilled Table:")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    client_request()
