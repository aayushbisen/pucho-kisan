<p align="center"> 
    <img src="forum/static/forum/images/icons/icon-144x144.png" >
</p>

# 🌾 Pucho Kisaan

A community-driven forum for farmers to ask questions and get expert guidance on real-world farming problems.

🔗 **[Visit Pucho Kisan ↗](https://pucho-kisan.onrender.com)**

---

## 👀 Preview

<p align="center">
    <img src="preview/1.png" width="300px">
</p>

<br/>

---

<br/>

<p align="center">
    <img src="preview/3.png" width="300px">
</p>

<br/>

---

<br/>

<p align="center">
    <img src="preview/4.png" width="300px">
</p>

---

## 🔐 Test Credentials

The application comes with **pre-populated dummy data** for testing and exploration.

### 👨‍🌾 Test Farmers

| Name             | Phone Number | Password  |
| ---------------- | ------------ | --------- |
| John Farmer      | 0000000000   | hello1234 |
| Alice Greenfield | 0000000001   | hello1234 |
| Bob Harvest      | 0000000002   | hello1234 |
| Carol Meadows    | 0000000003   | hello1234 |
| Dave Cropwell    | 0000000004   | hello1234 |

### 🧑‍🔬 Test Specialists

| Name                 | Phone Number | Subject         |
| -------------------- | ------------ | --------------- |
| Dr. Emma Soilwise    | 1111111111   | Soil Science    |
| Dr. Frank Pestman    | 1111111112   | Pest Control    |
| Dr. Grace Vetcare    | 1111111113   | Animal Health   |
| Prof. Henry Seedling | 1111111114   | Crop Management |
| Dr. Iris Waterwise   | 1111111115   | Irrigation      |

### 📊 Included Dummy Data

* 👨‍🌾 5 test farmers with real questions
* ❓ 10 sample questions across categories:

  * Pests
  * Crops
  * Animals
  * Purchase
* 💡 14 helpful community answers
* ⬆️ Upvotes and user interactions

---

## ✨ Features

* 🌾 Ask farming-related questions
* 💬 Community-driven answers
* ⬆️ Upvote helpful questions and answers
* 📱 Progressive Web App (PWA) support
* 🌍 Multi-language support
* 👥 Connect with nearby farmers
* 📸 Attach images and videos to questions
* 🧑‍🌾 Expert specialists directory

---

## 🛠️ Technology Stack

* **Backend:** Django 6.0.1
* **Frontend:** Materialize CSS
* **Database:** SQLite
* **PWA:** Service Workers, Web Manifest

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/pucho-kisan.git
cd pucho-kisan
```

### 2️⃣ Create & activate a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run migrations

```bash
python manage.py migrate
```

### 5️⃣ Load dummy data (optional)

```bash
# Dummy data is automatically loaded via migration
# To remove: python manage.py migrate forum 0021
```

### 6️⃣ Start the development server

```bash
python manage.py runserver
```

### 7️⃣ Open the app

Visit 👉 `http://localhost:8000`
Log in using any test credentials listed above.

---

## 📄 License

This project is open source and available under the **[MIT License](LICENSE)**.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the **[issues page](https://github.com/yourusername/pucho-kisan/issues)**.

---

### ❤️ Made with love, for farmers
