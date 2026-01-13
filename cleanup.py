import os
import json
def delete_generated_images(directory):
    """
    Deletes all resized, watermarked, and compressed images from the given directory.
    """
    patterns = ["_resized.jpg", "_watermarked.jpg", "_compressed.jpg"]
    deleted_files = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(pattern) for pattern in patterns):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"🗑 Deleted: {file_path}")
                    deleted_files += 1
                except Exception as e:
                    print(f"❌ Error deleting {file_path}: {e}")

    if deleted_files == 0:
        print("✅ No generated images found to delete.")
    else:
        print(f"✅ Cleanup complete. {deleted_files} files deleted.")

def remove_unknown(file1):
    def remove_unknown_guests(data):
        for event in data:
            event["Guests"] = [guest for guest in event["Guests"] if guest["whatsapp Number"].lower() != "unknown"]
        return data

    # Load JSON from file
    input_file = file1  # Replace with your actual file path
    output_file = file1

    with open(input_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Remove guests with "Unknown" WhatsApp number
    cleaned_data = remove_unknown_guests(json_data)

    # Save the cleaned JSON back to a file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file, indent=4)

    print(f"Cleaned JSON saved to {output_file}")

# Example usage: Run in the same directory where images are stored
# delete_generated_images("Photos")