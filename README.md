# 🚀 Lost and Found Campus Application

A modern, full-stack web application for managing lost and found items on campus with **Python backend** and **AWS S3 cloud storage integration**. This professional application helps students and staff efficiently report lost items and claim found items with real-time search, filtering, image upload capabilities, and complete administrative control.

## ✨ Key Features

### 🔍 **User Features**
- **User Authentication**: Secure JWT-based authentication with user management
- **Real-time Search**: Advanced search with filtering capabilities
- **Advanced Filtering**: Category-based filtering with status queries
- **Image Upload**: Direct upload to AWS S3 cloud storage with local backup
- **Item Management**: Report lost items and register found items with UUID tracking
- **Responsive Design**: Mobile-first responsive design with modern UI/UX
- **Data Persistence**: JSON-based data storage with backup capabilities

### 🛡️ **Admin Panel Features**
- **Secure Authentication**: Role-based access control (admin/admin123)
- **Complete Item Management**: Full CRUD operations on all items
- **Statistics Dashboard**: Real-time analytics and item counts
- **User Management**: View and manage registered users
- **Data Export**: JSON-based data management and backup

### 🗄️ **Database Features**
- **JSON Backend**: Lightweight JSON-based data storage
- **UUID Primary Keys**: Globally unique identifiers for all entities
- **Data Relationships**: Structured data relationships between users, items, and categories
- **Data Backup**: Automatic JSON file backups for data safety
- **Migration Ready**: Clean data structure ready for database migration

### 🛠️ **Technical Excellence**
- **Modern UI**: Beautiful Material-UI design with TypeScript
- **Cloud Storage**: AWS S3 integration for reliable image hosting
- **Professional Error Handling**: Comprehensive error boundaries and validation
- **Testing Suite**: Jest testing with comprehensive coverage
- **Clean Code**: ESLint compliant, well-documented, maintainable codebase

## 🎯 Tech Stack

### **Frontend**
- **React 18** with TypeScript
- **Material-UI (MUI) v5** for design system with custom mobile theme
- **React Router v6** for navigation
- **Axios** for API communication
- **Jest** with React Testing Library

### **Backend**
- **Python 3.8+** with custom HTTP server
- **AWS S3** with boto3 for cloud storage
- **JSON persistence** with automatic data management
- **Multipart form data** handling for file uploads
- **Admin API endpoints** with authentication

### **Infrastructure**
- **AWS S3** for secure image storage
- **Environment variables** for secure configuration
## 🚀 Quick Start

### **Prerequisites**
- **PostgreSQL** (version 12+ recommended)
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** version control

### **One-Click Setup & Start**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd example-lost-found-proj

# 2. One-click setup and start (recommended)
./setup-enhanced.sh

# OR basic setup (if you have Python compatibility issues)
./setup.sh
```

**That's it!** 🎉 Both scripts will:
- ✅ Set up backend (Python virtual environment, dependencies, database)
- ✅ Set up frontend (npm dependencies)
- ✅ Start both servers automatically
- ✅ Handle Python version compatibility
- ✅ Check all prerequisites

### **Access the Application**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📊 **Admin Panel**: http://localhost:8000/admin (admin/admin123)

### **Quick Start (After Initial Setup)**
```bash
# To restart both servers, just run either setup script again:
./setup-enhanced.sh

# OR
./setup.sh
```

Then open **http://localhost:3000** in your browser! 🎉

## 📋 Prerequisites

- **Node.js** v16+ ([Download](https://nodejs.org/))
- **Python** 3.8+ ([Download](https://python.org/))
- **AWS Account** for S3 storage ([Create](https://aws.amazon.com/))
- **Git** ([Download](https://git-scm.com/))

### Verify Installation:
```bash
node --version    # Should show v16+
python3 --version # Should show v3.8+
git --version     # Should show git version
```

## 🔧 Configuration

### **AWS S3 Setup**
1. **Create S3 Bucket**: 
   - Go to AWS S3 Console
   - Create bucket (e.g., `lost-found-campus-yourname`)
   - **Important**: Disable ACLs (keep "ACLs disabled" selected)
   - Note your bucket name and region

2. **Create IAM User**:
   - Go to AWS IAM Console
   - Create user with programmatic access
   - Attach `AmazonS3FullAccess` policy
   - Save Access Key ID and Secret Access Key

3. **Configure Environment Variables**:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"  
export AWS_S3_BUCKET_NAME="your_bucket_name_here"
export AWS_REGION="your_region_here"  # e.g., "us-east-1"
```

### **Test S3 Connection**
```bash
source venv/bin/activate
python3 -c "from s3_config import test_s3_connection; test_s3_connection()"
```
You should see: ✅ S3 connection successful!

## 🎮 Application Access

- **User Frontend**: http://localhost:3000 (Main user interface)
- **Admin Panel**: http://localhost:8000/admin (React-powered admin dashboard - admin/admin123)
- **Backend API**: http://localhost:8000/api/items
- **Admin API**: http://localhost:8000/api/admin/items

### **Access Control**
- **User Interface**: Only accessible from `localhost:3000`
- **Admin Interface**: Only accessible from `localhost:8000/admin` (React-based)
- **No admin button** in the user interface for clean separation

### **🎯 Admin Interface (React-Based)**
The admin interface has been migrated from HTML to a full React application:
- **AdminLogin**: Professional login component with Material-UI design
- **AdminDashboard**: Complete dashboard with real-time statistics
- **AdminContext**: React state management for admin authentication
- **Responsive Design**: Mobile-friendly Material-UI components
- **Admin Mode Detection**: Automatically configures API calls when served from backend

## 🧪 Testing the Application

### **User Interface Testing**
1. **Browse Items**: View all active lost/found items in beautiful responsive grid
2. **Search**: Try searching for "iPhone", "backpack", or any keyword
3. **Filter**: Use category filters (electronics, accessories, etc.) and status filters
4. **Create Item**: Click square "+" button and test S3 image upload
5. **View Details**: Click any item to see full details page
6. **Mobile Experience**: Test on mobile devices or browser dev tools

### **Admin Panel Testing**
1. **Access Admin**: Go to http://localhost:8000/admin
2. **Login**: Use admin/admin123 credentials
3. **View Statistics**: See real-time counts of all items
4. **Manage Items**: View ALL items including returned ones
5. **Update Status**: Mark items as returned and see them disappear from user interface
6. **Admin Features**: Test item deletion, status updates, notes

### **Mobile Responsiveness Testing**
1. **Open Browser Dev Tools**: F12 → Toggle device toolbar
2. **Test Different Sizes**: iPhone, iPad, Android phones
3. **Touch Targets**: Verify 44px minimum touch areas
4. **Navigation**: Test sticky header and responsive layout
5. **Button Behavior**: Verify square "+" button shows icon only on mobile

## 📱 Complete Feature List

### ✅ **User Features**
- Real-time search with debounced input
- Advanced category and status filtering  
- AWS S3 image upload with progress indicators
- Individual item detail pages
- Professional mobile-responsive design
- Touch-friendly interface (44px+ touch targets)
- Automatic hiding of returned items
- Square action button positioned right of header
- Responsive grid layout (1/2/3 columns)
- Enhanced typography and visual hierarchy

### ✅ **Admin Features**  
- Secure admin authentication system
- Complete item management dashboard
- Real-time statistics with accurate counts
- Mark items as lost/found/returned
- View all items including returned ones
- Add administrative notes to items
- Delete items functionality
- Admin-only API endpoints

### ✅ **Technical Features**
- TypeScript for type safety
- ESLint compliant code
- Mobile-first responsive design
- AWS S3 cloud storage integration
- Unique file naming with UUIDs
- Professional error handling
- Clean component architecture
- Comprehensive testing setup

### ✅ **Security & Data Protection**
- Environment variables for AWS credentials
- Returned items hidden from public view
- Admin-only access to sensitive operations
- Secure S3 file uploads
- Proper CORS configuration

## 🗂️ Project Structure

```
example-lost-found-proj/
├── src/                     # React TypeScript frontend
│   ├── components/          # Reusable UI components
│   ├── pages/              # Main application pages
│   ├── types/              # TypeScript type definitions
│   └── index.tsx           # App entry point with enhanced theme
├── enhanced_server.py       # Python backend with S3 & admin features
├── s3_config.py            # AWS S3 configuration
├── lost_found_db.json      # JSON database with item persistence
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── quick_start.sh          # Automated setup script
├── SETUP_GUIDE.md          # Comprehensive setup guide
├── __mocks__/              # Jest testing mocks
└── venv/                   # Python virtual environment
```

## 🚨 Troubleshooting

### **Port Issues**
```bash
# Kill backend process
lsof -ti:8000 | xargs kill -9
# Kill frontend process  
lsof -ti:3000 | xargs kill -9
```

### **S3 Connection Issues**
- Verify AWS credentials are set as environment variables
- Check bucket name and region are correct
- Ensure IAM user has S3 permissions
- Confirm bucket has ACLs disabled

### **Installation Issues**
```bash
# Python issues
source venv/bin/activate
pip install -r requirements.txt

# Node.js issues
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### **Admin Panel Issues**
- Verify you're using correct credentials (admin/admin123)
- Check that postgresql_server.py is running
- Ensure you're accessing http://localhost:8000/admin

### **Mobile Responsiveness Issues**
- Clear browser cache
- Test in browser dev tools with device simulation
- Verify viewport meta tag in public/index.html

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📖 Documentation

- **[Complete Documentation](docs/DOCUMENTATION.md)**: Comprehensive setup, API, and troubleshooting guide
- **[Database Schema](docs/DOCUMENTATION.md#database-schema)**: PostgreSQL table structure
- **[API Reference](docs/DOCUMENTATION.md#api-documentation)**: Complete API endpoint documentation

## 🗂️ Project Structure

```
example-lost-found-proj/
├── backend/
│   ├── postgresql_server.py     # Main backend server
│   ├── database_config.py       # Database configuration & setup
│   ├── s3_upload.py             # AWS S3 integration
│   ├── seed_database.py         # Database seeding utility
│   ├── sql_query.py             # SQL query utility
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── lost_found_db.json       # Sample data backup
│   ├── user_db.json             # User data backup
│   └── uploads/                 # Local image storage
├── frontend/
│   ├── src/                     # React TypeScript source
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   └── build/                   # Production build
├── config/
│   ├── database.env.example     # Database config template
│   └── aws-credentials-template.txt
└── docs/
    └── DOCUMENTATION.md         # Complete documentation
```

## 🔒 Security Notes

- **PostgreSQL**: Use strong passwords and proper user permissions in production
- **Environment Variables**: Never commit sensitive credentials to version control
- **Admin Access**: Change default admin credentials (admin/admin123) in production
- **AWS S3**: Use IAM roles and least-privilege principle for S3 access

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 What You Get

Once setup is complete, you'll have a **production-ready** Lost & Found Campus application featuring:

### 🎯 **Modern Architecture**
- **Frontend**: React with TypeScript for type safety
- **Backend**: Python with PostgreSQL for robust data management
- **Storage**: AWS S3 integration with local backup
- **Authentication**: JWT-based secure authentication
- **Database**: PostgreSQL with proper relational design

### 🛡️ **Administrative Features**
- **Admin Panel**: Complete item and user management
- **Analytics**: Real-time statistics and reporting
- **Data Export**: SQL query capabilities for analysis
- **User Management**: Role-based access control
- **Data Integrity**: Foreign key relationships and constraints

### 🏗️ **Production Ready**
- **Scalable**: PostgreSQL database for growth
- **Maintainable**: Clean codebase with proper documentation
- **Secure**: Environment-based configuration
- **Responsive**: Mobile-first responsive design
- **Backup**: JSON file backups for data safety

---

## 📐 Figma Prototype

Our design assets and project documentation are available on Figma. This includes key UI/UX prototypes and essential diagrams used throughout development.

[🔗 View the Complete Figma Workspace](https://www.figma.com/design/pnSc3hQ3Hnj582Fi5I6Izc/Advenced-Software-Project?node-id=0-1&t=opU5IjUV8G3EgwZa-1)


### 📊 Included Visual Assets
- **Iteration 1 Burn-down Chart**
- **Iteration 2 Burn-down Chart**
- **Iteration 1 Velocity Chart**
- **Iteration 2 Velocity Chart**
- **Draft Entity-Relationship (ERD) Diagram**
- **Finalized Entity-Relationship (ERD) Diagram**
- **Unified Modeling Language (UML) Diagram**
- **Final UI Design Prototype**

These resources provide a comprehensive view of our project's progress, data architecture, and user interface development.

**Perfect for campus deployment!** 🚀🗄️✨

*Documentation Last Updated: August 1, 2025*
