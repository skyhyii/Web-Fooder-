# 🍽️ FooDer - Smart Food Recommendation System

## 🚀 About FooDer

**Bingung mau makan apa hari ini? Kami punya solusinya! 👋**

**FooDer** adalah sistem rekomendasi makanan personal yang membantu pengguna menemukan makanan dan restoran terbaik sesuai preferensi mereka.

Aplikasi ini lahir dari permasalahan sederhana namun sering dialami banyak orang: **terlalu banyak pilihan makanan membuat pengguna kesulitan menentukan apa yang ingin dimakan**. Sistem pencarian biasa hanya menampilkan daftar makanan, sedangkan FooDer berusaha memahami selera unik setiap pengguna.

Dengan menggabungkan **Recommendation System**, **Location-Based Search**, **Sentiment Analysis**, dan **AI Chatbot**, FooDer menghadirkan pengalaman mencari makanan yang lebih cepat, personal, dan relevan.

---

## ✨ Key Features

### 👤 User Authentication

* Registrasi akun
* Login & Logout
* Manajemen profil pengguna

### ❤️ Swipe-Based Food Discovery

* Swipe kanan untuk Like
* Swipe kiri untuk Dislike
* Pengalaman seperti aplikasi Tinder
* Sistem mempelajari preferensi pengguna dari aktivitas swipe

### 🎯 Personalized Food Recommendation

* Menggunakan metode **TF-IDF (Term Frequency - Inverse Document Frequency)**
* Membentuk profil preferensi berdasarkan makanan yang disukai pengguna
* Merekomendasikan makanan yang paling relevan dengan selera pengguna

### 🔍 Food Search

* Mencari makanan secara langsung melalui menu pencarian
* Mendukung eksplorasi makanan di luar hasil rekomendasi

### 🤝 Food Matching System

* Menghitung tingkat kecocokan antara preferensi pengguna dan makanan
* Menampilkan makanan yang berhasil menjadi **Match**

### 📍 Real-Time Nearby Restaurant Recommendation

* Scraping Google Maps secara real-time
* Menemukan restoran terdekat berdasarkan makanan yang berhasil di-match
* Menampilkan informasi restoran yang relevan

### 😊 Restaurant Sentiment Analysis

* Mengambil ulasan restoran dari Google Maps
* Melakukan analisis sentimen terhadap review pelanggan
* Membantu pengguna memilih restoran dengan kualitas terbaik

### 🤖 AI Food Assistant

* Chatbot AI interaktif
* Menjawab pertanyaan seputar:

  * Makanan
  * Restoran
  * Rekomendasi kuliner
  * Informasi terkait makanan lainnya

### 📊 User Statistics Dashboard

* Jumlah swipe
* Jumlah like
* Jumlah match

### 📚 Favorite Foods

* Menyimpan daftar makanan yang telah di-like
* Memudahkan pengguna melihat kembali makanan favorit mereka

---

## 🧠 How It Works

### 1️⃣ User Preference Collection

Pengguna mengisi preferensi makanan dan melakukan swipe terhadap berbagai makanan yang ditampilkan.

⬇️

### 2️⃣ TF-IDF Weight Calculation

Sistem menghitung bobot TF-IDF dari makanan yang disukai pengguna untuk membentuk representasi preferensi.

⬇️

### 3️⃣ Food Recommendation

Sistem mencari makanan dengan karakteristik yang paling mirip dengan preferensi pengguna.

⬇️

### 4️⃣ Food Matching

Dilakukan perhitungan tingkat kecocokan sehingga diperoleh makanan yang berhasil menjadi **Match**.

⬇️

### 5️⃣ Restaurant Discovery

Sistem melakukan scraping Google Maps secara real-time untuk menemukan restoran terdekat yang menyediakan makanan hasil match.

⬇️

### 6️⃣ Sentiment Analysis

Review restoran dianalisis untuk mengetahui sentimen pelanggan dan kualitas restoran.

⬇️

### 7️⃣ Recommendation Result

Pengguna memperoleh rekomendasi makanan dan restoran yang sesuai dengan preferensinya.

---

## 🏗️ System Architecture

```text
User
 │
 ▼
Food Preference Input
 │
 ▼
Swipe Like / Dislike
 │
 ▼
TF-IDF Recommendation Engine
 │
 ▼
Food Matching System
 │
 ▼
Google Maps Scraper
 │
 ▼
Restaurant Review Collection
 │
 ▼
Sentiment Analysis Engine
 │
 ▼
Restaurant Recommendation
 │
 ▼
User Interface
```

---

## 🛠️ Technologies Used

### Backend

* Python
* FastAPI
* Pandas
* NumPy
* Scikit-Learn
* Selenium

### Recommendation System

* TF-IDF Vectorization
* Cosine Similarity
* Content-Based Filtering

### AI & NLP

* Sentiment Analysis
* Natural Language Processing
* AI Chatbot

### Data Source

* Google Maps Reviews
* Food Dataset

### Frontend

* HTML
* CSS
* JavaScript

### Database

* PostgreSQL

---

## 🎯 Advantages of FooDer

✅ Personalisasi berdasarkan selera pengguna

✅ Interaksi swipe yang intuitif

✅ Rekomendasi makanan yang relevan

✅ Restoran dicari secara real-time

✅ Analisis sentimen otomatis

✅ AI Chatbot untuk konsultasi makanan

✅ Dashboard statistik pengguna

---

## 📸 Main Features Preview

### ❤️ Food Swipe Interface

Swipe makanan seperti Tinder untuk membantu sistem memahami preferensi pengguna.

### 🎯 Personalized Recommendation

Dapatkan rekomendasi makanan yang sesuai dengan selera Anda.

### 📍 Nearby Restaurant Finder

Temukan restoran terdekat yang menyediakan makanan hasil rekomendasi.

### 😊 Sentiment Analysis

Lihat kualitas restoran berdasarkan analisis ulasan pelanggan.

### 🤖 AI Food Assistant

Tanyakan apa saja terkait makanan dan restoran kepada chatbot AI.

### 📊 User Analytics

Pantau riwayat aktivitas dan preferensi makanan Anda.

---

## 🌟 Impact

FooDer membantu pengguna:

🍔 Mengurangi kebingungan saat memilih makanan

⏱️ Menghemat waktu dalam mencari restoran

🎯 Mendapatkan rekomendasi yang lebih personal

📍 Menemukan restoran terdekat dengan cepat

⭐ Menghindari restoran dengan ulasan buruk

🤖 Mendapatkan bantuan AI dalam eksplorasi kuliner

---

## 👨‍💻 Team Project

🌟 Muhammad Zikra Al Rizkya Adler
🌟 Muhammad Zidan Alhamid
🌟 Muthia Rezi Aisyah
🌟 Nakita Raisya Gezkara

👨‍💻 S1 Data Science - Telkom University

Developed with ❤️ to make food discovery smarter, faster, and more personalized.

---

## 📄 License

This project is developed for educational and research purposes.
