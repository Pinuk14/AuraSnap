import os
import json
import time
import pickle
import cv2
import numpy as np
import pywhatkit
import pyautogui
import pyperclip
from PIL import Image
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

def sort_face_recognition(EMBEDDING_FILE, DATASET_DIR, EVENTS_JSON_PATH, EVENT_NAME, SIMILARITY_THRESHOLD=0.6):
    """
    Recognizes faces in images and updates events.json while avoiding duplicates.
    """
    # Load ArcFace model
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0)  # Use GPU (ctx_id=-1 for CPU)

    # Load trained embeddings
    with open(EMBEDDING_FILE, "rb") as f:
        data = pickle.load(f)
        trained_embeddings = np.array(data["embeddings"])
        labels = np.array(data["labels"])
        label_map = data["label_map"]

    # Load events data
    with open(EVENTS_JSON_PATH, "r") as f:
        events = json.load(f)

    # Find the relevant event
    event = next((e for e in events if e["Event Name"] == EVENT_NAME), None)
    if not event:
        print(f"❌ Error: Event '{EVENT_NAME}' not found.")
        return

    grouped_paths = {}

    for img_name in os.listdir(DATASET_DIR):
        img_path = os.path.join(DATASET_DIR, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        faces = app.get(img)
        if not faces:
            continue

        for face in faces:
            test_embedding = face.embedding
            similarities = cosine_similarity([test_embedding], trained_embeddings)
            max_similarity_index = np.argmax(similarities)
            max_similarity = similarities[0, max_similarity_index]

            predicted_phone_number = label_map.get(labels[max_similarity_index], "Unknown") if max_similarity >= SIMILARITY_THRESHOLD else "Unknown"

            if predicted_phone_number not in grouped_paths:
                grouped_paths[predicted_phone_number] = set()
            grouped_paths[predicted_phone_number].add(img_path)

    # Convert sets to lists
    grouped_paths = {phone_number: list(paths) for phone_number, paths in grouped_paths.items()}

    # Prepare existing guest data to avoid duplicates
    guest_dict = {guest["whatsapp Number"]: set(guest.get("photos", [])) for guest in event["Guests"]}

    for phone_number, paths in grouped_paths.items():
        if phone_number in guest_dict:
            new_photos = [path for path in paths if path not in guest_dict[phone_number]]
            guest_dict[phone_number].update(new_photos)
            for guest in event["Guests"]:
                if guest["whatsapp Number"] == phone_number:
                    guest["photos"].extend(new_photos)
        else:
            event["Guests"].append({
                "name": "Unknown",
                "whatsapp Number": phone_number,
                "photos": paths
            })

    # Save updated data
    with open(EVENTS_JSON_PATH, "w") as f:
        json.dump(events, f, indent=4)

    print(f"✅ Recognition completed and events.json updated without duplicates.")

def send_whatsapp_messages(settings_path, json_path, event_name, image_folder):
    """
    Sends WhatsApp messages with watermarked images, avoiding duplicates.
    """
    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)

        default_message = settings.get("Whatsapp", "This is a default Message.")
        watermark_image = settings.get("WaterMark Image", r"C:/Users/student/Downloads/Aura/Logo.png")
        watermark_position = settings.get("WaterMark Location", "bottom-right")
    except FileNotFoundError:
        print(f"❌ Error: The file '{settings_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: The file '{settings_path}' contains invalid JSON.")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return

    # Load event data
    with open(json_path, "r") as file:
        data = json.load(file)

    event = next((e for e in data if e["Event Name"] == event_name), None)
    if not event:
        print(f"❌ Event '{event_name}' not found.")
        return

    sent_images = set()

    for guest in event["Guests"]:
        guest_name = guest["name"]
        whatsapp_number = guest["whatsapp Number"]
        photos = guest["photos"]

        if not photos:
            continue

        for photo in photos:
            watermarked_photo = add_watermark(photo, watermark_image, watermark_position)

            if watermarked_photo and watermarked_photo not in sent_images:
                print(f"📤 Sending {watermarked_photo} to {whatsapp_number}...")
                pywhatkit.sendwhats_image(f"+91{whatsapp_number}", watermarked_photo, "", tab_close=False, close_time=20)
                sent_images.add(watermarked_photo)
                time.sleep(12)
                pyautogui.hotkey('ctrl', 'shift', 'tab')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(2)

        message = f"Hello {guest_name}, {default_message}"
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)
        pyautogui.press('enter')
        print(f"✅ Message sent to {whatsapp_number}")

    cleanup_images(image_folder)
    time.sleep(5)

def resize_image(image_path, max_width=1024):
    """
    Resizes image to max width while maintaining aspect ratio.
    """
    try:
        img = Image.open(image_path)
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
            resized_path = f"{os.path.splitext(image_path)[0]}_resized.jpg"
            img.save(resized_path, "JPEG", quality=85, optimize=True)
            return resized_path
        return image_path
    except Exception as e:
        print(f"❌ Error resizing image: {e}")
        return image_path

def add_watermark(image_path, watermark_path, position):
    """
    Adds a watermark to the image.
    """
    try:
        if not os.path.exists(image_path) or not os.path.exists(watermark_path):
            return None

        image_path = resize_image(image_path)
        img = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA")

        wm_width = int(img.width * 0.2)
        wm_height = int((watermark.height / watermark.width) * wm_width)
        watermark = watermark.resize((wm_width, wm_height), Image.LANCZOS)

        positions = {
            "bottom-right": (img.width - wm_width - 20, img.height - wm_height - 20),
            "bottom-left": (20, img.height - wm_height - 20),
            "top-right": (img.width - wm_width - 20, 20),
            "top-left": (20, 20),
            "center": ((img.width - wm_width) // 2, (img.height - wm_height) // 2)
        }
        pos = positions.get(position, positions["bottom-right"])

        img.paste(watermark, pos, watermark)
        watermarked_path = f"{os.path.splitext(image_path)[0]}_watermarked.jpg"
        img.convert("RGB").save(watermarked_path, "JPEG", quality=85, optimize=True)

        return watermarked_path
    except Exception as e:
        print(f"❌ Error adding watermark: {e}")
        return None

def cleanup_images(directory):
    """
    Deletes processed images after sending.
    """
    for file in os.listdir(directory):
        if file.endswith("_resized.jpg") or file.endswith("_watermarked.jpg"):
            os.remove(os.path.join(directory, file))
