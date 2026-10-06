# 🌾 FarmDirect - Direct Farmer-to-Consumer Platform

FarmDirect is a dedicated web platform developed to **eliminate middlemen and mediators** between farmers and consumers. It connects growers directly with buyers so farmers receive 100% of their rightful earnings while consumers purchase harvest-fresh produce without broker commissions.

---

## 🌟 Key Features

### 1. Dual Portals & Login Flows
- **👨‍🌾 Farmer Portal (`/farmer/login`)**:
  - Registration & Login capturing basic farm details: Name, Mobile / WhatsApp, Email, State, District, and Village/Farm location.
  - Farmer Dashboard:
    - Add & publish new crop listings with price per unit, available quantity, harvest date, and description.
    - Set custom honest prices without broker cuts.
    - Track active inventory and toggle "Sold Out" or "Available".
    - Direct Inquiries inbox: View buyer names, requested quantities, and direct call/WhatsApp buttons.
    - View local consumer demands to supply crops directly.

- **🛒 Consumer Portal (`/consumer/login`)**:
  - Registration & Login capturing delivery details: Name, Mobile / WhatsApp, Email, State, City/District, and Area/Locality.
  - Consumer Dashboard:
    - Browse crops grown by local farmers near their district.
    - Direct Connect: One-click Phone Call and WhatsApp Chat with pre-formatted crop inquiry messages.
    - Post crop demands ("What I need"): Specify crop name, quantity, target price, and delivery location.
    - Track direct inquiries sent to farmers.

### 2. Eliminating Middlemen: Transparent Pricing
- **Direct Price vs Retail Markup**: Every crop shows the farmer's direct price alongside traditional middleman/retail rates.
- **Interactive Savings Calculator**: Consumers can input quantity (e.g. 10 kg, 50 kg) to immediately calculate how much money they save and how much the farmer receives directly (0% commission).

### 3. Direct Contact Channels
- **One-Click Phone Call**: Directly connects the buyer to the farmer's mobile phone (`tel:...`).
- **Direct WhatsApp Chat**: Generates an encoded WhatsApp direct link (`https://wa.me/...`) specifying the exact crop name, quantity, and price.
- **In-App Inquiries**: Send messages with contact details that appear immediately on the farmer's dashboard.

---

## 🚀 How to Run

### Option 1: One-Click (Windows)
Double-click `run.bat` in the project directory:
```
C:\Users\bhara\.gemini\antigravity\scratch\farm_direct\run.bat
```

### Option 2: Command Line
Open PowerShell or Command Prompt in `C:\Users\bhara\.gemini\antigravity\scratch\farm_direct`:
```powershell
python app.py
```
Then visit **http://127.0.0.1:5000** in your browser.

---

## 🔑 Pre-seeded Demo Accounts

For immediate testing, sample accounts and realistic crop listings are pre-seeded in the database:

| Role | Email | Password | Location |
|---|---|---|---|
| **Farmer** | `ramesh@farmer.com` | `password123` | Borsad, Anand (Gujarat) |
| **Farmer** | `suresh@farmer.com` | `password123` | Khanna, Ludhiana (Punjab) |
| **Farmer** | `anitha@farmer.com` | `password123` | Srirangapatna, Mandya (Karnataka) |
| **Consumer** | `pooja@consumer.com` | `password123` | Bodakdev, Ahmedabad (Gujarat) |
| **Consumer** | `amit@consumer.com` | `password123` | Indiranagar, Bengaluru (Karnataka) |

*(You can also register brand new Farmer or Consumer accounts directly from the UI).*

---

## 📁 Project Structure

```
farm_direct/
├── app.py                     # Main Flask backend application & routing
├── database.py                # SQLite schema, initial seed data, and helper queries
├── farm_direct.db             # SQLite database (auto-generated)
├── run.bat                    # Windows one-click start script
├── README.md                  # Documentation
├── static/
│   ├── css/
│   │   └── style.css          # Responsive design, card layouts, agricultural palette
│   └── js/
│       └── main.js            # Auth tab toggle, savings calculator, WhatsApp helper
└── templates/
    ├── base.html              # Base template with role badges and navigation
    ├── index.html             # Landing page with mission, stats, and catalog
    ├── farmer_login.html      # Farmer login and registration
    ├── consumer_login.html    # Consumer login and registration
    ├── farmer_dashboard.html  # Farmer crop management and buyer inquiry inbox
    ├── consumer_dashboard.html# Consumer marketplace, nearby crops, and demand posting
    ├── marketplace.html       # Public crop search with category/location filters
    └── crop_detail.html       # Crop details with direct WhatsApp & phone contact
```
