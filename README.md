# 📸 AuraSnap

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![PyTorch](https://img.shields.io/badge/PyTorch-GPU%20Supported-red?logo=pytorch)
![TensorFlow](https://img.shields.io/badge/TensorFlow-GPU%20Supported-orange?logo=tensorflow)
![CUDA](https://img.shields.io/badge/CUDA-Enabled-brightgreen?logo=nvidia)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-purple)
![Status](https://img.shields.io/badge/Project-Academic-success)

---

## 📖 Overview

**AuraSnap** is an AI-powered, face recognition–based photo management system built for **event photography studios**. It automates the entire post-event workflow—**face detection, photo sorting, watermarking, and WhatsApp delivery**—reducing manual effort and turnaround time.

---

## 🚀 Key Features

- 🔍 **Automatic Face Recognition**
  - Identifies individuals in bulk event photos
  - Uses deep learning–based face embeddings (ArcFace / FaceNet)

- 🗂️ **Smart Photo Sorting**
  - Automatically organizes images into person-specific lists
  - Supports group photos (same image sorted into multiple lists)

- 🖼️ **Dynamic Watermarking**
  - Adds customizable watermarks (studio name, event name, guest name)
  - Ensures branding without blocking faces

- 📤 **Automated WhatsApp Delivery**
  - Sends photos directly to guests via WhatsApp using PyWhatKit
  - Contact numbers are linked during dataset training

- 🖥️ **User-Friendly Desktop GUI**
  - Built using **CustomTkinter**
  - Supports Dark & Light themes
  - Designed for non-technical users

- 📷 **Real-Time Face Recognition (Optional)**
  - Webcam-based recognition
  - Displays known guest details instantly

- 🌐 **Offline First**
  - Fully functional offline (except WhatsApp delivery)
  - Suitable for on-site event usage

---

## 🧠 Tech Stack

| Category | Technologies |
|--------|-------------|
| Language | Python 3.8+ |
| GUI | CustomTkinter |
| Computer Vision | OpenCV |
| Deep Learning | TensorFlow / PyTorch |
| Face Recognition | ArcFace / FaceNet |
| Image Processing | PIL (Pillow) |
| Automation | PyWhatKit |
| Optimization | Nvidia Omniverse |

---

## ⚙️ GPU & Deep Learning Setup (Important)

AuraSnap **can run on CPU**, but **GPU acceleration is highly recommended** for best performance.

### ✅ Recommended (Optional but Best)
- GPU-enabled **PyTorch**
- GPU-enabled **TensorFlow**
- NVIDIA GPU with **CUDA support**

GPU acceleration significantly improves:
- Face embedding generation
- Batch image processing
- Real-time webcam recognition
- Model training & fine-tuning

> ⚠️ Without GPU versions, the system will still work, but processing may be slower for large datasets.

---

## 🏗️ System Architecture (High Level)

1. Input event images  
2. Face detection using OpenCV  
3. Face embedding using deep learning models  
4. Face matching via cosine similarity  
5. Photo sorting into JSON-based lists  
6. Watermarking using PIL  
7. WhatsApp delivery using PyWhatKit  

---

## 🖥️ System Requirements

### Hardware
- Intel i5 (12th Gen) or higher  
- 8 GB RAM (16 GB recommended)  
- NVIDIA GPU (RTX 3060 or higher recommended)  
- 500 MB free storage  

### Software
- Windows 11  
- Python 3.8+  
- WhatsApp Web (logged in)

---

## 🧪 Performance Highlights

- ✅ >95% recognition accuracy for trained faces
- 📁 Handles 1000+ images per batch
- 👥 Supports multi-face group photos
- ⚡ Significantly faster with GPU acceleration

---

## ⚠️ Known Limitations

- Requires high-quality training images
- WhatsApp delivery depends on WhatsApp Web session
- Duplicate image detection requires further optimization

---

## 🔮 Future Enhancements

- ☁️ Cloud storage integration
- 📱 Mobile application version
- 🔁 Continuous face re-training across events
- 🌍 Multi-language UI support
- 🎨 Advanced watermark templates
- 📊 Self-learning guest face database

---

## 👨‍💻 Core Team Contributions

- **[Pinak Meher](https://github.com/Pinuk14)** 🔗
- **[Parth Mhatre](https://github.com/parth-mhatre24)** 🔗
- **[Niharika Raut](https://github.com/NiharikaRaut-02)** 🔗
- **[Seon D’silva](https://github.com/Seon-open-sourceylon)** 🔗

## ✨ Honorable Mention

- **[Maric Brass](https://github.com/Maricbrass)** 🔗
- **[Nash Tuscano](https://github.com/23Nash)** 🔗
- **[Rishi Vartak](https://github.com/RishiVartak6)** 🔗

---

## 🏫 Academic Info

- **Institution:** Vidyavardhini’s College of Engineering & Technology  
- **Department:** Computer Engineering  
- **Semester:** Semester IV  
- **Academic Year:** 2024–25  
