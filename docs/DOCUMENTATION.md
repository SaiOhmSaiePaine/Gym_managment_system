# 📚 Lost & Found Campus - Complete Documentation

## 🚀 Quick Start Guide

### **Quick Setup & Run**
```bash
# 1. Clone and navigate to project
git clone <your-repo-url>
cd example-lost-found-proj

# 2. Run quick setup shell script
./setup.sh #for python version 3.12 and below

#or

./setup-enhanced.sh #for python version 3.13 and above
```

### **Manual Setup & Run**
```bash
# 1. Clone and navigate to project
git clone <your-repo-url>
cd example-lost-found-proj

# 2. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 3. Database setup (PostgreSQL required)
cp .env.example .env  # Configure your database settings
python3 database_config.py  # Initialize database

# 4. Frontend setup
cd ../frontend
npm install

# 5. Start the application
# Terminal 1 (Backend):
cd backend && source venv/bin/activate && python3 postgresql_server.py

# Terminal 2 (Frontend):
cd frontend && npm start
```

### **Access Points**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📊 **Admin Panel**: http://localhost:8000/admin (admin/admin123)

---

## 🗄️ Database Schema

### **Core Tables:**

#### **👥 USERS**
```sql
- id (UUID, Primary Key)
- name (VARCHAR, User full name)
- email (VARCHAR, Unique email address)
- password_hash (VARCHAR, Hashed password)
- role (VARCHAR, user/admin)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### **📱 ITEMS**
```sql
- id (UUID, Primary Key)
- title (VARCHAR, Item title/name)
- description (TEXT, Detailed description)
- category_id (INTEGER, Foreign Key → categories.id)
- status (VARCHAR, lost/found/returned/claimed)
- location_found (VARCHAR, Where item was found)
- date_found (DATE, Date when found)
- image_url (TEXT, Primary image URL)
- user_id (UUID, Foreign Key → users.id)
- contact_info (TEXT, Contact information)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### **🏷️ CATEGORIES**
```sql
- id (INTEGER, Primary Key)
- name (VARCHAR, Category name)
- description (TEXT, Category description)
- created_at (TIMESTAMP)
```

---

## 🔗 API Documentation

### **Base URL**: `http://localhost:8000`

### **Authentication**
All authenticated endpoints require a Bearer token:
```
Authorization: Bearer <your-jwt-token>
```

### **Key Endpoints**

#### **Authentication**
```http
POST /api/users/register
POST /api/users/login
```

#### **Items**
```http
GET    /api/items           # List all items
POST   /api/items           # Create new item
GET    /api/items/{id}      # Get specific item
PUT    /api/items/{id}      # Update item
DELETE /api/items/{id}      # Delete item
```

#### **Categories**
```http
GET /api/categories         # List all categories
```

#### **Admin**
```http
GET /admin                  # Admin panel
```

---

## 🚨 Troubleshooting

### **"localhost:3000 can't be reached"**
✅ **Solution**: Make sure both servers are running and wait for compilation to complete.

### **"AWS credentials not configured"**
✅ **Solution**: Configure AWS credentials in your `.env` file:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET_NAME=your_bucket_name
AWS_REGION=your_region
```

### **"Port already in use"**
✅ **Solution**: 
```bash
# Kill existing processes
pkill -f "python3 postgresql_server.py"
pkill -f "npm start"
# Wait 5 seconds, then restart
```

### **Database connection errors**
✅ **Solution**: Ensure PostgreSQL is running and `.env` file is configured correctly.

### **Dependencies errors**
✅ **Solution**:
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend  
cd frontend && npm install
```

---

## 🏗️ Project Structure

```
example-lost-found-proj/
├── backend/
│   ├── postgresql_server.py     # Main backend server
│   ├── database_config.py       # Database configuration
│   ├── s3_upload.py             # AWS S3 integration
│   ├── seed_database.py         # Database seeding utility
│   ├── sql_query.py             # SQL query utility
│   ├── requirements.txt         # Python dependencies
│   ├── lost_found_db.json       # JSON backup data
│   ├── user_db.json             # User backup data
│   └── uploads/                 # Local image storage
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── utils/               # Utility functions
│   │   └── types/               # TypeScript types
│   ├── package.json             # Node dependencies
│   └── build/                   # Production build
├── config/
│   ├── database.env.example     # Database config template
│   └── aws-credentials-template.txt
└── docs/
    └── DOCUMENTATION.md         # This file
```

---

## 🔧 Development

### **Environment Variables**
Create `.env` file in backend directory:
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lost_found_campus
DB_USER=your_username
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_secret_key

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET_NAME=your_bucket_name
AWS_REGION=your_region
```

### **Useful Commands**
```bash
# Run SQL queries
python3 sql_query.py "SELECT COUNT(*) FROM items;"

# Seed database with sample data
python3 seed_database.py

# Upload existing images to S3
python3 s3_upload.py
```

---

## 📝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** and test thoroughly
4. **Commit changes**: `git commit -m "Add your feature"`
5. **Push to branch**: `git push origin feature/your-feature`
6. **Create Pull Request**

### **Code Standards**
- Follow existing code style and naming conventions
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation when needed

---

## 🆘 Support

If you encounter issues:
1. Check this troubleshooting section
2. Verify all dependencies are installed
3. Ensure PostgreSQL and AWS are configured correctly
4. Check server logs for error messages
5. Create an issue on GitHub with detailed error information

---

*Last Updated: July 2025*
