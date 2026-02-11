# 💍 Wedding Elite V2.0 - Full Stack Application

## 📂 מבנה הפרויקט

```
wedding-elite-v2/
├── backend/
│   ├── main.py              # FastAPI server with full CRUD
│   └── requirements.txt      # Python dependencies
├── frontend/
│   └── index.html           # Single-page app with dynamic editing
└── README.md                # This file
```

## 🚀 התקנה והרצה

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server will run on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend (HTML)

```bash
cd frontend

# Option 1: Open directly in browser
open index.html

# Option 2: Use Python server
python -m http.server 3000
# Then open: http://localhost:3000/index.html
```

## 🔧 קונפיגורציה

### עדכן כתובת API בפרונטאנד

בקובץ `frontend/index.html`, שנה:

```javascript
const API_URL = "http://localhost:8000";  // למקומי
// או
const API_URL = "https://your-api.onrender.com";  // לייצור
```

## 📋 API Endpoints

### Weddings
```
POST   /weddings                    # Create wedding
GET    /weddings/{id}               # Get wedding
PUT    /weddings/{id}               # Update wedding (EDITABLE)
DELETE /weddings/{id}               # Delete wedding
GET    /weddings/{id}/dashboard     # Dashboard data
```

### Budget
```
GET    /weddings/{id}/budget        # Get categories
POST   /weddings/{id}/budget        # Add category
PUT    /budget/{cat_id}             # Update category (EDITABLE)
DELETE /budget/{cat_id}             # Delete category
```

### Vendor Bookings
```
GET    /weddings/{id}/bookings      # Get bookings
POST   /weddings/{id}/bookings      # Add booking
PUT    /bookings/{id}               # Update booking (EDITABLE)
DELETE /bookings/{id}               # Delete booking
```

### Tasks
```
GET    /weddings/{id}/tasks         # Get tasks
POST   /weddings/{id}/tasks         # Add task
PUT    /tasks/{id}                  # Update task (EDITABLE)
PATCH  /tasks/{id}/complete         # Toggle completion
DELETE /tasks/{id}                  # Delete task
```

### Vendors Marketplace
```
GET    /vendors                     # Search vendors
GET    /vendors/{id}                # Vendor profile
POST   /vendors                     # Create vendor profile
```

## ✨ פיצ'רים עיקריים

### ✅ V2.0 Features (Implemented)

**1. Full CRUD Operations**
- ✅ Create, Read, Update, Delete for all entities
- ✅ Edit-in-place UI
- ✅ Inline editing with modals
- ✅ Real-time feedback

**2. Dynamic Editing**
- ✅ Edit wedding names (inline)
- ✅ Edit wedding date (modal)
- ✅ Edit total budget (modal)
- ✅ Edit categories (inline)
- ✅ Add/Edit/Delete vendors
- ✅ Add/Edit/Delete tasks

**3. Vendor Management**
- ✅ Vendor bookings (couple's vendors)
- ✅ Vendor marketplace (searchable)
- ✅ Category-based organization

**4. Smart Features**
- ✅ Auto-generated default tasks
- ✅ Auto-generated budget categories
- ✅ Countdown timer
- ✅ Control percentage meter
- ✅ Budget tracking with alerts

**5. Multi-Tab Interface**
- ✅ Home (Dashboard)
- ✅ Budget (with editing)
- ✅ Suppliers (marketplace)
- ✅ Tasks (with CRUD)
- ✅ Profile (settings)

**6. Mobile-First Design**
- ✅ Bottom navigation
- ✅ One-handed usability
- ✅ Touch-friendly interactions
- ✅ Responsive cards

## 🎨 Design System

### Colors
```
Primary:    #6366F1 (Indigo)
Secondary:  #8B5CF6 (Purple)
Success:    #10B981 (Green)
Warning:    #F97316 (Orange)
Danger:     #EF4444 (Red)
```

### Typography
```
Font Family: Assistant (Hebrew)
Heading:     800 weight
Body:        400 weight
Bold:        700 weight
```

## 📊 Database Schema

הקובץ מכיל 9 טבלאות:
- `users` - משתמשים
- `weddings` - חתונות
- `budget_categories` - קטגוריות תקציב
- `vendors` - ספקים (marketplace)
- `vendor_bookings` - הזמנות ספקים
- `tasks` - משימות
- `reviews` - ביקורות
- `shared_access` - גישה משותפת
- `notifications` - התראות

## 🔐 Authentication (TODO)

כרגע האפליקציה עובדת ללא authentication למטרות demo.
לייצור, יש להוסיף:
- JWT tokens
- User registration
- Login/Logout
- Password hashing

## 🚀 Deploy to Production

### Backend (Render/Railway)

1. צור Git repository
2. העלה את תיקיית `backend/`
3. הגדרות ב-Render:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)

1. העלה את `frontend/index.html`
2. עדכן את `API_URL` לכתובת הייצור
3. Deploy!

## 📈 Future Enhancements (Phase 2)

- [ ] Real-time sync with WebSocket
- [ ] AI Budget Assistant
- [ ] Smart Task Generator
- [ ] Push Notifications
- [ ] Couple Sync feature
- [ ] Parent Mode
- [ ] Vendor Portal
- [ ] Payment tracking
- [ ] Document upload
- [ ] PDF export

## 🐛 Known Issues

- [ ] WebSocket implementation needs testing
- [ ] No authentication yet
- [ ] No file upload yet
- [ ] No email notifications yet

## 📝 Notes

- SQLite database (`wedding_elite_v2.db`) created automatically
- All data persists between restarts
- Frontend works standalone with mock data
- Connect to API for full functionality

## 💡 Tips

**For Development:**
```bash
# Backend
cd backend && python main.py

# Frontend (separate terminal)
cd frontend && python -m http.server 3000
```

**For Testing API:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🆘 Support

עזרה נוספת:
- קרא את `wedding_elite_v2_upgrade.md` למפרט מלא
- בדוק את Swagger docs ב-`/docs`
- כל ה-endpoints מתועדים שם

---

**Built with 💜 for couples planning their perfect wedding**

Version: 2.0.0
