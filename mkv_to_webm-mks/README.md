# MKV Tools 🛠️

A personal script I wrote to automate common tasks with `.mkv` video files using `ffmpeg` and `mkvpropedit`.  
It batch‑processes all `.mkv` files in the current directory and performs the following:

- 🧹 Remove embedded titles from MKV files  
- 🎬 Convert MKV → WebM (video + audio streams, audio re‑encoded to Opus)  
- 📑 Extract subtitles into a separate `.mks` file  
- 🖼️ Generate thumbnails (WebP images at 1280×720, taken at 30s mark, saved in `.thumbnails/`)  
- 🗑️ Clean up: deletes the original `.mkv` files and finally deletes itself  

---

## ⚙️ Requirements

- [FFmpeg](https://ffmpeg.org/) installed and available in your system’s PATH  
- [MKVToolNix](https://mkvtoolnix.download/) (for `mkvpropedit`)  
- Python 3.7+  

---

## 🚀 Usage

1. Place the script in a folder containing your `.mkv` files.  
2. Run it with:

   ```bash
   python mkv_tools.py
   ```

3. The script will:
   - Process all `.mkv` files in the folder  
   - Output `.webm`, `.mks`, and `.webp` thumbnail files  
   - Remove the original `.mkv` files  
   - Delete itself after completion  

---

## 📂 Output Structure

```
.
├── video1.webm
├── video1.mks
├── .thumbnails/
│   ├── video1.webp
│   └── video2.webp
└── ...
```

---

## ⚠️ Notes

- This script is destructive: it **removes the original MKV files** and deletes itself after running.  
- **No CLI interface**: to change behavior, **edit the file directly**.  
  - Comment out the lines/functions you don’t want to run.  
  - Modify the commands parameters inside the functions to customize output.    

 