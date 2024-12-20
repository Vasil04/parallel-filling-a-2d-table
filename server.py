import socket
import threading
import json
import time


def fill_table(table, start_row, end_row, value):
    for i in range(start_row, end_row):
        for j in range(len(table[i])):
            table[i][j] = value


def single_thread_fill_table(rows, cols):
    table = [[0 for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    fill_table(table, 0, rows, 1)
    end_time = time.time()
    return table, end_time - start_time


def parallel_fill_table(rows, cols, num_threads):
    table = [[0 for _ in range(cols)] for _ in range(rows)]

    max_dimension = max(rows, cols)
    num_threads = min(num_threads, max_dimension)

    if num_threads > rows:
        chunk_size = cols // num_threads
        threads = []

        def fill_columns(start_col, end_col, value):
            for i in range(rows):
                for j in range(start_col, end_col):
                    table[i][j] = value

        start_time = time.time()
        for t in range(num_threads):
            start_col = t * chunk_size
            end_col = (t + 1) * chunk_size if t != num_threads - 1 else cols
            thread = threading.Thread(target=fill_columns, args=(start_col, end_col, t + 1))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        end_time = time.time()

    else:
        chunk_size = rows // num_threads
        threads = []

        start_time = time.time()
        for t in range(num_threads):
            start_row = t * chunk_size
            end_row = (t + 1) * chunk_size if t != num_threads - 1 else rows
            thread = threading.Thread(target=fill_table, args=(table, start_row, end_row, t + 1))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        end_time = time.time()

    return table, end_time - start_time


def handle_client(conn):
    try:
        data = conn.recv(1024).decode()
        request = json.loads(data)
        rows = request['rows']
        cols = request['cols']
        num_threads = request['num_threads']
        _, single_time = single_thread_fill_table(rows, cols)

        table, multi_time = parallel_fill_table(rows, cols, num_threads)
        response = {
            "table": table,
            "single_thread_time": single_time,
            "multi_thread_time": multi_time,
            "time_difference": single_time - multi_time
        }
        conn.sendall(json.dumps(response).encode())
    except Exception as e:
        conn.sendall(f"Error: {e}".encode())
    finally:
        conn.close()


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
