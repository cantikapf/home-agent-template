import sys
import os
import socket
import json

def run_cli_directly():
    from datetime import datetime
    import argparse
    
    def add_expense(amount, category, desc):
        data = []
        try:
            with open('expenses.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        data.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "category": category,
            "description": desc
        })
        
        with open('expenses.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Pengeluaran berhasil dicatat: {desc} (Rp{amount:,}) - Kategori: {category}")

    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True)
    parser.add_argument('--amount', type=int)
    parser.add_argument('--category')
    parser.add_argument('--desc')
    args = parser.parse_args()
    
    if args.action == 'expense':
        add_expense(args.amount, args.category, args.desc)


def main():
    # Socket UNIX di-disable di Windows, forward langsung ke home_agent.py
    if os.name == 'nt':
        import subprocess
        python_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'python.exe')
        if not os.path.exists(python_bin):
            python_bin = 'python'
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home_agent.py')
        result = subprocess.run([python_bin, script_path] + sys.argv[1:], capture_output=True, text=True)
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return
    
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(130.0)  # Allow up to 130s for TikTok AI video extraction
    try:
        s.connect("/tmp/home_agent.sock")
    except (FileNotFoundError, AttributeError):
        print("Error: Daemon is not running. Falling back to direct CLI mode.")
        run_cli_directly()
        return
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
