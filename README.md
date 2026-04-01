[README.md](https://github.com/user-attachments/files/26398159/README.md)
 Media Tool v2.1  
**Video/Audio Cutter + Image Inserter (CLI Tool)**

A powerful command-line media processing tool built with Python and FFmpeg.  
This tool allows you to:

 Cut video/audio segments  
 Remove portions from media files  
Insert images into videos with customization  

---

Features

### 1. Video / Audio Cutting
- Cut specific segments from media files
- Automatically creates:
  - Backup of original file
  - Extracted cut segment
  - Remaining media after removal

### 2. Image Insert in Video
- Overlay images on videos
- Customize:
  - Position (top-left, center, etc.)
  - Opacity (transparency)
  - Size (percentage of video width)
  - Duration and timing

---

## 📁 Supported Formats

### Video
- .mp4, .avi, .mov, .mkv, .flv, .wmv

### Audio
- .mp3, .wav, .flac, .m4a

### Image
- .png, .jpg, .jpeg, .bmp, .gif, .webp

---

## ⚙️ Requirements

- Python 3.x
- FFmpeg & FFprobe (MANDATORY)

Download FFmpeg: https://ffmpeg.org/download.html

---

## 🛠️ Installation

```bash
git clone <your-repo-link>
cd media-tool
pip install -r requirements.txt
```

Make sure ffmpeg is added to your system PATH.

---

## ▶️ Usage

```bash
python main.py
```

---

## 📋 Main Menu

1. Video / Audio CUT karna hai  
2. Video mein IMAGE insert karni hai  
3. Exit  

---

## ✂️ Cutting Workflow

1. Select media file  
2. Enter start time and duration  
3. Tool generates:
   - backup_filename.ext  
   - filename_cut_starttoend.ext  
   - filename_remaining.ext  

---

## 🖼️ Image Insert Workflow

1. Select video file  
2. Select image file  
3. Configure:
   - Start time  
   - Duration  
   - Position  
   - Opacity  
   - Size  
4. Output:
   video_with_image.ext  

---

## 🧠 Internal Working

- Uses ffmpeg for cutting, concatenation, and overlay
- Uses ffprobe for duration and resolution detection

---

## ⚠️ Error Handling

- Checks if FFmpeg is installed  
- Validates file existence and input ranges  
- Auto-cleans temporary files  

---

## 📌 Notes

- Works in current directory only  
- Always creates backup before modifying original file  
- Fast processing using stream copy  

---

## 👨‍💻 Author

Made with ❤️ for learning and practical usage  

---

## 📜 License

Open-source and free to use
