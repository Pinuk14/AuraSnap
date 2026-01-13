import os
import cv2
import numpy as np
import pickle
import insightface
from insightface.app import FaceAnalysis
import hdbscan

def train_face_recognition(file_path, event_name):
    # Define paths
    # EVENT_DIR = os.path.join(file_path, event_name)
    DATASET_DIR = os.path.join(file_path, "guests_folder")
    MODELS_DIR = os.path.join(file_path, "events_models")
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    EMBEDDING_FILE = os.path.join(MODELS_DIR, f"{event_name}_face_embeddings.pkl")
    HDBSCAN_MODEL_FILE = os.path.join(MODELS_DIR, f"{event_name}_hdbscan_model.pkl")
    
    # Load ArcFace model
    app = FaceAnalysis(name="buffalo_l")  # High-accuracy model
    app.prepare(ctx_id=0)  # Use GPU (ctx_id=-1 for CPU)
    
    # Check if the dataset directory exists
    if not os.path.exists(DATASET_DIR):
        print(f"❌ Error: 'guests_folder' not found at {DATASET_DIR}. Training aborted.")
        return
    
    # Extract face embeddings from dataset
    def extract_embeddings():
        embeddings = []
        labels = []
        label_map = {}
        person_id = 0

        for person in os.listdir(DATASET_DIR):
            person_dir = os.path.join(DATASET_DIR, person)
            if not os.path.isdir(person_dir):
                continue

            print(f"Processing directory: {person_dir}")
            for img_name in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    print(f"Failed to load image: {img_path}")
                    continue

                faces = app.get(img)
                if faces:
                    embedding = faces[0].embedding  # Extract 512D embedding
                    embeddings.append(embedding)
                    labels.append(person_id)
                    print(f"Extracted embedding for image: {img_path}")
                else:
                    print(f"No face detected in image: {img_path}")
            
            label_map[person_id] = person
            person_id += 1
        
        embeddings = np.array(embeddings)
        print(f"Extracted {len(embeddings)} embeddings.")
        return embeddings, np.array(labels), label_map
    
    # Save embeddings for reuse
    def save_embeddings(embeddings, labels, label_map):
        with open(EMBEDDING_FILE, "wb") as f:
            pickle.dump({"embeddings": embeddings, "labels": labels, "label_map": label_map}, f)
    
    # Train and save embeddings
    embeddings, labels, label_map = extract_embeddings()
    if embeddings.size == 0:
        print("No embeddings found. Exiting.")
        return
    save_embeddings(embeddings, labels, label_map)
    print(f"Face embeddings extracted and saved for event '{event_name}'.")
    
    # Ensure embeddings are in 2D format
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)
    
    # Train HDBSCAN model with prediction data enabled
    clusterer = hdbscan.HDBSCAN(min_cluster_size=3, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    cluster_labels = clusterer.fit_predict(embeddings)
    
    # Save clustering model
    with open(HDBSCAN_MODEL_FILE, "wb") as f:
        pickle.dump(clusterer, f)
    
    print(f"Trained HDBSCAN model for event '{event_name}'. Found {len(set(cluster_labels))} clusters.")

# Example usage:
# file_path = "C:/Users/Sanyu Tuscano/Desktop/Aura Snap"
# event_name = "Birthday"
# train_face_recognition(file_path, event_name)
