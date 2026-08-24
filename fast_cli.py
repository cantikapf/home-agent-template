import sys
import socket
import json

def main():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(130.0)  # Allow up to 130s for TikTok AI video extraction
    try:
        s.connect("/tmp/home_agent.sock")
    except FileNotFoundError:
        print("Error: Daemon is not running.")
        sys.exit(1)
    except socket.timeout:
        print("Error: Daemon connection timed out.")
        sys.exit(1)
        
    s.sendall(json.dumps(sys.argv[1:]).encode('utf-8'))
    
    output = b""
    while True:
        try:
            data = s.recv(4096)
            if not data:
                break
            output += data
        except socket.timeout:
            output += b"\nError: Operation timed out waiting for daemon."
            break
        
    print(output.decode('utf-8'), end="")

if __name__ == "__main__":
    main()
