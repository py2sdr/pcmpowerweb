"""
PCM Audio Power Meter
-------------------------------------------------------------------------
Author: Edson Pereira, PY2SDR
Code Assistant: Gemini
-------------------------------------------------------------------------
"""

import sys
import pyaudio
import threading
import time
import math
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIGURATION ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000  
CHUNK = 8192   
AUTHOR_NAME = "Edson Pereira, PY2SDR"
ASSISTANT_CREDIT = "Code Assistant: Gemini"

latest_number = "0.0"

def list_devices():
    p = pyaudio.PyAudio()
    print("\n=== PCM POWER METER: AUDIO INPUT DEVICES ===")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"{i:<7} | {dev['name']}")
    p.terminate()

def audio_listener(device_index):
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, input_device_index=device_index,
                        frames_per_buffer=CHUNK)
        while True:
            try:
                raw_data = stream.read(CHUNK, exception_on_overflow=False)
                arr = np.frombuffer(raw_data, np.int16).astype(np.float32)
                mean_sq = np.mean(arr**2)
                pwr = 10 * np.log10(mean_sq) if mean_sq >= 1.0 else 0.0
                global latest_number
                latest_number = f"{pwr:.1f}"
            except: break
    except: pass
    finally:
        try: stream.close()
        except: pass
        p.terminate()

class SimpleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return 
    def do_GET(self):
        if self.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html'); self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/events':
            self.send_response(200); self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache'); self.send_header('Connection', 'keep-alive'); self.end_headers()
            while True:
                try:
                    self.wfile.write(f"data: {latest_number}\n\n".encode()); self.wfile.flush()
                except: break
                time.sleep(0.05) 

    def get_html(self):
        return f"""
        <!DOCTYPE html>
        <html data-theme="dark">
        <head>
            <title>PCM Power Meter</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                * {{ box-sizing: border-box; user-select: none; }}
                
                :root {{
                    --bg: #000;
                    --text: #007bff;
                    --header: #555;
                    --max: #0f0;  /* Green */
                    --min: #ff0;  /* Yellow */
                    --btn-bg: #222;
                    --btn-text: #fff;
                    --btn-border: #444;
                }}

                [data-theme="light"] {{
                    --bg: #fff;
                    --text: #0056b3;
                    --header: #999;
                    --max: #008000; /* Darker Green for light mode */
                    --min: #b8860b; /* Darker Yellow/Gold for light mode */
                    --btn-bg: #eee;
                    --btn-text: #000;
                    --btn-border: #ccc;
                }}

                body {{ 
                    font-family: 'MS Gothic', sans-serif; 
                    display: flex; flex-direction: column; justify-content: space-between; align-items: center; 
                    height: 100vh; margin: 0; padding: 20px 10px 30px 10px;
                    background: var(--bg); color: var(--text); 
                    transition: background 0.3s, color 0.3s;
                }}
                
                header {{ font-size: 24px; font-weight: bold; color: var(--header); text-transform: uppercase; }}

                .stats-box {{ text-align: center; display: flex; flex-direction: column; gap: 8px; }}
                .stat-line {{ font-size: clamp(22px, 6vw, 32px); font-weight: bold; }}
                
                #max-row {{ color: var(--max); }}
                #min-row {{ color: var(--min); }}
                
                .main-display {{
                    display: flex;
                    align-items: baseline;
                    gap: 10px;
                }}

                #number {{ 
                    font-size: clamp(80px, 20vw, 35vh); 
                    font-variant-numeric: tabular-nums; font-weight: bold;
                }}

                .unit {{
                    font-size: clamp(24px, 8vw, 10vh);
                    font-weight: bold;
                    color: var(--header);
                }}

                .controls {{
                    display: flex;
                    gap: 15px;
                    width: 100%;
                    max-width: 400px;
                    justify-content: center;
                    margin-bottom: 10px;
                }}

                .btn {{
                    flex: 1;
                    padding: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    background: var(--btn-bg);
                    color: var(--btn-text);
                    border: 1px solid var(--btn-border);
                    border-radius: 8px;
                    cursor: pointer;
                    text-transform: uppercase;
                }}

                footer {{ text-align: center; line-height: 1.4; color: #666; font-size: 14px; }}
                .author {{ font-size: 18px; font-weight: bold; color: #888; }}
            </style>
        </head>
        <body>
            <header>PCM Power Meter</header>
            
            <div class="stats-box">
                <div id="max-row" class="stat-line">Max Power: <span id="max">0.0</span> dB</div>
                <div id="min-row" class="stat-line">Min Power: <span id="min">0.0</span> dB</div>
            </div>
            
            <div class="main-display">
                <div id="number">0.0</div>
                <div class="unit">dB</div>
            </div>
            
            <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
                <div class="controls">
                    <button class="btn" onclick="resetStats()">Reset Stats</button>
                    <button class="btn" onclick="toggleTheme()">Toggle Theme</button>
                </div>
                
                <footer>
                    <div class="author">{AUTHOR_NAME}</div>
                    <div class="assistant">{ASSISTANT_CREDIT}</div>
                </footer>
            </div>

            <script>
                let maxVal = -999.0, minVal = 999.0, currentVal = 0.0, firstData = true;
                const eventSource = new EventSource('/events');
                
                eventSource.onmessage = (e) => {{
                    currentVal = parseFloat(e.data);
                    document.getElementById('number').innerText = e.data;
                    if (firstData && currentVal > 0) {{
                        maxVal = currentVal; minVal = currentVal; firstData = false;
                    }} else if (!firstData) {{
                        if (currentVal > maxVal) maxVal = currentVal;
                        if (currentVal < minVal && currentVal > 0) minVal = currentVal;
                    }}
                    document.getElementById('max').innerText = (maxVal === -999.0) ? "0.0" : maxVal.toFixed(1);
                    document.getElementById('min').innerText = (minVal === 999.0) ? "0.0" : minVal.toFixed(1);
                }};

                function resetStats() {{
                    maxVal = currentVal; minVal = currentVal;
                    document.getElementById('max').innerText = maxVal.toFixed(1);
                    document.getElementById('min').innerText = minVal.toFixed(1);
                }}

                function toggleTheme() {{
                    const html = document.documentElement;
                    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                    html.setAttribute('data-theme', newTheme);
                }}
            </script>
        </body>
        </html>
        """

if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_devices()
    else:
        try:
            threading.Thread(target=audio_listener, args=(int(sys.argv[1]),), daemon=True).start()
            HTTPServer(('0.0.0.0', 8080), SimpleHandler).serve_forever()
        except KeyboardInterrupt: pass
