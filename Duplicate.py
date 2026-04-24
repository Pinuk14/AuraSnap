import json

def remove_duplicate_photos(events_json_path):
    # Load events data
    with open(events_json_path, "r") as f:
        events = json.load(f)

    # Iterate through each event
    for event in events:
        # Iterate through each guest in the event
        for guest in event["Guests"]:
            if "photos" in guest:
                # Normalize paths first to ensure identical files with different slashes are caught
                normalized_photos = [photo.replace("\\", "/") for photo in guest["photos"]]
                # Convert the list of photo paths to a set to remove duplicates
                unique_photos = list(set(normalized_photos))
                # Update the guest's photos list with unique paths
                guest["photos"] = unique_photos

    # Save updated events data back to JSON
    with open(events_json_path, "w") as f:
        json.dump(events, f, indent=4)

    print("✅ Duplicate photo paths removed from events.json.")

