import customtkinter as ctk 
from PIL import Image,ImageTk
from tkinter import filedialog
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import datetime as dt
import json
import shutil
import os
import cv2  #pip install opencv-python
import threading
import time
import winsound
import Train
import Sort
import whatsapp
import cleanup

BASIC_JSON=r"Basic.json"
EVENTS_JSON=r"Events.json"
# Global variables
current_theme = "light"
phone_number=""
whatsapp_message=""
cam=""

# -------------------Functions--------------------------
def load_basic():
    with open(BASIC_JSON) as f:
        data = json.load(f)
        global phone_number
        phone_number=data['Number']
        global whatsapp_message
        whatsapp_message=data['Whatsapp']
        global cam
        cam=data['Camera']
        global processing_mode
        processing_mode = data.get('Processing Mode', 'CPU')
        print(f"Camera: {cam}, Mode: {processing_mode}")

load_basic()

def load_events():
    if os.path.exists(EVENTS_JSON):
        with open(EVENTS_JSON, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def show_popup(title, message, font1, timeout=3000):
    popup = ctk.CTkToplevel()  
    popup.geometry("400x200")
    popup.title(title)
    
    # Make sure the popup is always on top
    popup.transient(root)  
    popup.grab_set()  
    popup.focus_force()  
    
    label = ctk.CTkLabel(popup, text=message, wraplength=350, font=font1)
    label.pack(pady=20)
    
    def close_popup():
        popup.destroy()
    
    # Auto-close the popup after 'timeout' milliseconds
    popup.after(timeout, close_popup)
    
    button = ctk.CTkButton(popup, text="OK", command=close_popup)
    button.pack(pady=10)

def change_theme():
    global current_theme
    # print(f"Current mode: {current_theme}")  # Debugging line
    if current_theme == "light":
        current_theme = "dark"
    else:
        current_theme = "light"
    # print(f"Setting new mode: {current_theme}")  # Debugging line
    ctk.set_appearance_mode(current_theme)

# -----------------Screen Functions---------------------
def open_add_screen():
    def create_folder():
        # Get the folder path from the entry box and the folder name to create
        base_path = file_var.get()
        folder_name = Eventname.get()
        
        if base_path and folder_name:
            new_folder_path = os.path.join(base_path, folder_name)
            try:
                os.makedirs(new_folder_path)  # Create the new folder
                status_label.configure(text=f"Folder '{folder_name}' created successfully!", fg_color="green")
                save_event()
            except FileExistsError:
                status_label.configure(text=f"Folder '{folder_name}' already exists.", fg_color='red')
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", fg_color="red")
            

    def browse_file():
        file_path = filedialog.askdirectory() # Open file picker dialog
        if file_path:
            file_var.set(file_path)

    def save_event():
        file_loc=f"{file_var.get()}/{Eventname.get()}"
        event_data = {
            "Event Name": Eventname.get(),
            "Event Date": Eventdate.get(),
            "Event Owner": Eventowner.get(),
            "Contact Number": Number.get(),
            "File Location": file_loc,
            "Guests":[]
        }
        
        file_path = EVENTS_JSON
        events = []
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    events = json.load(file)
                except json.JSONDecodeError:
                    events = []
        
        events.append(event_data)
        
        with open(file_path, "w") as file:
            json.dump(events, file, indent=4)
        
        print("Event saved successfully!")
        
    # def validate_inputs(*args):
    #     """ Enable Capture button only if all fields are filled and phone number is valid """
    #     if Eventname.get() and Eventdate.get() and Eventowner.get() and file_var.get() and Number.get().isdigit() and len(Number.get()) == 10:
    #         save_btn.configure(state="normal")
    #     else:
    #         save_btn.configure(state="disabled")
    for widget in root.winfo_children():
        widget.destroy()

    # Add new widgets (new window content)
    title_frame=ctk.CTkFrame(root,width=1400,height=60,fg_color=('#6f6f6f','#bdbdbd'))
    title_frame.pack_propagate(False)
    label = ctk.CTkLabel(title_frame, text="Add New Event", font=("System", 50))
    back_btn = ctk.CTkButton(title_frame, text="Go Back",
                             width=50, command=load_main_screen)
    back_btn.pack(side='left',padx=10)
    label.pack(expand=True)
    title_frame.pack()

    frame1 = ctk.CTkFrame(root)
    frame1.pack(side='top',pady=20)

    Eventname=ctk.StringVar()
    Eventdate=ctk.StringVar()
    Eventowner=ctk.StringVar()
    Number=ctk.StringVar()
    file_var = ctk.StringVar()

    ctk.CTkLabel(frame1,text='Event Name',font=("System", 20)).pack(side='left',padx=10,pady=10)
    ctk.CTkEntry(frame1,textvariable=Eventname).pack(side='left',padx=10,pady=10)

    frame2 = ctk.CTkFrame(root)
    frame2.pack(side='top',pady=20)

    ctk.CTkLabel(frame2,text='Event Date\n(DD/MM/YYYY)',font=("System", 20)).pack(side='left',padx=10,pady=10)
    ctk.CTkEntry(frame2,textvariable=Eventdate).pack(side='left',padx=10,pady=10)
    ctk.CTkButton(frame2,text='Today\'s Date',width=50,command=lambda: Eventdate.set(dt.datetime.now().strftime("%d/%m/%Y"))).pack(side='left',padx=10,pady=10)

    frame3 = ctk.CTkFrame(root)
    frame3.pack(side='top',pady=20)
    ctk.CTkLabel(frame3,text='Event Owner',font=("System", 20)).pack(side='left',padx=10,pady=10)
    ctk.CTkEntry(frame3,textvariable=Eventowner).pack(side='left',padx=10,pady=10)

    ctk.CTkLabel(frame3,text='Contact Number',font=("System", 20)).pack(side='left',padx=10,pady=10)
    ctk.CTkEntry(frame3,textvariable=Number).pack(side='left',padx=10,pady=10)

    frame4 = ctk.CTkFrame(root)
    frame4.pack(side='top',pady=20)
    ctk.CTkLabel(frame4, text="Select Folder Location",font=("System", 20)).pack(pady=5)
    entry = ctk.CTkEntry(frame4, textvariable=file_var, state="readonly")  # Display file path
    entry.pack(side="left", padx=10, pady=10)
    browse_button = ctk.CTkButton(frame4, text="Browse", command=browse_file)
    browse_button.pack(side="left", padx=10)

    frame5 = ctk.CTkFrame(root)
    frame5.pack(side='top',pady=20)
    save_btn = ctk.CTkButton(frame5, text="Save Event",width=40, command=create_folder)
    save_btn.pack(pady=10)

    status_label = ctk.CTkLabel(frame5, text="", fg_color="red")
    status_label.pack(pady=5)
    # validate_inputs()

def open_remove_screen():
    def load_events():
        file_path = EVENTS_JSON
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_events(events):
        with open(EVENTS_JSON, "w") as file:
            json.dump(events, file, indent=5)

    def save_events_from_form():
        updated_events = []
        for entry in event_entries:
            event_name = entry["event_name"].get()
            event_date = entry["event_date"].get()
            event_owner = entry["event_owner"].get()
            contact_number = entry["contact_number"].get()
            file_location = entry["file_location"].get()

            # Preserve Guests if event already exists
            original_event = next((e for e in original_events if e["Event Name"] == event_name), None)

            updated_events.append({
                "Event Name": event_name,
                "Event Date": event_date,
                "Event Owner": event_owner,
                "Contact Number": contact_number,
                "File Location": file_location,
                "Guests": original_event["Guests"] if original_event else []  
            })

        save_events(updated_events)
        open_remove_screen()  # Refresh UI
        print("Events saved successfully!")

    def show_popup(title, message, confirm_action=None):
        """ Custom popup window """
        popup = ctk.CTkToplevel()
        popup.title(title)
        popup.geometry("400x200")
        popup.grab_set()  # Make popup modal

        ctk.CTkLabel(popup, text=message, font=("System", 16), wraplength=350).pack(pady=20)

        btn_frame = ctk.CTkFrame(popup)
        btn_frame.pack(pady=10)

        if confirm_action:  # Confirmation popup with Yes/No buttons
            ctk.CTkButton(btn_frame, text="Yes", fg_color="red", command=lambda: [confirm_action(), popup.destroy()]).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No", fg_color="gray", command=popup.destroy).pack(side="left", padx=10)
        else:  # Simple "OK" popup
            ctk.CTkButton(btn_frame, text="OK", command=popup.destroy).pack(pady=10)

    def remove_event(event_name):
        global original_events

        def confirm_delete():
            """ Executes deletion after confirmation """
            nonlocal event_name
            original_events = load_events()
            event_to_remove = next((e for e in original_events if e["Event Name"] == event_name), None)

            if event_to_remove:
                folder_path = event_to_remove["File Location"]

                # Delete event folder if exists
                if os.path.exists(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                        print(f"Deleted folder: {folder_path}")
                    except Exception as e:
                        print(f"Error deleting folder: {e}")

                # Remove event from JSON data
                updated_events = [e for e in original_events if e["Event Name"] != event_name]
                save_events(updated_events)  # Save updated list

                # Success message
                show_popup("Success", f"Event '{event_name}' has been removed.")
                open_remove_screen()  # Refresh UI
            else:
                show_popup("Error", "Event not found.")

        # Show confirmation popup
        show_popup("Warning", f"Are you sure you want to remove '{event_name}'? This action cannot be undone.", confirm_delete)


    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Title
    title_frame = ctk.CTkFrame(root, width=1400, height=60, fg_color=('#6f6f6f', '#bdbdbd'))
    title_frame.pack_propagate(False)
    title_frame.pack()
    back_btn = ctk.CTkButton(title_frame, text="Go Back",
                             width=50, command=load_main_screen)
    back_btn.pack(side='left',padx=10)    
    ctk.CTkLabel(title_frame, text="Update Events", font=("System", 50)).pack(expand=True)
    ctk.CTkButton(title_frame, text="Go Back", width=50, command=load_main_screen).pack(side='left', padx=10)

    frame = ctk.CTkFrame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Load existing events
    original_events = load_events()
    event_entries = []

    # Create table headers
    headers = ["Event Name", "Event Date", "Event Owner", "Contact Number", "File Location", "Actions"]
    for col, header in enumerate(headers):
        ctk.CTkLabel(frame, text=header, font=("System", 14, "bold")).grid(row=0, column=col, padx=5, pady=5)

    # Create form fields dynamically
    for row, event in enumerate(original_events, start=1):
        entry_dict = {}
        entry_dict["event_name"] = ctk.CTkEntry(frame)
        entry_dict["event_date"] = ctk.CTkEntry(frame)
        entry_dict["event_owner"] = ctk.CTkEntry(frame)
        entry_dict["contact_number"] = ctk.CTkEntry(frame)
        entry_dict["file_location"] = ctk.CTkEntry(frame)

        entry_dict["event_name"].insert(0, event["Event Name"])
        entry_dict["event_date"].insert(0, event["Event Date"])
        entry_dict["event_owner"].insert(0, event["Event Owner"])
        entry_dict["contact_number"].insert(0, event["Contact Number"])
        entry_dict["file_location"].insert(0, event["File Location"])

        entry_dict["event_name"].grid(row=row, column=0, padx=5, pady=5)
        entry_dict["event_date"].grid(row=row, column=1, padx=5, pady=5)
        entry_dict["event_owner"].grid(row=row, column=2, padx=5, pady=5)
        entry_dict["contact_number"].grid(row=row, column=3, padx=5, pady=5)
        entry_dict["file_location"].grid(row=row, column=4, padx=5, pady=5)

        # Remove button for each event
        remove_btn = ctk.CTkButton(frame, text="Remove", fg_color="red",command=lambda name=event["Event Name"]: remove_event(name))

        remove_btn.grid(row=row, column=5, padx=5, pady=5)

        event_entries.append(entry_dict)

    # Save button
    ctk.CTkButton(root, text="Save", command=save_events_from_form).pack(pady=10)

def open_automate_screen():
    def magic():
        event_name = event.get().strip()
        events = load_events()

        event_info = next((e for e in events if e["Event Name"] == event_name), None)
        if not event_info:
            print("⚠️ No event selected or event not found!")
            status_label.configure(text="⚠️ No event selected!", text_color="red")
            return
            
        file_directory = event_info["File Location"]
        selected_path = file_loc.get().strip()  # User-selected directory
        final_directory = selected_path if selected_path else file_directory
        
        ok_button.configure(state="disabled")
        status_label.configure(text="Starting process...", text_color="white")
        progress_bar.set(0)
        eta_label.configure(text="ETA: Calculating...")
        
        embeded_dir = file_directory + f"/events_models/{event_name}_face_embeddings.pkl"
        should_train = True
        
        # Check if model exists and ask to retrain
        if os.path.exists(embeded_dir):
            from tkinter import messagebox
            should_train = messagebox.askyesno("Retrain Model?", "A trained model for this event already exists.\n\nDo you want to retrain the model?\n(Select 'No' to use the existing model and skip to Sorting)")
        
        # Start background thread
        threading.Thread(target=run_magic_thread, args=(event_name, file_directory, final_directory, should_train), daemon=True).start()

    def run_magic_thread(event_name, file_directory, final_directory, should_train):
        start_time = [time.time()]
        
        def progress_callback(current, total, phase_name):
            if total > 0:
                percent = current / total
                elapsed = time.time() - start_time[0]
                if current > 0:
                    eta_seconds = (elapsed / current) * (total - current)
                    m, s = divmod(int(eta_seconds), 60)
                    eta_text = f"ETA: {m}m {s}s"
                else:
                    eta_text = "ETA: Calculating..."
            else:
                percent = 1.0
                eta_text = "ETA: 0m 0s"
                
            def update_ui():
                status_label.configure(text=f"{phase_name} ({current}/{total})", text_color="cyan")
                progress_bar.set(percent)
                eta_label.configure(text=eta_text)
            
            root.after(0, update_ui)

        def wrap_phase(phase_func, *args, **kwargs):
            start_time[0] = time.time()
            return phase_func(*args, **kwargs)

        try:
            # Training
            if should_train:
                accuracy = wrap_phase(Train.train_face_recognition, file_directory, event_name, progress_callback)
                if accuracy is not None:
                    # Show testing accuracy phase in progress bar
                    progress_callback(100, 100, f"Testing Accuracy: {accuracy:.1f}%")
                    time.sleep(2)  # Pause to let the user see the accuracy
                cleanup.remove_unknown(EVENTS_JSON)
            else:
                progress_callback(100, 100, "Training Skipped")
                time.sleep(1)
            
            # Sorting
            embeded_dir = file_directory + f"/events_models/{event_name}_face_embeddings.pkl"
            if not os.path.exists(embeded_dir):
                raise Exception("Face embedding model not found. Training might have failed.")
                
            cleanup.delete_generated_images(final_directory)
            wrap_phase(Sort.sort_face_recognition, embeded_dir, final_directory, EVENTS_JSON, event_name, progress_callback=progress_callback)
            cleanup.remove_unknown(EVENTS_JSON)
            
            # WhatsApp
            wrap_phase(whatsapp.send_whatsapp_messages, BASIC_JSON, EVENTS_JSON, event_name, final_directory, progress_callback)
            cleanup.delete_generated_images(final_directory)
            
            def final_ui():
                status_label.configure(text="✅ All Tasks Completed Successfully!", text_color="green")
                progress_bar.set(1.0)
                eta_label.configure(text="")
                ok_button.configure(state="normal")
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            
            root.after(0, final_ui)
            
        except Exception as e:
            def error_ui():
                status_label.configure(text=f"❌ Error: {str(e)}", text_color="red")
                ok_button.configure(state="normal")
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            root.after(0, error_ui)

    def browse_file():
        file_path = filedialog.askdirectory()  # Open file picker dialog
        if file_path:
            file_loc.set(file_path)  # Store selected path in entry field

    def load_events():
        """Load events from JSON file."""
        if os.path.exists(EVENTS_JSON):
            with open(EVENTS_JSON, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def populate_combobox():
        """Populate combo box with event names."""
        events = load_events()
        event_names = [event["Event Name"] for event in events]
        Event_combo.configure(values=tuple(event_names))

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Add new widgets (new window content)
    title_frame = ctk.CTkFrame(root, width=1400, height=60, fg_color=('#6f6f6f', '#bdbdbd'))
    title_frame.pack_propagate(False)
    label = ctk.CTkLabel(title_frame, text="Magic ✨", font=("System", 50))
    back_btn = ctk.CTkButton(title_frame, text="Go Back", width=50, command=load_main_screen)
    back_btn.pack(side='left', padx=10)
    label.pack(expand=True)
    title_frame.pack()

    event = ctk.StringVar()
    file_loc = ctk.StringVar()
    
    frame1 = ctk.CTkFrame(root)
    frame1.pack(expand=True)
    
    ctk.CTkLabel(frame1, text="Select Event", font=("System", 20)).pack(side='left', padx=10, pady=10)
    Event_combo = ctk.CTkComboBox(frame1, variable=event, command=lambda _: print(event.get()))
    Event_combo.pack(side='left', padx=10, pady=10)
    populate_combobox()

    frame2 = ctk.CTkFrame(root)
    frame2.pack(expand=True)
    
    ctk.CTkLabel(frame2, text="Select Path to your\nPhotos folder", font=("System", 20)).pack(side='left', padx=10, pady=10)
    entry = ctk.CTkEntry(frame2, textvariable=file_loc, state="readonly")  # Display file path
    entry.pack(side="left", padx=10, pady=10)
    browse_button = ctk.CTkButton(frame2, text="Browse", width=30, command=browse_file)
    browse_button.pack(side="left", padx=10)
    
    frame3 = ctk.CTkFrame(root)
    frame3.pack(expand=True)  
    ok_button = ctk.CTkButton(frame3, text="Ok", width=60,font=("System", 30), command=magic)
    ok_button.pack(side="left", padx=10)
    
    # Progress UI
    progress_frame = ctk.CTkFrame(root, fg_color="transparent")
    progress_frame.pack(expand=True, fill='x', padx=50, pady=10)
    
    status_label = ctk.CTkLabel(progress_frame, text="", font=("System", 20))
    status_label.pack(pady=5)
    
    progress_bar = ctk.CTkProgressBar(progress_frame, width=600, height=20, corner_radius=10, progress_color="#1E90FF")
    progress_bar.set(0)
    progress_bar.pack(pady=10)
    
    eta_label = ctk.CTkLabel(progress_frame, text="", font=("System", 16, "italic"), text_color="gray")
    eta_label.pack(pady=5)

def open_capture_screen():
    def capture():
        print('Capturing...')
        show_popup('Get Ready', 'Smile 😁', font1=('', 50))

        def generate_dataset():
            user_name = name.get().strip()
            user_id = number.get().strip()  # Using phone number as the folder name
            event_name = eventname.get().strip()

            file_path = EVENTS_JSON
            events = load_events()

            # Add guest information to the event
            for event in events:
                if event["Event Name"] == event_name:
                    event["Guests"].append({
                        "name": user_name,
                        "whatsapp Number": user_id,
                        "photos": []
                    })
                    break

            # Save updated event data back to JSON
            with open(file_path, "w") as file:
                json.dump(events, file, indent=4)

            # Create a folder for the user using their phone number inside the event's guest folder
            event_folder = next(event for event in events if event["Event Name"] == event_name)["File Location"]
            event_guests_folder = os.path.join(event_folder, "guests_folder")
            os.makedirs(event_guests_folder, exist_ok=True)

            user_folder = os.path.join(event_guests_folder, str(user_id))  # Store data under phone number
            os.makedirs(user_folder, exist_ok=True)

            # Open camera and start capturing
            camera_index = int(cam.split()[-1])
            print(f"Using camera index: {camera_index}")
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print("❌ Failed to open camera.")
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                show_popup("Camera Error", "Camera is unavailable or in use by another app.", font1=("System", 16))
                return
                
            img_id = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to capture image.")
                    break

                img_id += 1

                # Save color image (without cropping or converting to grayscale)
                file_name_path = os.path.join(user_folder, f"{img_id}.jpg")
                cv2.imwrite(file_name_path, frame)

                # Display captured image with count
                cv2.putText(frame, str(img_id), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Captured Image", frame)

                if cv2.waitKey(1) == 13 or img_id == 100:  # Stop after collecting 100 images
                    break

            cap.release()
            cv2.destroyAllWindows()
            print(f"✅ Data collection completed for {user_name} (Phone: {user_id})")

        generate_dataset()

    def load_events():
        file_path = EVENTS_JSON
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []
    
    def open_camera():
        selected_index = int(cam.split()[-1])
        cap = cv2.VideoCapture(selected_index)
        if not cap.isOpened():
            print("Failed to open camera")
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            show_popup("Camera Error", "Camera is unavailable.", font1=("System", 16))
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    def populate_combobox():
        events = load_events()
        event_names = [event["Event Name"] for event in events]
        combo_box.configure(values=tuple(event_names))

    def validate_inputs(*args):
        """ Enable Capture button only if all fields are filled and phone number is valid """
        if eventname.get() and name.get() and number.get().isdigit() and len(number.get()) == 10:
            capture_btn.configure(state="normal")
        else:
            capture_btn.configure(state="disabled")

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Add new widgets (new window content)
    title_frame = ctk.CTkFrame(root, width=1400, height=60, fg_color=('#6f6f6f','#bdbdbd'))
    title_frame.pack_propagate(False)
    label = ctk.CTkLabel(title_frame, text="Capture", font=("System", 50))
    back_btn = ctk.CTkButton(title_frame, text="Go Back", width=50, command=load_main_screen)
    back_btn.pack(side='left', padx=10)
    label.pack(expand=True)
    title_frame.pack()

    eventname = ctk.StringVar()
    name = ctk.StringVar()
    number = ctk.StringVar()

    # Attach validation to input variables
    eventname.trace_add("write", validate_inputs)
    name.trace_add("write", validate_inputs)
    number.trace_add("write", validate_inputs)

    frame1 = ctk.CTkFrame(root)
    frame1.pack(expand=True)

    ctk.CTkLabel(frame1, text='Event Name').pack(side='left', padx=10, pady=10)
    combo_box = ctk.CTkComboBox(frame1, variable=eventname)
    combo_box.pack(side='left', padx=10, pady=10)
    populate_combobox()

    ctk.CTkLabel(frame1, text='Name').pack(side='left', padx=10, pady=10)
    ctk.CTkEntry(frame1, textvariable=name).pack(side='left', padx=10, pady=10)

    frame2 = ctk.CTkFrame(root)
    frame2.pack(expand=True)   
    ctk.CTkLabel(frame2, text='Phone Number\n(Whatsapp)').pack(side='left', padx=10, pady=10)
    ctk.CTkEntry(frame2, textvariable=number).pack(side='left', padx=10, pady=10) 

    frame3 = ctk.CTkFrame(root)
    frame3.pack(expand=True)
    ctk.CTkButton(frame3, text="Check Camera", font=("System", 20), command=open_camera).pack(side='left',padx=10)

    frame4 = ctk.CTkFrame(root)
    frame4.pack(expand=True)  
    capture_btn = ctk.CTkButton(frame4, text='Capture', font=("System", 30), command=capture, state="disabled")
    capture_btn.pack()

    validate_inputs()  # Initial check to disable button if fields are empty

def open_update_screen():
    def update():
        msg=whatsapp_text.get("0.0", "end").strip()
        cam=camera.get()
        mode=proc_mode.get()
        delivery = delivery_mode.get()
        # camera.set("")
        # whatsapp_text.insert("0.0","")
        # write a code to write the data into the file Basic.json
        with open(BASIC_JSON, 'r') as f:
            data = json.load(f)
            data['Number'] = new_num.get()
            data['Whatsapp'] = msg
            data['Camera']=cam
            data['Processing Mode'] = mode
            data['WhatsApp Delivery Method'] = delivery
            with open(BASIC_JSON, 'w') as f:
                json.dump(data, f, indent=4)
        
        # Update global variables
        global whatsapp_message, processing_mode
        whatsapp_message = msg
        processing_mode = mode
        show_popup("Success", "Settings updated successfully!", font1=("System", 16))

    def get_available_cameras():
        cameras = []
        for i in range(5):  # Checking up to 5 camera indexes
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(f"Camera {i}")
                cap.release()
        return cameras if cameras else ["No Cameras Found"]
    
    def open_camera():
        selected_index = int(camera.get().split()[-1])
        cap = cv2.VideoCapture(selected_index)
        if not cap.isOpened():
            print("Failed to open camera")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()  

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    camera_list=get_available_cameras()
    # Add new widgets (new window content)
    title_frame=ctk.CTkFrame(root,width=1400,height=60,fg_color=('#6f6f6f','#bdbdbd'))
    title_frame.pack_propagate(False)
    label = ctk.CTkLabel(title_frame, text="Update Your Details", font=("System", 50))
    back_btn = ctk.CTkButton(title_frame, text="Go Back",
                             width=50, command=load_main_screen)
    back_btn.pack(side='left',padx=10)
    label.pack(expand=True)
    title_frame.pack()
    new_num=ctk.StringVar()
    new_num.set(phone_number)

    frame1 = ctk.CTkFrame(root)
    frame1.pack(expand=True)
    ctk.CTkLabel(frame1,text="Update Phone Number",font=("System", 20)).pack(side='left',padx=10,pady=10)
    ctk.CTkEntry(frame1,textvariable=new_num).pack(side='left',padx=10,pady=10)

    frame2=ctk.CTkFrame(root)
    frame2.pack(expand=True)
    ctk.CTkLabel(frame2,text="Whatsapp Message\n(Use @USERNAME for mentioning\nthe particular guest)",font=("System", 20)).pack(side='left',padx=10,pady=10)
    whatsapp_text=ctk.CTkTextbox(frame2,wrap='word')
    whatsapp_text.pack(side='left',padx=10,pady=10)
    whatsapp_text.insert("0.0",f'{whatsapp_message}')
    
    frame3=ctk.CTkFrame(root)
    frame3.pack(expand=True)
    ctk.CTkLabel(frame3, text="Select Camera:").pack(side='left',padx=10)
    camera = ctk.StringVar(value=cam if cam in camera_list else (camera_list[0] if camera_list else "No Cameras Found"))
    ctk.CTkComboBox(frame3, values=camera_list, variable=camera).pack(side='left',padx=10)
    ctk.CTkButton(frame3, text="Open Camera", command=open_camera).pack(side='left',padx=10)

    frame_mode = ctk.CTkFrame(root)
    frame_mode.pack(expand=True)
    ctk.CTkLabel(frame_mode, text="Processing Mode:", font=("System", 20)).pack(side='left', padx=10)
    proc_mode = ctk.StringVar(value=processing_mode)
    ctk.CTkRadioButton(frame_mode, text="CPU", variable=proc_mode, value="CPU").pack(side='left', padx=5)
    ctk.CTkRadioButton(frame_mode, text="GPU", variable=proc_mode, value="GPU").pack(side='left', padx=5)

    # Load current delivery method for default value
    try:
        with open(BASIC_JSON, 'r') as f:
            basic_data = json.load(f)
            current_delivery = basic_data.get("WhatsApp Delivery Method", "PyAutoGUI")
    except:
        current_delivery = "PyAutoGUI"

    frame_delivery = ctk.CTkFrame(root)
    frame_delivery.pack(expand=True)
    ctk.CTkLabel(frame_delivery, text="WhatsApp Delivery:", font=("System", 20)).pack(side='left', padx=10)
    delivery_mode = ctk.StringVar(value=current_delivery)
    ctk.CTkRadioButton(frame_delivery, text="PyAutoGUI (Simple)", variable=delivery_mode, value="PyAutoGUI").pack(side='left', padx=5)
    ctk.CTkRadioButton(frame_delivery, text="Selenium (Robust)", variable=delivery_mode, value="Selenium").pack(side='left', padx=5)

    frame4=ctk.CTkFrame(root)
    frame4.pack(expand=True)

    ctk.CTkButton(frame4, text='Update', font=("System",20),command=update).pack(side='left',padx=10,pady=10)

def open_watermark_screen():
    file_path = "Basic.json"

    # Load existing JSON data if available
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # If JSON is corrupted, start fresh
    else:
        data = {}

    # Initialize variables with existing data or default values
    watermark_text = ctk.StringVar(value=data.get("Whatsapp", ""))
    watermark_image = ctk.StringVar(value=data.get("WaterMark Image", ""))
    watermark_posi = ctk.StringVar(value=data.get("WaterMark Location", "bottom-right"))
    watermark_opacity = ctk.DoubleVar(value=float(data.get("WaterMark Opacity", 1.0)))
    watermark_scale = ctk.DoubleVar(value=float(data.get("WaterMark Scale", 0.2)))

    def update_watermark_info():
        """ Saves watermark details (text, position, opacity, scale, image path) to 'Basic.json' """
        try:
            data["Whatsapp"] = watermark_text.get() if watermark_text.get() else data.get("Whatsapp", "")
            data["WaterMark Location"] = watermark_posi.get()
            data["WaterMark Image"] = watermark_image.get()
            data["WaterMark Opacity"] = watermark_opacity.get()
            data["WaterMark Scale"] = watermark_scale.get()

            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            print("✅ Watermark details updated successfully in JSON.")
            show_popup("Success", "Watermark settings saved!", font1=("System", 16))
        except Exception as e:
            print(f"❌ Error updating JSON: {e}")

    def select_watermark_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            watermark_image.set(file_path)
            refresh_preview()

    def refresh_preview(*args):
        """ Dynamically composite the watermark on the sample image to show a live preview """
        try:
            sample_path = "Sample photo.png"
            wm_path = watermark_image.get()
            
            if not os.path.exists(sample_path):
                img = Image.new("RGB", (800, 600), "grey")
            else:
                img = Image.open(sample_path).convert("RGBA")
            
            # Thumbnail size bounds to keep preview responsive
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            if wm_path and os.path.exists(wm_path):
                watermark = Image.open(wm_path).convert("RGBA")
                opac = watermark_opacity.get()
                scale = watermark_scale.get()
                pos = watermark_posi.get()

                if opac < 1.0:
                    alpha = watermark.split()[3]
                    alpha = alpha.point(lambda p: p * opac)
                    watermark.putalpha(alpha)

                wm_width = int(img.width * scale)
                wm_height = int((watermark.height / max(watermark.width, 1)) * wm_width)
                
                if wm_width > 0 and wm_height > 0:
                    watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)

                    positions = {
                        "top-left": (20, 20),
                        "top-center": ((img.width - wm_width) // 2, 20),
                        "top-right": (img.width - wm_width - 20, 20),
                        "center-left": (20, (img.height - wm_height) // 2),
                        "center": ((img.width - wm_width) // 2, (img.height - wm_height) // 2),
                        "center-right": (img.width - wm_width - 20, (img.height - wm_height) // 2),
                        "bottom-left": (20, img.height - wm_height - 20),
                        "bottom-center": ((img.width - wm_width) // 2, img.height - wm_height - 20),
                        "bottom-right": (img.width - wm_width - 20, img.height - wm_height - 20)
                    }
                    final_pos = positions.get(pos, positions["bottom-right"])
                    img.paste(watermark, final_pos, watermark)

            img_tk = ImageTk.PhotoImage(img)
            preview_label.configure(image=img_tk, text="")
            preview_label.image = img_tk
        except Exception as e:
            print(f"❌ Error updating preview: {e}")

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Title Bar
    title_frame = ctk.CTkFrame(root, width=1400, height=60, fg_color=('#6f6f6f', '#bdbdbd'))
    title_frame.pack_propagate(False)
    title_frame.pack()
    label = ctk.CTkLabel(title_frame, text="Watermark Settings", font=("System", 50))
    back_btn = ctk.CTkButton(title_frame, text="Go Back", width=50, command=load_main_screen)
    back_btn.pack(side='left', padx=10)
    label.pack(side="left", padx=10, expand=True)

    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    # Left controls
    controls_frame = ctk.CTkFrame(main_frame, width=300)
    controls_frame.pack(side="left", fill="y", padx=10)
    
    ctk.CTkButton(controls_frame, text="Select Watermark Image", command=select_watermark_image).pack(pady=20)
    
    ctk.CTkLabel(controls_frame, text="Opacity", font=("System", 16)).pack(pady=(10,0))
    ctk.CTkSlider(controls_frame, from_=0.1, to=1.0, variable=watermark_opacity, command=refresh_preview).pack(pady=5)
    
    ctk.CTkLabel(controls_frame, text="Size (Scale)", font=("System", 16)).pack(pady=(10,0))
    ctk.CTkSlider(controls_frame, from_=0.05, to=0.8, variable=watermark_scale, command=refresh_preview).pack(pady=5)
    
    ctk.CTkLabel(controls_frame, text="Position", font=("System", 16)).pack(pady=(20,5))
    pos_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    pos_frame.pack(pady=5)
    
    posi = ["top-left", "top-center", "top-right", "center-left", "center", "center-right", "bottom-left", "bottom-center", "bottom-right"]
    n = 0
    for i in range(3):
        for j in range(3):
            ctk.CTkRadioButton(pos_frame, text=posi[n].split('-')[0].capitalize(), value=posi[n], variable=watermark_posi, command=refresh_preview, width=60).grid(row=i, column=j, padx=5, pady=5)
            n += 1
            
    ctk.CTkButton(controls_frame, text="Save Settings", font=("System", 20), command=update_watermark_info, fg_color="#1E90FF").pack(side="bottom", pady=20)
    
    # Right preview
    preview_frame = ctk.CTkFrame(main_frame)
    preview_frame.pack(side="right", expand=True, fill="both", padx=10)
    
    ctk.CTkLabel(preview_frame, text="Live Preview", font=("System", 20)).pack(pady=10)
    preview_label = ctk.CTkLabel(preview_frame, text="Loading preview...", fg_color="black")
    preview_label.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Initial render
    refresh_preview()

# Function to Load Main Screen
def load_main_screen():
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Title Bar
    title_frame = ctk.CTkFrame(root, width=1400, height=80, fg_color=('#6f6f6f', '#bdbdbd'))
    title_frame.pack_propagate(False)
    title_frame.pack()

    # Theme Switch
    ctk.CTkSwitch(title_frame,
                  text='Theme',
                  font=('Rockwell', 20),
                  switch_width=60,
                  switch_height=30,
                  button_color=('#fef6f6', '#2038b2'),
                  text_color=('#fef6f6', '#2038b2'),
                  command=change_theme).pack(side='left', pady=10, padx=10)

    # Load Logo Image
    logo_image = ctk.CTkImage(light_image=Image.open("Logo.png"), size=(80,80))

    # Add Logo Instead of Text
    logo_label = ctk.CTkLabel(title_frame, image=logo_image, text="")  # Empty text to display only the image
    logo_label.pack(side='right', padx=10)

    # Title Text
    ctk.CTkLabel(title_frame, text="Aura Snap", font=("Vineta BT", 60)).pack(expand=True, side='left')

    # Main Screen Content
    frame0 = ctk.CTkFrame(root, corner_radius=10)
    frame0.pack(expand=True)
    ctk.CTkLabel(frame0, text="Main Menu", font=("System", 40), text_color=('#2038b2', '#fef6f6')).pack(expand=True, side='left')

    frame1 = ctk.CTkFrame(root, corner_radius=10)
    frame1.pack(expand=True)
    ctk.CTkButton(frame1, text='Add event', font=('Rockwell', 30), width=200, height=80, command=open_add_screen).pack(side='left', padx=20, pady=10)
    ctk.CTkButton(frame1, text='Update Event', font=('Rockwell', 30), width=200, height=80, command=open_remove_screen).pack(side='left', padx=20, pady=10)
    ctk.CTkButton(frame1, text='Capture', font=('Rockwell', 30), width=200, height=80, command=open_capture_screen).pack(side='left', padx=20, pady=10)

    frame2 = ctk.CTkFrame(root, corner_radius=10)
    frame2.pack(expand=True)
    ctk.CTkButton(frame2, text='Magic ✨', font=('Rockwell', 30), width=200, height=80, command=open_automate_screen).pack(side='left', padx=20, pady=10)
    ctk.CTkButton(frame2, text='Watermark', font=('Rockwell', 30), width=200, height=80, command=open_watermark_screen).pack(side='left', padx=20, pady=10)

    frame3 = ctk.CTkFrame(root, corner_radius=10)
    frame3.pack(expand=True)
    ctk.CTkButton(frame3, text='Update My Details', font=('Rockwell', 30), width=200, height=80, command=open_update_screen).pack(side='left', padx=20, pady=10)

    ctk.CTkLabel(root, text=f'📞 {phone_number}', font=("System", 30), text_color=('#2038b2', '#fef6f6')).pack(side='right', padx=5, pady=5)

# ---------------MAIN-------------------#
root = ctk.CTk()
root.geometry("1400x800")  # Adjust as needed
root.title("Aura Snap")
# Load the Main Screen
root.iconbitmap("Logo.ico")
load_main_screen()

# Run the App
root.mainloop()