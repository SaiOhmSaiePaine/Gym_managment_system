# 📚 Lost & Found Campus - Complete Documentation

## 🚀 Quick Start Guide

### **Quick Setup & Run**
```bash
# 1. Clone and navigate to project
git clone <your-repo-url>
cd example-lost-found-proj

# 2. Run setup script (one-click setup)
./setup.sh
```

**Note**: If you encounter Python version compatibility issues (Python 3.13+), use:
```bash
./setup-enhanced.sh  # Enhanced version with Python compatibility handling
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
- admin_notes (TEXT, Internal admin notes) ✨ NEW
- custody_status (VARCHAR, Item custody status)
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
Authorization: Bearer <jwt_token>
```

### **User Authentication**

#### **POST** `/api/users/register`
Register a new user account
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### **POST** `/api/users/login`
Login and receive JWT token
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### **GET** `/api/users/me`
Get current user profile (requires authentication)

### **Items Management**

#### **GET** `/api/items`
Get all items (excludes returned items from public view)
- Query parameters: `page`, `per_page`, `search`, `category`, `status`

#### **POST** `/api/items`
Create a new item (requires authentication)
```json
{
  "title": "Lost iPhone",
  "description": "Black iPhone 13 Pro",
  "category": "Electronics",
  "status": "lost",
  "location_found": "Library 2nd Floor",
  "contact_info": "john@example.com"
}
```

#### **GET** `/api/items/{id}`
Get specific item details

#### **PUT** `/api/items/{id}`
Update item (admin only - supports admin_notes field)

#### **DELETE** `/api/items/{id}`
Delete item (admin only)

### **Admin Endpoints**

#### **GET** `/api/admin/items`
Get all items including returned items (admin only)

#### **GET** `/api/admin/users`
Get all users with statistics (admin only)
```json
{
  "users": [
    {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "item_count": 5,
      "lost_count": 2,
      "found_count": 3,
      "returned_count": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_count": 25,
  "total_pages": 3
}
```

#### **DELETE** `/api/admin/users/{id}` ✨ NEW
Delete user and all their items (admin only)
- Permanently removes user and associated data
- Returns confirmation with deleted user details

---

## 🛡️ Admin Panel Features

### **Admin Dashboard** (`/admin`)
- 📊 **Overview Statistics**: Total users, items, categories
- 📈 **Analytics**: Item status distribution, user activity
- 🎯 **Quick Actions**: Recent items, user management

### **Item Management** (`/admin/items`)
- ✅ **View**: Complete item details with user information
- ✅ **Update**: Modify item status, add admin notes, update location info
- ✅ **Delete**: Permanently remove items from system
- ✅ **Admin Notes**: Add internal notes to items for tracking
- ✅ **Status Management**: Change item status (lost/found/returned/claimed)
- ✅ **Advanced Filtering**: Filter by status, category, date range

### **User Management** (`/admin/users`) ✨ UPDATED
- ✅ **View**: Complete user profiles with item statistics
- ✅ **Search**: Find users by name or email
- ✅ **Filter**: Filter by role (user/admin)
- ✅ **Statistics**: View user activity (items posted, found, returned)
- ✅ **Delete**: Remove users and all their associated items 🗑️
- ❌ **Edit**: User editing not implemented
- ❌ **Create**: User creation not available (users register themselves)
- ❌ **Role Management**: Cannot change user roles
- ❌ **Password Reset**: Not available through admin panel

**Delete User Feature:**
- Clean trash can icon instead of non-functional edit buttons
- Confirmation dialog with user details
- Permanently deletes user and all their items
- Real-time table updates after deletion
- Proper error handling and user feedback

---

## 🎯 Key Features

### **Frontend (React)**
- 📱 **Responsive Design**: Works on desktop and mobile
- 🔐 **User Authentication**: Login/register with JWT
- 📋 **Item Listings**: Browse lost and found items
- 🔍 **Search & Filter**: Find items by category, status, keywords
- 📸 **Image Upload**: Upload photos of items (local storage fallback)
- 👤 **User Profiles**: Manage personal items and account

### **Backend (Python)**
- 🗄️ **PostgreSQL Database**: Robust relational database
- 🔒 **JWT Authentication**: Secure token-based auth
- 🖼️ **Image Storage**: AWS S3 with local fallback
- 📧 **Email Integration**: Ready for notifications (not implemented)
- 🛡️ **Admin Panel**: Full administrative interface
- 🔄 **Auto-Migration**: Database schema updates automatically

### **Admin Features**
- 📊 **Dashboard**: Overview of system statistics
- 👥 **User Management**: View, search, and delete users
- 📦 **Item Management**: Full CRUD operations with admin notes
- 🔍 **Advanced Search**: Filter and search across all data
- 📈 **Analytics**: System usage and item statistics
- 🗑️ **Data Management**: Clean deletion of users and items

---

## 📁 File Structure

```
example-lost-found-proj/
├── 📁 backend/                 # Python backend
│   ├── 📁 venv/               # Python virtual environment
│   ├── 📁 uploads/            # Local image storage
│   ├── 📁 admin_build/        # Pre-built admin interface
│   ├── 📄 postgresql_server.py # Main backend server
│   ├── 📄 database_config.py   # Database configuration
│   ├── 📄 s3_upload.py        # AWS S3 integration
│   ├── 📄 admin_interface_modifier.js # Admin UI enhancements ✨
│   ├── 📄 requirements.txt     # Python dependencies
│   └── 📄 .env                # Environment variables
├── 📁 frontend/               # React frontend
│   ├── 📁 src/               # Source code
│   ├── 📁 public/            # Static assets
│   ├── 📄 package.json       # Node.js dependencies
│   └── 📄 tsconfig.json      # TypeScript configuration
├── 📁 config/                # Configuration templates
├── 📁 docs/                  # Documentation
├── 📄 setup.sh              # Quick setup script
├── 📄 setup-enhanced.sh      # Enhanced setup with Python compatibility
└── 📄 README.md             # Project overview
```

---

## ⚙️ Configuration

### **Environment Variables** (backend/.env)
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lost_found_campus
DB_USER=your_username
DB_PASSWORD=your_password

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-west-2
```

### **Database Setup**
The application uses PostgreSQL. Both setup scripts will:
1. Check for database connectivity
2. Create necessary tables automatically
3. Handle schema migrations (including new admin_notes field)
4. Set up proper indexes and constraints

---

## 🚨 Troubleshooting

### **Common Issues:**

#### **Port Already in Use**
```bash
# Kill existing processes
pkill -f "postgresql_server.py"
pkill -f "npm start"
# Or use the setup script which handles this automatically
./setup.sh
```

#### **Python Version Compatibility**
- **Python 3.7-3.12**: Use `./setup.sh`
- **Python 3.13+**: Use `./setup-enhanced.sh`

#### **Database Connection Issues**
1. Ensure PostgreSQL is running
2. Check .env file configuration
3. Verify database credentials
4. Ensure database exists

#### **S3 Upload Issues**
- Application falls back to local storage automatically
- Check AWS credentials in .env file
- Verify S3 bucket permissions
- S3 is optional - local storage works fine

#### **Admin Panel Issues**
- Default admin credentials: admin/admin123
- Admin interface uses JavaScript injection for enhanced features
- Clear browser cache if buttons don't work properly

---

## 🔄 Recent Updates

### **Version 2.0 Features:**
- ✨ **Enhanced Admin User Management**: Functional delete buttons with trash can icons
- ✨ **Admin Notes Field**: Internal notes for item tracking
- ✨ **Improved Item Filtering**: Returned items hidden from public view
- ✨ **Better Error Handling**: Enhanced user feedback and validation
- ✨ **Database Auto-Migration**: Automatic schema updates for existing databases
- ✨ **Cleanup & Optimization**: Removed unused files and improved performance

### **Admin Interface Improvements:**
- Replaced non-functional edit buttons with working delete buttons
- Clean trash can icons matching modern UI standards
- API-driven user matching for reliable functionality
- Real-time table updates after user deletion
- Improved error messages and user feedback

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review error logs in terminal
3. Ensure all dependencies are installed
4. Verify database and environment configuration
5. Try the enhanced setup script for compatibility issues

The application is designed to be robust with fallbacks for common issues (S3 → local storage, enhanced Python compatibility, etc.).