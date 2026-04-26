import fastapi
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json, os, shutil, base64, asyncio, threading, time
from pydantic import BaseModel
from typing import Optional
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import filedialog

# ── Import your existing logic ──────────────────────────────────────────────
from core import Train, Sort, whatsapp, cleanup

BASIC_JSON = os.path.join(os.path.dirname(__file__), "data", "Basic.json")
EVENTS_JSON = os.path.join(os.path.dirname(__file__), "data", "Events.json")

app = FastAPI(title="AuraSnap API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def read_events():
    if os.path.exists(EVENTS_JSON):
        with open(EVENTS_JSON, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def write_events(events):
    with open(EVENTS_JSON, "w") as f:
        json.dump(events, f, indent=4)

def read_basic():
    if os.path.exists(BASIC_JSON):
        with open(BASIC_JSON, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def write_basic(data):
    with open(BASIC_JSON, "w") as f:
        json.dump(data, f, indent=4)

# ─────────────────────────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────────────────────────
class EventModel(BaseModel):
    event_name: str
    event_date: str
    event_owner: str
    contact_number: str
    file_location: str
    base_path: str

class UpdateEventModel(BaseModel):
    event_name: str
    event_date: str
    event_owner: str
    contact_number: str
    file_location: str

class SettingsModel(BaseModel):
    phone_number: str
    whatsapp_message: str
    camera: str
    processing_mode: str
    whatsapp_delivery: str

class WatermarkModel(BaseModel):
    wm_image_b64: Optional[str] = None
    opacity: float = 1.0
    scale: float = 0.2
    position: str = "bottom-right"

class CaptureFrameModel(BaseModel):
    event_name: str
    user_name: str
    phone_number: str
    frame_b64: str  # base64 encoded JPEG frame

class MagicModel(BaseModel):
    event_name: str
    custom_path: Optional[str] = None
    tasks: list[str] = ["train", "sort", "send"]  # Selective tasks


# ─────────────────────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AuraSnap API running"}

@app.get("/utils/select-folder")
def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    return {"path": folder_path}


# ─────────────────────────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────────────────────────
@app.get("/events")
def get_events():
    return read_events()

@app.post("/events")
def add_event(ev: EventModel):
    new_folder = os.path.join(ev.base_path, ev.event_name)
    try:
        os.makedirs(new_folder, exist_ok=False)
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Folder already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    event_data = {
        "Event Name": ev.event_name,
        "Event Date": ev.event_date,
        "Event Owner": ev.event_owner,
        "Contact Number": ev.contact_number,
        "File Location": new_folder.replace("\\", "/"),
        "Accuracy": 0,
        "Guests": []
    }
    events = read_events()
    events.append(event_data)
    write_events(events)
    return {"detail": "Event created", "event": event_data}

@app.put("/events/{event_name}")
def update_event(event_name: str, ev: UpdateEventModel):
    events = read_events()
    for e in events:
        if e["Event Name"] == event_name:
            e["Event Date"] = ev.event_date
            e["Event Owner"] = ev.event_owner
            e["Contact Number"] = ev.contact_number
            e["File Location"] = ev.file_location
            write_events(events)
            return {"detail": "Updated"}
    raise HTTPException(status_code=404, detail="Event not found")

@app.delete("/events/{event_name}")
def delete_event(event_name: str):
    events = read_events()
    ev = next((e for e in events if e["Event Name"] == event_name), None)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    folder = ev.get("File Location", "")
    if folder and os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)
    updated = [e for e in events if e["Event Name"] != event_name]
    write_events(updated)
    return {"detail": "Deleted"}

# ─────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────
@app.get("/settings")
def get_settings():
    return read_basic()

@app.post("/settings")
def save_settings(s: SettingsModel):
    data = read_basic()
    data["Number"] = s.phone_number
    data["Whatsapp"] = s.whatsapp_message
    data["Camera"] = s.camera
    data["Processing Mode"] = s.processing_mode
    data["WhatsApp Delivery Method"] = s.whatsapp_delivery
    write_basic(data)
    return {"detail": "Settings saved"}

# ─────────────────────────────────────────────────────────────
#  WATERMARK PREVIEW
# ─────────────────────────────────────────────────────────────
@app.post("/watermark/preview")
def watermark_preview(wm: WatermarkModel):
    """Returns a base64 PNG of the watermarked sample image."""
    sample_path = os.path.join(os.path.dirname(__file__), "assets", "Sample photo.png")
    try:
        if os.path.exists(sample_path):
            img = Image.open(sample_path).convert("RGBA")
        else:
            img = Image.new("RGBA", (800, 600), (100, 100, 120, 255))

        img.thumbnail((800, 600), Image.Resampling.LANCZOS)

        if wm.wm_image_b64:
            raw = base64.b64decode(wm.wm_image_b64)
            watermark = Image.open(io.BytesIO(raw)).convert("RGBA")
            opac = wm.opacity
            scale = wm.scale
            pos = wm.position

            if opac < 1.0:
                alpha = watermark.split()[3]
                alpha = alpha.point(lambda p: p * opac)
                watermark.putalpha(alpha)

            wm_width = int(img.width * scale)
            wm_height = int((watermark.height / max(watermark.width, 1)) * wm_width)

            if wm_width > 0 and wm_height > 0:
                watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                positions = {
                    "top-left":      (20, 20),
                    "top-center":    ((img.width - wm_width) // 2, 20),
                    "top-right":     (img.width - wm_width - 20, 20),
                    "center-left":   (20, (img.height - wm_height) // 2),
                    "center":        ((img.width - wm_width) // 2, (img.height - wm_height) // 2),
                    "center-right":  (img.width - wm_width - 20, (img.height - wm_height) // 2),
                    "bottom-left":   (20, img.height - wm_height - 20),
                    "bottom-center": ((img.width - wm_width) // 2, img.height - wm_height - 20),
                    "bottom-right":  (img.width - wm_width - 20, img.height - wm_height - 20),
                }
                img.paste(watermark, positions.get(pos, positions["bottom-right"]), watermark)

        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {"image_b64": b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/watermark/save")
def watermark_save(wm: WatermarkModel):
    data = read_basic()
    data["WaterMark Opacity"] = wm.opacity
    data["WaterMark Scale"] = wm.scale
    data["WaterMark Location"] = wm.position
    write_basic(data)
    return {"detail": "Watermark settings saved"}

# ─────────────────────────────────────────────────────────────
#  CAPTURE FRAMES
# ─────────────────────────────────────────────────────────────
@app.post("/capture/frame")
def save_capture_frame(body: CaptureFrameModel):
    """Receive a base64 JPEG frame from browser and save it."""
    events = read_events()
    ev = next((e for e in events if e["Event Name"] == body.event_name), None)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    folder = ev["File Location"]
    guests_folder = os.path.join(folder, "guests_folder", body.phone_number)
    os.makedirs(guests_folder, exist_ok=True)

    # Count existing frames
    existing = len([f for f in os.listdir(guests_folder) if f.endswith(".jpg")])
    frame_path = os.path.join(guests_folder, f"{existing + 1}.jpg")

    raw = base64.b64decode(body.frame_b64.split(",")[-1])
    with open(frame_path, "wb") as f:
        f.write(raw)

    # Also ensure guest entry exists in JSON
    guest_exists = any(
        g.get("whatsapp Number") == body.phone_number
        for g in ev.get("Guests", [])
    )
    if not guest_exists:
        ev["Guests"].append({
            "name": body.user_name,
            "whatsapp Number": body.phone_number,
            "photos": []
        })
        write_events(events)

    return {"detail": f"Frame {existing + 1} saved", "count": existing + 1}

@app.delete("/capture/clear/{event_name}/{phone_number}")
def clear_capture_folder(event_name: str, phone_number: str):
    events = read_events()
    ev = next((e for e in events if e["Event Name"] == event_name), None)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    
    folder = ev["File Location"]
    guests_folder = os.path.join(folder, "guests_folder", phone_number)
    if os.path.exists(guests_folder):
        shutil.rmtree(guests_folder, ignore_errors=True)
    os.makedirs(guests_folder, exist_ok=True)
    return {"detail": "Folder cleared"}


# ─────────────────────────────────────────────────────────────
#  MAGIC  (SSE Progress Stream)
# ─────────────────────────────────────────────────────────────
@app.post("/magic/check-model")
def check_model_exists(body: MagicModel):
    events = read_events()
    ev = next((e for e in events if e["Event Name"] == body.event_name), None)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    embed_path = os.path.join(ev["File Location"], "events_models", f"{body.event_name}_face_embeddings.pkl")
    return {"exists": os.path.exists(embed_path)}

@app.post("/magic/run")
def run_magic(body: MagicModel):
    """SSE endpoint that streams progress events back to the frontend."""
    events = read_events()
    ev = next((e for e in events if e["Event Name"] == body.event_name), None)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    file_directory = ev["File Location"]
    final_directory = body.custom_path.strip() if body.custom_path and body.custom_path.strip() else file_directory

    queue: list[str] = []
    done = {"v": False}

    def progress_callback(current, total, phase_name):
        percent = (current / total * 100) if total > 0 else 100
        msg = json.dumps({"type": "progress", "phase": phase_name, "current": current, "total": total, "percent": round(percent, 1)})
        queue.append(msg)

    def worker():
        try:
            tasks = body.tasks
            print(f"DEBUG: Starting Magic for event '{body.event_name}' with tasks: {tasks}")
            
            if "train" in tasks:
                accuracy = Train.train_face_recognition(file_directory, body.event_name, progress_callback)
                if accuracy is not None:
                    # Update accuracy in Events.json
                    ev_list = read_events()
                    for e in ev_list:
                        if e["Event Name"].strip().lower() == body.event_name.strip().lower():
                            e["Accuracy"] = round(accuracy, 2)
                            print(f"DEBUG: Saved accuracy {accuracy}% to event '{e['Event Name']}'")
                            break
                    write_events(ev_list)
                    
                    progress_callback(100, 100, f"Training Complete (Accuracy: {accuracy:.1f}%)")
                    time.sleep(1.5)
                cleanup.remove_unknown(EVENTS_JSON)
            else:
                progress_callback(100, 100, "Training Skipped")
                time.sleep(0.5)

            embed_path = os.path.join(file_directory, "events_models", f"{body.event_name}_face_embeddings.pkl")
            
            if "sort" in tasks:
                if not os.path.exists(embed_path):
                    raise Exception("Face embedding model not found. Please run Training first.")
                
                cleanup.delete_generated_images(final_directory)
                Sort.sort_face_recognition(embed_path, final_directory, EVENTS_JSON, body.event_name, progress_callback=progress_callback)
                cleanup.remove_unknown(EVENTS_JSON)
            else:
                progress_callback(100, 100, "Sorting Skipped")
                time.sleep(0.5)
            
            if "send" in tasks:
                whatsapp.send_whatsapp_messages(BASIC_JSON, EVENTS_JSON, body.event_name, final_directory, progress_callback)
                cleanup.delete_generated_images(final_directory)
            else:
                progress_callback(100, 100, "WhatsApp Sending Skipped")
                time.sleep(0.5)

            queue.append(json.dumps({"type": "done", "message": "Selected tasks completed!"}))

        except Exception as e:
            queue.append(json.dumps({"type": "error", "message": str(e)}))
        finally:
            done["v"] = True

    threading.Thread(target=worker, daemon=True).start()

    async def event_stream():
        while not done["v"] or queue:
            while queue:
                item = queue.pop(0)
                yield f"data: {item}\n\n"
            await asyncio.sleep(0.2)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
