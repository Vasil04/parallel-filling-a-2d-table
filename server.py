import socket
import threading
import json
import time


# Function to fill part of the table
def fill_table(table, start_row, end_row, value):
    for i in range(start_row, end_row):
        for j in range(len(table[i])):
            table[i][j] = value


# Single-threaded filling
def single_thread_fill_table(rows, cols):
    table = [[0 for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    fill_table(table, 0, rows, 1)  # Single thread handles all rows
    end_time = time.time()
    return table, end_time - start_time


# Multi-threaded filling
def parallel_fill_table(rows, cols, num_threads):
    # Create independent chunks for each thread to work on
    chunks = [[] for _ in range(num_threads)]  # Each thread has its own chunk

    chunk_size = rows // num_threads
    threads = []

    start_time = time.time()
    for t in range(num_threads):
        # Create a separate chunk of rows for each thread
        chunks[t] = [[0 for _ in range(cols)] for _ in range(chunk_size)]

        # Define start and end indices for the thread's chunk
        start_row = t * chunk_size
        end_row = (t + 1) * chunk_size if t != num_threads - 1 else rows

        # Thread works only on its local chunk
        thread = threading.Thread(target=fill_table, args=(chunks[t], 0, end_row - start_row, t + 1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    end_time = time.time()

    # Combine chunks into the final table
    table = []
    for chunk in chunks:
        table.extend(chunk)

    return table, end_time - start_time


# Function to handle a client connection
def handle_client(conn):
    try:
        # Receive data from client
        data = conn.recv(1024).decode()
        request = json.loads(data)
        rows = request['rows']
        cols = request['cols']
        num_threads = request['num_threads']
        # Single-threaded execution
        _, single_time = single_thread_fill_table(rows, cols)

        # Multi-threaded execution
        table, multi_time = parallel_fill_table(rows, cols, num_threads)
        # Prepare response
        response = {
            "table": table,
            "single_thread_time": single_time,
            "multi_thread_time": multi_time,
            "time_difference": single_time - multi_time
        }
        # print(response)
        conn.sendall(json.dumps(response).encode())
    except Exception as e:
        conn.sendall(f"Error: {e}".encode())
    finally:
        conn.close()


# Main server function
def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            threading.Thread(target=handle_client, args=(conn,)).start()


if __name__ == "__main__":
    start_server()
