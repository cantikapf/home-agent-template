import socket
import os
import sys
import json
import io
import contextlib
import traceback
import threading

import home_agent

SOCKET_FILE = "/tmp/home_agent.sock"

def handle_client(conn):
    try:
        data = conn.recv(65536)
        if not data:
            return
        
        args = json.loads(data.decode('utf-8'))
        f = io.StringIO()
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            try:
                sys.argv = ['home_agent.py'] + args
                home_agent.main()
            except SystemExit:
                pass
            except Exception as e:
                print(traceback.format_exc())
        
        output = f.getvalue()
        conn.sendall(output.encode('utf-8'))
    except Exception as e:
        conn.sendall(f"Daemon Error: {e}".encode('utf-8'))
    finally:
        conn.close()

def serve():
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(SOCKET_FILE)
    s.listen(5)
    
    print("Multithreaded Daemon started. Listening on", SOCKET_FILE)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn,))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    serve()
