import time
import json
import psutil
import subprocess
import websocket
import threading

SERVER_URL = "ws://localhost:8080"
DEVICE_ID = "macos"

def get_active_app():
    try:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.check_output(['osascript', '-e', script], stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except Exception:
        return "Unknown"

def get_system_stats():
    # Battery
    try:
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else 100
        power_plugged = battery.power_plugged if battery else True
    except Exception:
        battery_percent = 100
        power_plugged = True

    # CPU & Memory
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
    except Exception:
        cpu_percent = 0
        memory_percent = 0

    return {
        "battery": round(battery_percent),
        "powerPlugged": power_plugged,
        "cpuPercent": round(cpu_percent),
        "memoryUsedPercent": round(memory_percent),
        "foregroundApp": get_active_app()
    }

def on_message(ws, message):
    pass

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Connection Closed, reconnecting...")

def on_open(ws):
    print("Connected to server as macOS client")
    def run(*args):
        while True:
            stats = get_system_stats()
            payload = {
                "type": "device_update",
                "deviceId": DEVICE_ID,
                "state": stats
            }
            try:
                ws.send(json.dumps(payload))
            except Exception as e:
                print("Failed to send:", e)
                break
            time.sleep(2)
    threading.Thread(target=run, daemon=True).start()

def main():
    # warmup cpu percent
    psutil.cpu_percent()
    time.sleep(0.5)

    while True:
        try:
            ws = websocket.WebSocketApp(SERVER_URL,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            ws.run_forever()
        except Exception as e:
            print("Connection failed:", e)
        time.sleep(5)

if __name__ == "__main__":
    main()
