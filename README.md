# 📸 AuraSnap

![React](https://img.shields.io/badge/React-v18-blue?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100-green?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![PyTorch](https://img.shields.io/badge/PyTorch-GPU%20Supported-red?logo=pytorch)
![TensorFlow](https://img.shields.io/badge/TensorFlow-GPU%20Supported-orange?logo=tensorflow)
![CUDA](https://img.shields.io/badge/CUDA-Enabled-brightgreen?logo=nvidia)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue)
![Status](https://img.shields.io/badge/Project-Academic-success)

---

## 📖 Overview

**AuraSnap** is a high-performance, AI-powered face recognition system designed for event photography. It automates the complex workflow of **face detection, intelligent sorting, dynamic watermarking, and automated WhatsApp delivery**. 

Introduces a state-of-the-art **Liquid Glass** interface built on a **React + Python Sidecar** architecture, offering a premium, fluid experience for professional studios.

---

## ✨ Key Features

- 🧪 **Advanced Face Recognition**
  - Uses **InsightFace (ArcFace)** and **HDBSCAN** for highly accurate face clustering.
  - Automatically identifies guests across thousands of photos.
  
- 💎 **Liquid Glass UI**
  - Stunning modern aesthetic with glassmorphism, blur effects, and fluid animations.
  - Interactive "Magic" dashboard with real-time SSE progress streaming.
  - Fully responsive Light/Dark modes.

- 🗂️ **Modular Automation**
  - Selective execution: Choose to Train, Sort, or Send individually or all at once.
  - Smart Retraining: Skips training if a model already exists for an event.

- 🖼️ **Real-Time Watermarking**
  - Live preview with a checkerboard background for transparency visibility.
  - Full control over opacity, scale, and 9-grid positioning.

- 📤 **Automated WhatsApp Delivery**
  - Robust delivery via Selenium or PyAutoGUI fallback.
  - Intelligent deduplication to ensure guests never receive the same photo twice.

---

## 🧠 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React v18, Framer Motion, TailwindCSS, Vite |
| **Backend API** | FastAPI, Uvicorn, Python 3.10+ |
| **AI/ML** | InsightFace, HDBSCAN, OpenCV, NumPy |
| **Automation** | Selenium, PyAutoGUI, PyWhatKit |
| **Image Processing** | Pillow (PIL) |
| **Optimization** | Nvidia Omniverse |

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

## 🧪 Performance Highlights

- ✅ >95% recognition accuracy for trained faces
- 📁 Handles 1000+ images per batch
- 👥 Supports multi-face group photos
- ⚡ Significantly faster with GPU acceleration

---

## ⚠️ Known Limitations

- Requires high-quality training images
- WhatsApp delivery depends on WhatsApp Web session
- Duplicate image detection currently handles duplicate paths, but content-based pHash optimization is planned

---

## ⚠️ Requirements
- **OS**: Windows 10/11
- **Hardware**: 8GB RAM minimum (NVIDIA GPU recommended for faster face recognition)
- **Browser**: Chrome/Edge (for WhatsApp Selenium integration)

---

## 👨‍💻 Core Team

- **[Pinak Meher](https://github.com/Pinuk14)** 🔗
- **[Parth Mhatre](https://github.com/parth-mhatre24)** 🔗
- **[Niharika Raut](https://github.com/NiharikaRaut-02)** 🔗
- **[Seon D’silva](https://github.com/Seon-open-sourceylon)** 🔗

### ✨ Honarable Mentions
- **[Nash Tuscano](https://github.com/23Nash)**
- **[Maric Brass](https://github.com/Maricbrass)**
- **[Rishi Vartak](https://github.com/RishiVartak6)**

---

## 🏫 Academic Info
- **Institution**: Vidyavardhini’s College of Engineering & Technology
- **Department**: Computer Engineering
- **Academic Year**: 2024–25
