import os
import cv2
import numpy as np
import pickle
import json
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

# Custom FILES
from . import Duplicate
def sort_face_recognition(EMBEDDING_FILE, DATASET_DIR, EVENTS_JSON_PATH, EVENT_NAME, SIMILARITY_THRESHOLD=0.6, progress_callback=None):
    """
    Recognizes faces in photos and updates the events.json file while avoiding duplicate images.
    """
    # Load Processing Mode from Basic.json
    BASIC_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "Basic.json")
    try:
        with open(BASIC_JSON, "r") as f:
            basic_data = json.load(f)
            mode = basic_data.get("Processing Mode", "CPU")
            ctx_id = 0 if mode == "GPU" else -1
    except:
        ctx_id = -1
    
    # Load ArcFace model
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=ctx_id)

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
    if event is None:
        print(f"❌ Error: Event '{EVENT_NAME}' not found.")
        return

    grouped_paths = {}

    images_to_process = [img for img in os.listdir(DATASET_DIR) if os.path.isfile(os.path.join(DATASET_DIR, img))]
    total_images = len(images_to_process)
    processed_images = 0

    for img_name in images_to_process:
        if progress_callback:
            progress_callback(processed_images, total_images, "Sorting Phase")

        img_path = os.path.join(DATASET_DIR, img_name)
        img = cv2.imread(img_path)
        if img is None:
            processed_images += 1
            continue

        faces = app.get(img)
        if not faces:
            processed_images += 1
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
        
        processed_images += 1
        
    if progress_callback:
        progress_callback(total_images, total_images, "Sorting Phase")

    # Convert sets to lists
    grouped_paths = {phone_number: list(paths) for phone_number, paths in grouped_paths.items()}

    # Prepare existing guest data to avoid duplicates
    guest_dict = {guest["whatsapp Number"]: set(guest.get("photos", [])) for guest in event["Guests"]}

    for phone_number, paths in grouped_paths.items():
        if phone_number in guest_dict:
            # Only add new, unique photos
            new_photos = [path for path in paths if path not in guest_dict[phone_number]]
            guest_dict[phone_number].update(new_photos)
            for guest in event["Guests"]:
                if guest["whatsapp Number"] == phone_number:
                    guest["photos"].extend(new_photos)
        else:
            # Add new guest
            event["Guests"].append({
                "name": "Unknown",
                "whatsapp Number": phone_number,
                "photos": paths
            })

    # Save updated data
    with open(EVENTS_JSON_PATH, "w") as f:
        json.dump(events, f, indent=4)

    print(f"✅ Recognition completed and events.json updated without duplicates.")
    Duplicate.remove_duplicate_photos(EVENTS_JSON_PATH)