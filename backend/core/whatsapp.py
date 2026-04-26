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
import socket

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Check if there is an active internet connection.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def send_whatsapp_messages(settings_path, json_path, event_name, image_folder, progress_callback=None):
    """
    Sends WhatsApp messages with watermarked images, avoiding duplicates.
    Routes to either PyAutoGUI or Selenium based on settings.
    """
    if not check_internet_connection():
        raise Exception("No Internet Connection detected. Please connect to the internet to send WhatsApp messages.")

    try:
        with open(settings_path, "r") as settings_file:
            settings = json.load(settings_file)

        default_message = settings.get("Whatsapp", "This is a default Message.")
        watermark_image = settings.get("WaterMark Image", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "Logo.png"))
        watermark_position = settings.get("WaterMark Location", "bottom-right")
        watermark_opacity = float(settings.get("WaterMark Opacity", 1.0))
        watermark_scale = float(settings.get("WaterMark Scale", 0.2))
        delivery_method = settings.get("WhatsApp Delivery Method", "PyAutoGUI")
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

    total_photos = sum(len(guest.get("photos", [])) for guest in event["Guests"])
    processed_photos = [0]  # Using a list to pass by reference

    for guest in event["Guests"]:
        guest_name = guest["name"]
        whatsapp_number = guest["whatsapp Number"]
        photos = guest["photos"]

        if not photos:
            continue

        message = f"Hello {guest_name}, {default_message}"

        if delivery_method == "Selenium":
            _send_via_selenium(guest_name, whatsapp_number, photos, watermark_image, watermark_position, watermark_opacity, watermark_scale, message, sent_images, progress_callback, processed_photos, total_photos)
        else:
            _send_via_pyautogui(guest_name, whatsapp_number, photos, watermark_image, watermark_position, watermark_opacity, watermark_scale, message, sent_images, progress_callback, processed_photos, total_photos)

    cleanup_images(image_folder)
    time.sleep(5)
    
    if progress_callback:
        progress_callback(total_photos, total_photos, "Sending WhatsApp Messages")

def _send_via_pyautogui(guest_name, whatsapp_number, photos, watermark_image, watermark_position, watermark_opacity, watermark_scale, message, sent_images, progress_callback, processed_photos, total_photos):
    """
    Improved PyAutoGUI method utilizing pywhatkit's native tab management.
    """
    for i, photo in enumerate(photos):
        if progress_callback:
            progress_callback(processed_photos[0], total_photos, "Sending WhatsApp Messages")
            
        watermarked_photo = add_watermark(photo, watermark_image, watermark_position, watermark_opacity, watermark_scale)

        if watermarked_photo and watermarked_photo not in sent_images:
            print(f"📤 Sending {watermarked_photo} to {whatsapp_number} (PyAutoGUI)...")
            
            # Send the text message as a caption on the first image only
            caption = message if i == 0 else ""
            
            try:
                # tab_close=True ensures it cleans up after itself without manual pyautogui hotkeys
                pywhatkit.sendwhats_image(
                    receiver=f"+91{whatsapp_number}",
                    img_path=watermarked_photo,
                    caption=caption,
                    wait_time=25,
                    tab_close=True,
                    close_time=5
                )
                sent_images.add(watermarked_photo)
                print(f"✅ PyAutoGUI: Successfully sent to {whatsapp_number}")
            except Exception as e:
                print(f"❌ PyAutoGUI failed for {whatsapp_number}: {e}")
                
        processed_photos[0] += 1

def _send_via_selenium(guest_name, whatsapp_number, photos, watermark_image, watermark_position, watermark_opacity, watermark_scale, message, sent_images, progress_callback, processed_photos, total_photos):
    """
    Selenium/Playwright implementation for robust WhatsApp delivery.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import urllib.parse
    except ImportError:
        print("❌ Selenium or webdriver-manager is not installed. Please run: pip install selenium webdriver-manager")
        return

    print(f"🌐 Initializing Selenium for {whatsapp_number}...")
    
    # Setup Chrome profile to persist WhatsApp login
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selenium_profile")
    options.add_argument(f"user-data-dir={user_data_dir}")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"❌ Failed to initialize Chrome driver: {e}")
        return

    try:
        for i, photo in enumerate(photos):
            if progress_callback:
                progress_callback(processed_photos[0], total_photos, "Sending WhatsApp Messages")
                
            watermarked_photo = add_watermark(photo, watermark_image, watermark_position, watermark_opacity, watermark_scale)

            if watermarked_photo and watermarked_photo not in sent_images:
                print(f"📤 Sending {watermarked_photo} to {whatsapp_number} (Selenium)...")
                
                caption = message if i == 0 else ""
                encoded_caption = urllib.parse.quote(caption)
                
                # Open WhatsApp Web chat
                url = f"https://web.whatsapp.com/send?phone=91{whatsapp_number}&text={encoded_caption}"
                driver.get(url)
                
                # Wait for chat to load (wait for attachment clip icon)
                wait = WebDriverWait(driver, 60)
                try:
                    attach_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]')))
                    time.sleep(2)  # Give it a moment to fully render
                    attach_btn.click()
                    
                    # Wait for image input
                    img_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')))
                    
                    # Upload image
                    img_input.send_keys(os.path.abspath(watermarked_photo))
                    
                    # Wait for send button and click
                    send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Send"]')))
                    time.sleep(1) # Small delay to ensure caption is loaded in the input field
                    send_btn.click()
                    
                    # Wait a bit for the message to actually send before navigating away
                    time.sleep(5)
                    
                    sent_images.add(watermarked_photo)
                    print(f"✅ Selenium: Successfully sent to {whatsapp_number}")
                except Exception as inner_e:
                    print(f"❌ Failed to interact with WhatsApp Web for {whatsapp_number}: {inner_e}")
                    print("You may need to scan the QR code if this is your first time using Selenium.")
                    time.sleep(15) # Give user time to scan if they need to
            
            processed_photos[0] += 1
    finally:
        driver.quit()

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

def add_watermark(image_path, watermark_path, position, opacity=1.0, scale=0.2):
    """
    Adds a watermark to the image with configurable opacity and scale.
    """
    try:
        if not os.path.exists(image_path) or not os.path.exists(watermark_path):
            return None

        image_path = resize_image(image_path)
        img = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA")

        # Apply opacity
        if opacity < 1.0:
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: p * opacity)
            watermark.putalpha(alpha)

        # Scale watermark
        wm_width = int(img.width * scale)
        wm_height = int((watermark.height / watermark.width) * wm_width)
        watermark = watermark.resize((wm_width, wm_height), Image.LANCZOS)

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
