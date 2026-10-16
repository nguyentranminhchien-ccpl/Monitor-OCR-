import os
import sys
import time
import socket
import webbrowser
import threading

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import app

def find_free_port(default_port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', default_port)) != 0:
            return default_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def open_browser(port):
    time.sleep(1.2)
    url = f"http://localhost:{port}"
    print(f">> Dang mo trinh duyet tai: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    port = find_free_port(5000)
    print("=" * 60)
    print("HE THONG NHAN DIEN MONITOR & TU DONG NHAP LIEU EVT")
    print("Tac gia: BS. Nguyen Tran Minh Chien")
    print(f"Ung dung dang chay tai: http://localhost:{port}")
    print("=" * 60)
    
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    app.run(host='127.0.0.1', port=port, debug=False)
