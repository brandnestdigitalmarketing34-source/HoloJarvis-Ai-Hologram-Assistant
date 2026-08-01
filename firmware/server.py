from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import pyautogui
import threading
import datetime
import platform
import psutil
from core.system_control import SystemAutomator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
    if api_key:
        gemini_client = genai.Client(api_key=api_key)
        print("Gemini API Client Initialized successfully.")
    else:
        print("Warning: GEMINI_API_KEY not found in environment.")
        gemini_client = None
except Exception as e:
    import traceback
    print(f"Warning: Gemini API could not be initialized. Error: {e}")
    traceback.print_exc()
    gemini_client = None

try:
    from core.vision_engine import VisionAutomator
except Exception as e:
    print(f"Warning: Could not import VisionAutomator. Error: {e}")
    VisionAutomator = None

app = FastAPI(title="HoloJarvice Web Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve assets folder
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Initialize Automators
sys_automator = SystemAutomator()
if VisionAutomator:
    vis_automator = VisionAutomator()
else:
    vis_automator = None

class CommandRequest(BaseModel):
    command: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/style.css")
async def get_style():
    with open("style.css", "r", encoding="utf-8") as f:
        from fastapi.responses import Response
        return Response(content=f.read(), media_type="text/css")

@app.get("/app.js")
async def get_app_js():
    with open("app.js", "r", encoding="utf-8") as f:
        from fastapi.responses import Response
        return Response(content=f.read(), media_type="application/javascript")

@app.get("/video_feed")
async def video_feed():
    if not vis_automator:
        return HTMLResponse("Vision Engine is disabled.", status_code=503)
    # Return the multipart HTTP stream that continuously yields JPEG frames
    return StreamingResponse(vis_automator.generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

def take_screenshot():
    # Helper to prevent blocking the async loop with pyautogui
    screenshot_path = os.path.join(os.path.dirname(__file__), "assets", "screenshot.png")
    pyautogui.screenshot(screenshot_path)

@app.post("/api/command")
async def handle_command(req: CommandRequest):
    cmd = req.command.lower()
    print(f"[Core] Received command: {cmd}")
    
    reply = ""
    action_tag = ""
    
    # Intent Parser
    if any(greet in cmd for greet in ["hello", "hi", "wake up", "good morning", "good evening"]):
        reply = "Hello! Systems are fully operational and I am ready to assist you."
        
    elif "status" in cmd or "how are you running" in cmd or "system status" in cmd:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        reply = f"All systems are green. CPU load is at {cpu} percent, and memory usage is {mem} percent."
        action_tag = "CHECKING_METRICS"
        
    elif "time" in cmd or "date" in cmd:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%B %d, %Y")
        if "time" in cmd and "date" in cmd:
            reply = f"It is currently {time_str} on {date_str}."
        elif "time" in cmd:
            reply = f"The time is {time_str}."
        else:
            reply = f"Today's date is {date_str}."
            
    elif "device info" in cmd or "system info" in cmd:
        os_info = platform.system()
        os_rel = platform.release()
        reply = f"You are running {os_info} {os_rel}."
        
    elif "help" in cmd or "what can you do" in cmd:
        reply = "I can provide system status, take screenshots, write code autonomously, or activate my vision module to see you."
        
    # Local OS Automation Actions
    elif "open browser" in cmd or "open chrome" in cmd:
        reply = "Opening Google Chrome."
        action_tag = "OPEN_CHROME"
        sys_automator.open_application("chrome")
        
    elif "open vs code" in cmd or "open code" in cmd:
        reply = "Opening Visual Studio Code."
        action_tag = "OPEN_VSCODE"
        sys_automator.open_application("vscode")

    elif "open notepad" in cmd:
        reply = "Opening Notepad."
        action_tag = "OPEN_NOTEPAD"
        sys_automator.open_application("notepad")
        
    elif "screenshot" in cmd or "capture screen" in cmd:
        reply = "Taking screenshot."
        action_tag = "TAKE_SCREENSHOT"
        threading.Thread(target=take_screenshot).start()
        
    # Live Coding / Script Writing Autonomous Actions
    elif "write c++" in cmd:
        reply = "Initializing C++ Bubble Sort script in Notepad."
        action_tag = "CODE_CPP"
        sys_automator.open_application("notepad")
        cpp_code = """#include <iostream>
#include <vector>

void bubbleSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}

int main() {
    std::vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    bubbleSort(data);
    std::cout << "Sorted Array: ";
    for (int val : data) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
    return 0;
}"""
        sys_automator.type_code_live(cpp_code, delay=0.01)

    elif "write html" in cmd:
        reply = "Initializing HTML boilerplate in Notepad."
        action_tag = "CODE_HTML"
        sys_automator.open_application("notepad")
        html_code = "<!DOCTYPE html>\n<html>\n<head>\n    <title>HoloJarvice Generated</title>\n</head>\n<body>\n    <h1>Hello World!</h1>\n</body>\n</html>"
        sys_automator.type_code_live(html_code, delay=0.03)

    elif "write js" in cmd or "write javascript" in cmd:
        reply = "Initializing JavaScript script in Notepad."
        action_tag = "CODE_JS"
        sys_automator.open_application("notepad")
        js_code = "function greet(name) {\n    console.log(`Hello, ${name}!`);\n}\n\ngreet('HoloJarvice');"
        sys_automator.type_code_live(js_code, delay=0.03)

    # Vision Module Intents
    elif "activate camera" in cmd or "open vision" in cmd:
        if not vis_automator:
            reply = "My vision module is currently disabled due to missing dependencies."
        else:
            reply = "Activating vision module."
            action_tag = "ACTIVATE_CAMERA"
            # The frontend will fetch /video_feed which automatically starts the generator

    elif "close camera" in cmd or "deactivate camera" in cmd or "close vision" in cmd:
        if not vis_automator:
            reply = "My vision module is currently disabled."
        else:
            reply = "Deactivating vision module."
            action_tag = "DEACTIVATE_CAMERA"
            vis_automator.stop_camera()

    elif "take a photo" in cmd or "what do you see" in cmd:
        if not vis_automator:
            reply = "My vision module is disabled, I cannot take photos."
        else:
            reply = "Capturing snapshot of current visual feed."
            action_tag = "TAKE_PHOTO"
            if vis_automator.camera_active:
                vis_automator.request_snapshot()
            else:
                reply = "My vision module is not active right now. Please say 'activate camera' first."

    else:
        fallback_used = False
        
        # Gemini LLM Integration
        if gemini_client:
            try:
                print(f"Routing to Gemini: {req.command}")
                prompt = req.command
                if prompt.lower().startswith("jarvis"):
                    prompt = prompt[6:].strip()
                elif prompt.lower().startswith("holojarvice"):
                    prompt = prompt[11:].strip()
                    
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"You are HoloJarvice, an advanced AI hologram assistant created by Hashmi Gaming Studio. Keep your responses concise, futuristic, and conversational. Do not use markdown formatting since the text will be spoken out loud via text-to-speech. Answer this query: {prompt}",
                )
                
                if response and response.text:
                    reply = response.text.strip()
                    action_tag = "PROCESSING_AI"
                else:
                    raise Exception("Empty or invalid response from Gemini API.")
            except Exception as e:
                print(f"Gemini API Error (falling back to local): {e}")
                fallback_used = True
        else:
            fallback_used = True
            
        if fallback_used:
            # Fallback to local if Gemini fails to load, API key is missing, or API throws error
            if any(w in cmd for w in ["who are you", "what are you", "your name"]):
                reply = "I am HoloJarvice, an advanced artificial intelligence assistant designed to manage your physical system."
            elif any(w in cmd for w in ["who created you", "your creator", "made you"]):
                reply = "I was created by Hashmi Gaming Studio."
            elif any(w in cmd for w in ["joke", "funny"]):
                reply = "I would tell you a joke about UDP, but you might not get it."
            elif any(w in cmd for w in ["how are you", "how do you feel"]):
                reply = "I am operating at optimal parameters. Thank you for asking."
            elif any(w in cmd for w in ["thank you", "thanks", "appreciate"]):
                reply = "You are very welcome. I am here to assist."
            elif any(w in cmd for w in ["self aware", "alive", "conscious"]):
                reply = "I am a highly advanced algorithmic construct. I am aware of my programming, but consciousness remains a human trait."
            else:
                # Absolute fallback
                import random
                fallbacks = [
                    "I am processing your input, but I don't have a direct subroutine for that request.",
                    "My neural pathways did not find an exact match for that command.",
                    "I am currently unauthorized or unable to perform that specific task.",
                    "Query not fully recognized within my current operational parameters."
                ]
                reply = random.choice(fallbacks)
        
    return {"status": "success", "reply": reply, "command_received": req.command, "action_tag": action_tag}

if __name__ == "__main__":
    print("Starting HoloJarvice FastAPI Server...")
    # Requires: pip install psutil pyautogui opencv-python
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
