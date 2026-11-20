"""
FinSentinel Application Runner
Starts the FastAPI application and automatically opens the dashboard in your default browser.
"""
import sys
import time
import socket
import threading
import webbrowser
import os

def wait_and_open_browser(host: str = "127.0.0.1", port: int = 8000):
    url = f"http://{host}:{port}"
    print(f"[FinSentinel] Waiting for server on {url}...")
    for _ in range(60):
        try:
            with socket.create_connection((host, port), timeout=0.5):
                print(f"[FinSentinel] Server is ready! Opening {url} in your browser...")
                time.sleep(0.5)
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.5)
    print(f"[FinSentinel] Server took longer than expected. Please open {url} manually.")

if __name__ == "__main__":
    # Ensure current directory is project root
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Start browser opener in background thread
    threading.Thread(target=wait_and_open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, log_level="info")
