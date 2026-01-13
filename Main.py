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

# Custom FILES
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
        print(cam)

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
    ctk.CTkButton(root, text='Update', font=("System",15),command=fb.sync_events).pack(padx=10,pady=10)

def open_automate_screen():
    def magic():
        event_name = event.get().strip()
        events = load_events()

        event_info = next((e for e in events if e["Event Name"] == event_name), None)
        if event_info:
            file_directory = event_info["File Location"]
            selected_path = file_loc.get().strip()  # User-selected directory

            final_directory = selected_path if selected_path else file_directory

            print(f"📂 Selected Event Directory: {file_directory}")
            print(f"📂 User-Selected Directory: {selected_path}")
            print(f"✅ Using Directory for Sorting: {final_directory}")

            # **Ensure train completes before sorting**
            Train.train_face_recognition(file_directory, event.get())  # Block execution until training is done
            cleanup.remove_unknown(EVENTS_JSON)
            print("✅ Training completed. Proceeding to sorting...")
            embeded_dir=file_directory+f"/events_models/{event.get()}_face_embeddings.pkl"
            cleanup.delete_generated_images(entry.get())
            Sort.sort_face_recognition(embeded_dir,entry.get(),EVENTS_JSON,event.get()) 
            cleanup.remove_unknown(EVENTS_JSON) # Now call sorting
            whatsapp.send_whatsapp_messages(BASIC_JSON,EVENTS_JSON,event.get(),entry.get())
            cleanup.delete_generated_images(entry.get())  # Keep as is
        else:
            print("⚠️ No event selected or event not found!")

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
    ctk.CTkButton(frame3, text="Ok", width=60,font=("System", 30), command=magic).pack(side="left", padx=10)

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
        number=new_num.get()
        new_num.set("")
        msg=whatsapp_text.get("0.0", "end")
        cam=camera.get()
        camera.set("")
        whatsapp_text.insert("0.0","")
        # write a code to write the data into the file Basic.json
        with open(BASIC_JSON, 'r') as f:
            data = json.load(f)
            data['Number'] = number
            data['Whatsapp'] = msg
            data['Camera']=cam
            with open(BASIC_JSON, 'w') as f:
                json.dump(data, f, indent=4)

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
    camera = ctk.StringVar(value=camera_list[0] if camera_list else "No Cameras Found")
    ctk.CTkComboBox(frame3, values=camera_list, variable=camera).pack(side='left',padx=10)
    ctk.CTkButton(frame3, text="Open Camera", command=open_camera).pack(side='left',padx=10)

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
    watermark_posi = ctk.StringVar(value=data.get("WaterMark Location", ""))

    def update_watermark_info():
        """ Saves watermark details (text, position, and image path) to 'Basic.json' """
        try:
            # Update watermark details
            data["Whatsapp"] = watermark_text.get() if watermark_text.get() else data.get("Whatsapp", "")
            data["WaterMark Location"] = watermark_posi.get() if watermark_posi.get() else data.get("WaterMark Location", "")
            data["WaterMark Image"] = watermark_image.get() if watermark_image.get() else data.get("WaterMark Image", "")

            # Save updated data back to file
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

            print("✅ Watermark details updated successfully in JSON.")

        except Exception as e:
            print(f"❌ Error updating JSON: {e}")

    def select_watermark_image():
        """ Opens file dialog to select image, updates label and stores image path """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            watermark_image.set(file_path)
            update_image_preview(file_path)
            print(f"✅ Selected watermark image: {file_path}")

    def update_image_preview(img_path):
        """ Updates the preview image after selection """
        try:
            img = Image.open(img_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)  # Resize image to 100x100 px
            img_tk = ImageTk.PhotoImage(img)
            image_label.configure(image=img_tk, text="")  # Remove text when image is displayed
            image_label.image = img_tk  # Keep reference to avoid garbage collection
        except Exception as e:
            print(f"❌ Error displaying image: {e}")

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Title Bar
    title_frame = ctk.CTkFrame(root, width=1400, height=60, fg_color=('#6f6f6f', '#bdbdbd'))
    title_frame.pack_propagate(False)
    title_frame.pack()

    label = ctk.CTkLabel(title_frame, text="Add Watermark", font=("System", 50))

    back_btn = ctk.CTkButton(title_frame, text="Go Back", width=50, command=load_main_screen)
    back_btn.pack(side='left', padx=10)
    label.pack(side="left", padx=10, expand=True)

    # Watermark Image Selection
    frame2 = ctk.CTkFrame(root)
    frame2.pack(pady=10, expand=True)
    ctk.CTkLabel(frame2, text="Watermark Image", font=("System", 20)).pack(side='left', padx=10)
    ctk.CTkButton(frame2, text="Select Image", command=select_watermark_image).pack(side='left', padx=10)

    # Image Preview (Default: Empty)
    image_label = ctk.CTkLabel(root, text="No Image Selected", width=100, height=100, fg_color="gray")
    image_label.pack(pady=10)

    # If an existing image is found, display it
    if watermark_image.get():
        update_image_preview(watermark_image.get())

    # Watermark Position Selection
    frame3 = ctk.CTkFrame(root)
    frame3.pack(pady=10, expand=True)
    ctk.CTkLabel(frame3, text="Select the position", font=("System", 20)).grid(row=0, column=1, pady=5)

    posi = ["top-left", "top-center", "top-right", "center-left", "center", "center-right", "bottom-left", "bottom-center", "bottom-right"]
    positions = [[(i, j) for j in range(3)] for i in range(3)]  # 3x3 grid positions

    n = 0
    for i, row in enumerate(positions):
        for j, pos in enumerate(row):
            ctk.CTkRadioButton(frame3, text=posi[n], value=posi[n], variable=watermark_posi).grid(row=i+1, column=j, padx=5, pady=5)
            n += 1

    # Set the pre-selected radio button for position
    if watermark_posi.get():
        watermark_posi.set(data.get("WaterMark Location", ""))

    # Submit Button
    ctk.CTkButton(root, text="Submit", width=50, command=update_watermark_info).pack(side='bottom', pady=100)

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
    logo_image = ctk.CTkImage(light_image=Image.open("Final/Logo.png"), size=(80,80))

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
root.iconbitmap("Final 2/Logo.ico")
load_main_screen()

# Run the App
root.mainloop()