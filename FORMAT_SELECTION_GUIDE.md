# 🎵 Format Selection System - User Guide

## 🚀 **YANGI XUSUSIYAT: FORMAT TANLASH**

Endi bot YouTube URL yuborish-dan keyin format tanlash imkoniyatini beradi!

## 🎯 **Qanday ishlaydi:**

### **1. URL Yuboring:**
```
https://www.youtube.com/watch?v=example
```

### **2. Format Menyusi Ko'rinadi:**
```
🎵 Video Title
👤 Channel Name
⏱ 45:30 | 👀 1,234,567  
📊 ~500.0 MB

Format tanlang:

🎵 MP3 Audio     🎶 M4A Audio
📹 MP4 720p      📺 MP4 480p
      🎧 Best Audio Quality
```

### **3. Format Tanlang va Yuklab Oling!**

## 📋 **FORMAT VARIANTLARI:**

### **🎵 MP3 Audio (192kbps)**
- **Format:** MP3
- **Quality:** 192kbps
- **Size:** O'rtacha (best compression)
- **Use case:** Universal compatibility, music players
- **Processing:** FFmpeg conversion

### **🎶 M4A Audio**  
- **Format:** M4A/AAC
- **Quality:** Original (no conversion)
- **Size:** Kichik
- **Use case:** iPhone, iTunes, high quality
- **Processing:** Direct download

### **🎧 Best Audio Quality**
- **Format:** Auto (M4A/WebM/etc)
- **Quality:** Eng yuqori mavjud
- **Size:** Katta
- **Use case:** Audiophiles, professional use
- **Processing:** Minimal processing

### **📹 MP4 Video (720p)**
- **Format:** MP4 video
- **Quality:** 1280x720 (HD)
- **Size:** Katta
- **Use case:** HD video viewing
- **Processing:** Direct download

### **📺 MP4 Video (480p)**
- **Format:** MP4 video  
- **Quality:** 854x480 (SD)
- **Size:** O'rtacha
- **Use case:** Mobile devices, data saving
- **Processing:** Direct download

## ⚡ **DOWNLOAD PROCESS:**

### **Format Tanlash:**
1. URL yuboring
2. Format tugmasini bosing
3. Progress ko'ring: `⏳ 🎵 MP3 Audio yuklab olinmoqda... 75%`

### **Kichik Fayllar (<50MB):**
```
📊 Tayyor: 25.3 MB
📤 Yuborilmoqda...
✅ 🎵 MP3 Audio yuborildi!
```

### **Katta Fayllar (>50MB):**
```
📊 Tayyor: 234.5 MB
⚙️ Qismlar tayyorlanmoqda...

🎵 Long Video Title
📁 Format: 🎵 MP3 Audio
📊 Jami hajmi: 234.5 MB
⏱ Jami davomiyligi: 2:30:00
📦 6 qismga bo'lindi

Qaysi qismni tanlaysiz?
📀 1-qism | 45.0 MB | ⏱ 0:00-25:00
📀 2-qism | 45.0 MB | ⏱ 25:00-50:00
...
📦 Barcha qismlar
```

## 🎯 **FORMAT SELECTION TIPS:**

### **🎵 Music uchun:**
- **MP3** - Universal, har qanday device
- **M4A** - High quality, kichik size

### **📹 Video uchun:**
- **720p** - HD quality, katta screen
- **480p** - Mobile devices, tez download

### **🎧 Professional uchun:**
- **Best Audio** - Eng yuqori sifat
- **M4A** - Lossless quality

### **💾 Data Saving uchun:**
- **MP3** - Eng kichik size
- **480p Video** - Video uchun kichik

## 🔧 **TECHNICAL DETAILS:**

### **Audio Processing:**
- **MP3:** FFmpeg conversion with 192kbps
- **M4A:** Direct download, no conversion
- **Best:** Highest available format

### **Video Processing:**
- **720p/480p:** Direct download with quality filter
- Smart format selection based on availability

### **File Handling:**
- Audio files → `send_audio()` with metadata
- Video files → `send_video()` with preview
- Format info in caption

## 📊 **COMPARISON TABLE:**

| Format | Quality | Size | Speed | Compatibility |
|--------|---------|------|-------|--------------|
| MP3 | Good | Small | Fast | Universal |
| M4A | High | Small | Fastest | iOS/Modern |
| Best Audio | Highest | Large | Medium | Variable |
| 720p Video | HD | Large | Slow | Universal |
| 480p Video | SD | Medium | Medium | Universal |

## ✅ **ADVANTAGES:**

- 🎯 **User choice** - Pick exactly what you need
- 📱 **Device optimization** - Best format for your device  
- 💾 **Size control** - Choose size vs quality
- ⚡ **Speed options** - Fast download vs high quality
- 🔧 **Professional options** - Best quality available

---

## 🚀 **GET STARTED:**

1. **Railway'da deploy** tugaguncha kutib turing (5-10 daqiqa)
2. **Bot'ga YouTube URL** yuboring
3. **Format tanlang** - misol uchun MP3
4. **Natijani kuzating** - format bilan birga yuboriladi

**Professional format selection system endi faol!** 🎵📹

**Test qilib ko'ring va qaysi formatlar yaxshi ishlayotganini menga aytib qo'ying!** 🎯