#!/usr/bin/env python3
"""
Enhanced HTTP server for Lost & Found Campus API with S3 file upload support
Compatible with Python 3.13
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import email.message
from email import message_from_bytes
import io
import os
import jwt
import base64
from s3_config import upload_file_to_s3, test_s3_connection
# Import user authentication module
from user_auth import authenticate_user, create_user, get_user_by_id
import uuid
import shutil
import re

# Secret key for JWT tokens
JWT_SECRET = "your_jwt_secret_key_here"
TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

PORT = 8000
DATABASE_FILE = "lost_found_db.json"

# Mock data with existing items
default_items = [
    {
        "id": "1",
        "title": "Lost iPhone 13",
        "description": "Blue iPhone 13 with a clear case. Lost near the library on Tuesday.",
        "category": "electronics",
        "status": "lost",
        "location_found": "Main Library",
        "date_found": "2024-03-20",
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-13-blue-select-2021?wid=940&hei=1112&fmt=png-alpha&.v=1645036275334",
        "finder_id": "user1",
        "created_at": "2024-03-20T10:00:00Z"
    },
    {
        "id": "2", 
        "title": "Found Car Keys",
        "description": "Honda keys with a red keychain found in parking lot B.",
        "category": "accessories",
        "status": "found",
        "location_found": "Parking Lot B",
        "date_found": "2024-03-19",
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "finder_id": "user2",
        "created_at": "2024-03-19T15:00:00Z"
    },
    {
        "id": "3",
        "title": "Lost Backpack", 
        "description": "Black JanSport backpack with laptop inside. Lost in Student Center.",
        "category": "other",
        "status": "lost",
        "location_found": "Student Center",
        "date_found": "2024-03-18",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "finder_id": "user3",
        "created_at": "2024-03-18T09:30:00Z"
    },
    {
        "id": "4",
        "title": "Found Textbook",
        "description": "Calculus textbook found in classroom 205. Has 'Sarah' written inside.",
        "category": "books",
        "status": "found",
        "location_found": "Classroom 205",
        "date_found": "2024-03-17",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "finder_id": "user4",
        "created_at": "2024-03-17T14:20:00Z"
    },
    {
        "id": "5",
        "title": "Lost Wallet",
        "description": "Brown leather wallet with student ID inside. Lost in cafeteria.",
        "category": "accessories",
        "status": "lost",
        "location_found": "Main Cafeteria",
        "date_found": "2024-03-16",
        "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "finder_id": "user5",
        "created_at": "2024-03-16T12:15:00Z"
    },
    {
        "id": "6",
        "title": "Found Earbuds",
        "description": "Apple AirPods found in the gym locker room.",
        "category": "electronics",
        "status": "found",
        "location_found": "Gym Locker Room",
        "date_found": "2024-03-15",
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MME73?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1632861342000",
        "finder_id": "user6",
        "created_at": "2024-03-15T18:45:00Z"
    }
]

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file_locally(file_data, original_filename):
    """Save file to local uploads directory when S3 is not available"""
    try:
        # Generate unique filename
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return the relative URL path
        return f"/uploads/{unique_filename}"
    except Exception as e:
        print(f"❌ Local file save failed: {str(e)}")
        self._send_json_response({"error": f"File upload failed: {str(e)}"}, 500)
        return

def load_items():
    """Load items from JSON file, create with default data if file doesn't exist"""
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r') as f:
                data = json.load(f)
                print(f"📂 Loaded {len(data)} items from database")
                return data
        else:
            print("📂 No database file found, creating with default items")
            save_items(default_items)
            return default_items.copy()
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        print("📂 Using default items")
        return default_items.copy()

def save_items(items):
    """Save items to JSON file"""
    try:
        with open(DATABASE_FILE, 'w') as f:
            json.dump(items, f, indent=2)
        print(f"💾 Saved {len(items)} items to database")
    except Exception as e:
        print(f"❌ Error saving database: {e}")

# Load items from database on startup
mock_items = load_items()

class EnhancedRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        """Send CORS headers for cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        
    def _send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except BrokenPipeError:
            # Client disconnected before response was sent - log but don't crash
            print(f"🔗 Client disconnected before response could be sent")
            return
        except Exception as e:
            # Log other exceptions but don't crash
            print(f"❌ Error sending response: {str(e)}")
            return
    
    def _create_token(self, user_id):
        """Create JWT token for user authentication"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token
    
    def _verify_token(self, token):
        """Verify JWT token and return user_id if valid"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _get_auth_user_id(self):
        """Get authenticated user ID from Authorization header"""
        auth_header = self.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        return self._verify_token(token)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Serve uploaded files
        if path.startswith('/uploads/'):
            file_path = os.path.join(UPLOAD_DIR, os.path.basename(path))
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    # Set content type based on file extension
                    ext = os.path.splitext(file_path)[1].lower()
                    content_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(ext, 'application/octet-stream')
                    
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', str(len(content)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except BrokenPipeError:
                    # Client disconnected before file could be served - log but don't crash
                    print(f"🔗 Client disconnected before file could be served: {file_path}")
                    return
                except Exception as e:
                    print(f"❌ Error serving file: {str(e)}")
                    self._send_json_response({"error": "Error serving file"}, 500)
                    return
            else:
                self._send_json_response({"error": "File not found"}, 404)
                return
        
        # Handle /api/items endpoint
        elif path == '/api/items':
            try:
                # Get items from database
                items = load_items()
                
                # Apply filters if any
                search = query_params.get('search', [''])[0]
                category = query_params.get('category', [''])[0]
                status = query_params.get('status', [''])[0]
                
                if search:
                    items = [item for item in items if search.lower() in item.get('title', '').lower() or search.lower() in item.get('description', '').lower()]
                if category:
                    items = [item for item in items if item.get('category', '').lower() == category.lower()]
                if status:
                    items = [item for item in items if item.get('status', '').lower() == status.lower()]
                
                # Sort by created_at in descending order (newest first)
                items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                
                # Paginate results
                page = int(query_params.get('page', ['1'])[0])
                per_page = 12
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_items = items[start_idx:end_idx]
                
                self._send_json_response({
                    "items": paginated_items,
                    "total": len(items),
                    "page": page,
                    "per_page": per_page
                })
                return
            except Exception as e:
                print(f"❌ Error getting items: {str(e)}")
                self._send_json_response({"error": "Failed to get items"}, 500)
                return
        
        if path == '/':
            self._send_json_response({
                "message": "Lost & Found Campus API", 
                "endpoints": [
                    "/api/items",
                    "/api/items/{id}",
                    "/api/users/me",
                    "/admin"
                ]
            })
        elif path == '/admin':
            self._serve_admin_page()
        elif path == '/api/admin/items':
            self._handle_get_admin_items(query_params)
        elif path.startswith('/api/items/'):
            item_id = path.split('/')[-1]
            self._handle_get_item(item_id)
        elif path == '/api/users/me':
            self._handle_get_current_user()
        elif path.startswith('/api/placeholder/'):
            # Handle placeholder image requests
            self._handle_placeholder_image(path)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests (create items and user authentication)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/items':
            # Check if it's multipart (file upload) or JSON
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in content_type:
                self._handle_create_item_with_file()
            else:
                self._handle_create_item_json()
        elif path == '/api/admin/login':
            self._handle_admin_login()
        elif path == '/api/users/register':
            self._handle_user_register()
        elif path == '/api/users/login':
            self._handle_user_login()
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_PUT(self):
        """Handle PUT requests (update items)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle item updates
        if path.startswith('/api/items/'):
            item_id = path.split('/')[-1]
            self._handle_update_item(item_id)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_DELETE(self):
        """Handle DELETE requests (delete items)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle item deletion
        if path.startswith('/api/items/'):
            item_id = path.split('/')[-1]
            self._handle_delete_item(item_id)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def _handle_get_items(self, query_params):
        """Handle GET /api/items with filtering and pagination"""
        # Get query parameters
        page = int(query_params.get('page', ['1'])[0])
        search = query_params.get('search', [''])[0]
        category = query_params.get('category', [''])[0]
        status = query_params.get('status', [''])[0]
        per_page = 12
        
        # Load items from database and filter - always exclude returned items for regular API users
        items = load_items()
        filtered_items = [item for item in items if item['status'] != 'returned']
        
        if search:
            search_lower = search.lower()
            filtered_items = [
                item for item in filtered_items
                if search_lower in item['title'].lower() or search_lower in item['description'].lower()
            ]
        
        if category and category != '':
            filtered_items = [
                item for item in filtered_items
                if item['category'] == category
            ]
        
        if status and status != '':
            filtered_items = [
                item for item in filtered_items
                if item['status'] == status
            ]
        
        # Pagination
        total = len(filtered_items)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = filtered_items[start_idx:end_idx]
        
        # Add user information to each item
        items_with_user = []
        for item in paginated_items:
            item_with_user = item.copy()
            if 'user_id' in item_with_user:
                user = get_user_by_id(item_with_user['user_id'])
                if user:
                    item_with_user['user'] = user
            items_with_user.append(item_with_user)
        
        response = {
            "items": items_with_user,
            "total": total,
            "page": page,
            "per_page": per_page
        }
        
        self._send_json_response(response)
    
    def _handle_get_admin_items(self, query_params):
        """Handle GET /api/admin/items - shows ALL items including returned ones for admin"""
        # Get query parameters
        search = query_params.get('search', [''])[0]
        category = query_params.get('category', [''])[0]
        status = query_params.get('status', [''])[0]
        
        # For admin, show ALL items including returned ones (no pagination)
        items = load_items()
        filtered_items = items.copy()
        
        if search:
            search_lower = search.lower()
            filtered_items = [
                item for item in filtered_items
                if search_lower in item['title'].lower() or search_lower in item['description'].lower()
            ]
        
        if category and category != '':
            filtered_items = [
                item for item in filtered_items
                if item['category'] == category
            ]
        
        if status and status != '':
            filtered_items = [
                item for item in filtered_items
                if item['status'] == status
            ]
        
        # Sort by created_at in descending order (newest first)
        filtered_items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Return all items without pagination for admin
        response = {
            "items": filtered_items,
            "total": len(filtered_items),
            "page": 1,
            "per_page": len(filtered_items)
        }
        
        self._send_json_response(response)
    
    def _handle_get_item(self, item_id):
        """Handle GET /api/items/{id}"""
        items = load_items()
        for item in items:
            if str(item['id']) == str(item_id):
                # Prevent access to returned items for regular API users
                if item['status'] == 'returned':
                    self._send_json_response({"error": "This item has been returned to its owner and is no longer available."}, 404)
                    return
                
                # Add user information
                result = item.copy()
                if 'user_id' in result:
                    user = get_user_by_id(result['user_id'])
                    if user:
                        result['user'] = user
                
                self._send_json_response(result)
                return
        
        self._send_json_response({"error": "Item not found"}, 404)
    
    def _handle_create_item_with_file(self):
        """Handle POST /api/items with multipart/form-data (file upload)"""
        try:
            # Get authenticated user ID
            user_id = self._get_auth_user_id()
            
            if not user_id:
                self._send_json_response({"error": "Authentication required"}, 401)
                return
                
            # Get user information
            user = get_user_by_id(user_id)
            if not user:
                self._send_json_response({"error": "User not found"}, 404)
                return

            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self._send_json_response({"error": "Invalid content type"}, 400)
                return
            
            # Parse boundary
            boundary = content_type.split('boundary=')[1].encode()
            remainbytes = int(self.headers.get('Content-Length', 0))
            line = self.rfile.readline()
            remainbytes -= len(line)
            
            if not boundary in line:
                self._send_json_response({"error": "Invalid boundary"}, 400)
                return
            
            # Parse form fields
            item_data = {}
            file_data = None
            filename = None
            
            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                
                if boundary in line:
                    line = self.rfile.readline()
                    remainbytes -= len(line)
                    
                    # Parse content disposition
                    content_disposition = line.decode()
                    if 'Content-Disposition' not in content_disposition:
                        continue
                
                    # Get field name
                    name_match = re.search('name="([^"]+)"', content_disposition)
                    if not name_match:
                        continue
                        
                    field_name = name_match.group(1)
                    
                    # Check if this is a file field
                    if 'filename' in content_disposition:
                        filename_match = re.search('filename="([^"]+)"', content_disposition)
                        if filename_match:
                            filename = filename_match.group(1)
                        
                        # Skip content type line
                        line = self.rfile.readline()
                        remainbytes -= len(line)
                        
                        # Skip blank line
                        line = self.rfile.readline()
                        remainbytes -= len(line)
                        
                        # Read file data
                        file_data = b''
                        prev_line = None
                        while remainbytes > 0:
                            line = self.rfile.readline()
                            remainbytes -= len(line)
                            
                            if boundary in line:
                                if prev_line and prev_line.endswith(b'\r\n'):
                                    file_data = file_data[:-2]
                                break
                            elif prev_line:
                                file_data += prev_line
                            prev_line = line
                    else:
                        # Skip blank line
                        line = self.rfile.readline()
                        remainbytes -= len(line)
                        
                        # Read field value
                        line = self.rfile.readline()
                        remainbytes -= len(line)
                        value = line.decode().strip()
                        item_data[field_name] = value

            # Handle image upload (optional)
            image_url = None
            if filename and file_data:
                print(f"📤 Uploading image: {filename}")
            
            # Try local storage first since S3 is not configured
            try:
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                file_extension = filename.split('.')[-1] if '.' in filename else ''
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # Save file
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                # Set the URL path
                image_url = f"/uploads/{unique_filename}"
                print(f"✅ Image saved locally: {image_url}")
                
            except Exception as e:
                print(f"❌ Local save failed: {str(e)}")
                self._send_json_response({"error": f"File upload failed: {str(e)}"}, 500)
                return
            else:
                print("📝 Creating item without image")
            
            # Handle title auto-generation
            title = item_data.get('title', '').strip()
            description = item_data.get('description', '').strip()
            status = item_data.get('status', 'lost')
            
            # Auto-generate title if empty
            if not title and description:
                title = description[:50]
                if len(description) > 50:
                    title += '...'
            elif not title:
                title = 'Lost Item' if status == 'lost' else 'Found Item'
            
            # Generate new item
            new_id = str(uuid.uuid4())
            new_item = {
                "id": new_id,
                "title": title,
                "description": description,
                "category": item_data.get('category', ''),
                "status": status,
                "location": item_data.get('location_found', ''),  # Handle frontend field name
                "date_found": item_data.get('date_found', datetime.now().strftime("%Y-%m-%d")),
                "image_url": image_url,
                "user_id": user_id,
                "user_name": user.get('name', ''),  # Add user's name
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add to items database
            items = load_items()
            items.append(new_item)
            save_items(items)
            
            print(f"✅ Created new item: {new_item['title']} (ID: {new_id})")
            self._send_json_response({
                "success": True,
                "message": "Item created successfully", 
                "item": new_item
            })
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            self._send_json_response({"error": "File upload failed: " + str(e)}, 500)
            return
    
    def _handle_create_item_json(self):
        """Handle POST /api/items with JSON data"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                item_data = json.loads(post_data.decode('utf-8'))
                
                # Get authenticated user ID
                user_id = self._get_auth_user_id()
                
                if not user_id:
                    self._send_json_response({"error": "Authentication required"}, 401)
                    return
                
                # Get user information
                user = get_user_by_id(user_id)
                if not user:
                    self._send_json_response({"error": "User not found"}, 404)
                    return
                
                # Validate required fields
                required_fields = ['title', 'description', 'category', 'status']
                for field in required_fields:
                    if field not in item_data:
                        self._send_json_response(
                            {"error": f"Missing required field: {field}"},
                            400
                        )
                        return
                
                # Load current items and create new item
                items = load_items()
                new_id = str(uuid.uuid4())
                new_item = {
                    "id": new_id,
                    "title": item_data['title'],
                    "description": item_data['description'],
                    "category": item_data['category'],
                    "status": item_data['status'],
                    "location": item_data.get('location', ''),
                    "date_found": item_data.get('date_found', datetime.now().strftime("%Y-%m-%d")),
                    "image_url": item_data.get('image_url', None),
                    "user_id": user_id,
                    "user_name": user.get('name', 'Unknown User'),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Add to items list and save
                items.append(new_item)
                save_items(items)
                
                print(f"✅ Created new item without image: {new_item['title']} (ID: {new_id})")
                self._send_json_response({
                    "success": True,
                    "message": "Item created successfully",
                    "item": new_item
                })
            else:
                self._send_json_response({"error": "No data provided"}, 400)
                
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)
    
    def _handle_admin_login(self):
        """Handle admin login with simple credentials"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                credentials = json.loads(post_data.decode('utf-8'))
                
                # Simple admin credentials (in production, use proper authentication)
                if (credentials.get('username') == 'admin' and 
                    credentials.get('password') == 'admin123'):
                    
                    # Generate simple session token (in production, use proper JWT)
                    admin_token = "admin_" + str(datetime.now().timestamp())
                    
                    self._send_json_response({
                        "success": True,
                        "token": admin_token,
                        "message": "Admin login successful"
                    })
                else:
                    self._send_json_response({"error": "Invalid credentials"}, 401)
            else:
                self._send_json_response({"error": "No credentials provided"}, 400)
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)
    
    def _handle_update_item(self, item_id):
        """Handle updating an item (status, etc.)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                update_data = json.loads(post_data.decode('utf-8'))
                
                # Load items from database
                items = load_items()
                
                # Find and update the item
                for i, item in enumerate(items):
                    if item['id'] == item_id:
                        # Update allowed fields
                        if 'status' in update_data:
                            items[i]['status'] = update_data['status']
                        if 'notes' in update_data:
                            items[i]['admin_notes'] = update_data['notes']
                        
                        # Add updated timestamp
                        items[i]['updated_at'] = datetime.now().isoformat() + "Z"
                        
                        # Save to database
                        save_items(items)
                        
                        print(f"✅ Updated item {item_id}: {update_data}")
                        self._send_json_response(items[i])
                        return
                
                self._send_json_response({"error": "Item not found"}, 404)
            else:
                self._send_json_response({"error": "No update data provided"}, 400)
        except Exception as e:
            print(f"❌ Error updating item: {e}")
            self._send_json_response({"error": str(e)}, 500)
    
    def _handle_delete_item(self, item_id):
        """Handle deleting an item"""
        try:
            # Load items from database
            items = load_items()
            
            # Find and remove the item
            for i, item in enumerate(items):
                if item['id'] == item_id:
                    deleted_item = items.pop(i)
                    
                    # Save to database
                    save_items(items)
                    
                    print(f"🗑️ Deleted item {item_id}: {deleted_item['title']}")
                    self._send_json_response({
                        "success": True,
                        "message": f"Item '{deleted_item['title']}' deleted successfully",
                        "deleted_item": deleted_item
                    })
                    return
            
            self._send_json_response({"error": "Item not found"}, 404)
        except Exception as e:
            print(f"❌ Error deleting item: {e}")
            self._send_json_response({"error": str(e)}, 500)

    def _handle_get_current_user(self):
        """Handle GET /api/users/me endpoint"""
        user_id = self._get_auth_user_id()
        
        if not user_id:
            self._send_json_response({"error": "Unauthorized"}, 401)
            return
            
        user = get_user_by_id(user_id)
        if not user:
            self._send_json_response({"error": "User not found"}, 404)
            return
            
        self._send_json_response(user)
    
    def _handle_placeholder_image(self, path):
        """Handle GET /api/placeholder/{width}/{height} - generate simple placeholder"""
        try:
            # Parse dimensions from path like /api/placeholder/64/64
            parts = path.split('/')
            if len(parts) >= 4:
                width = int(parts[3])
                height = int(parts[4]) if len(parts) > 4 else width
            else:
                width = height = 64
            
            # Create a simple SVG placeholder
            svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
                <rect width="{width}" height="{height}" fill="#e0e0e0" />
                <text x="50%" y="50%" text-anchor="middle" dy="0.35em" font-family="Arial, sans-serif" font-size="12" fill="#666">
                    No Image
                </text>
            </svg>'''
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Content-Length', str(len(svg_content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(svg_content.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Error generating placeholder: {str(e)}")
            self._send_json_response({"error": "Error generating placeholder"}, 500)
    
    def _handle_user_register(self):
        """Handle user registration"""
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(request_body)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            if not all([name, email, password]):
                self._send_json_response(
                    {"error": "Name, email and password are required"}, 
                    400
                )
                return
                
            user, error = create_user(name, email, password)
            
            if error:
                self._send_json_response({"error": error}, 400)
                return
                
            token = self._create_token(user["id"])
            
            self._send_json_response({
                "message": "User registered successfully",
                "token": token,
                "user": user
            })
            
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)
    
    def _handle_user_login(self):
        """Handle user login"""
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(request_body)
            email = data.get('email')
            password = data.get('password')
            
            if not all([email, password]):
                self._send_json_response(
                    {"error": "Email and password are required"}, 
                    400
                )
                return
                
            user, error = authenticate_user(email, password)
            
            if error:
                self._send_json_response({"error": error}, 401)
                return
                
            token = self._create_token(user["id"])
            
            self._send_json_response({
                "message": "Login successful",
                "token": token,
                "user": user
            })
            
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)

    def _serve_admin_page(self):
        """Serve the admin dashboard HTML page"""
        admin_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lost & Found Campus - Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 25%, #3b82f6 100%);
            min-height: 100vh;
            color: #1f2937;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }
        
        h1 {
            color: white;
            text-align: center;
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 8px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.3);
            letter-spacing: -0.025em;
        }
        
        .subtitle {
            color: rgba(255,255,255,0.85);
            text-align: center;
            font-size: 1.125rem;
            margin-bottom: 32px;
            font-weight: 400;
        }
        
        .login-form {
            background: white;
            padding: 48px;
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            max-width: 420px;
            margin: 60px auto;
            text-align: center;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .login-form h2 {
            color: #1f2937;
            margin-bottom: 32px;
            font-size: 1.75rem;
            font-weight: 600;
        }
        
        .login-form input {
            width: 100%;
            padding: 16px 20px;
            margin: 12px 0;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.2s ease;
            background: #f9fafb;
            color: #374151;
        }
        
        .login-form input:focus {
            outline: none;
            border-color: #3b82f6;
            background: white;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .login-form button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 24px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .login-form button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.25);
        }
        
        .admin-panel {
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            margin-top: 32px;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 2px solid #f3f4f6;
        }
        
        .header h2 {
            color: #1f2937;
            font-size: 1.875rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }
        
        .logout-btn {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 14px;
        }
        
        .logout-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(220, 38, 38, 0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 28px;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid #e2e8f0;
            position: relative;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            border-color: #3b82f6;
        }
        
        .stat-card.active {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.25);
            border-color: #1e40af;
        }
        
        .stat-card.active .stat-number {
            color: white;
        }
        
        .stat-card.active .stat-label {
            color: rgba(255,255,255,0.9);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1e40af;
            margin-bottom: 8px;
            line-height: 1;
        }
        
        .stat-label {
            color: #64748b;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        
        .filter-controls {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        }
        
        .filter-controls h3 {
            margin: 0 0 16px 0;
            color: #374151;
            font-size: 1.125rem;
            font-weight: 600;
        }
        
        .filter-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .table-container {
            background: white;
            border-radius: 12px;
            overflow-x: auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            /* Enable horizontal scrolling on smaller screens */
            -webkit-overflow-scrolling: touch;
            /* Better mobile scrolling */
            scroll-behavior: smooth;
            position: relative;
        }
        
        /* Mobile-specific table container improvements */
        @media (max-width: 768px) {
            .table-container {
                margin: 0 -16px; /* Allow table to extend to screen edges */
                border-radius: 0;
                box-shadow: none;
                border-top: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
            }
            
            /* Add subtle scroll indicator */
            .table-container::after {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                width: 20px;
                background: linear-gradient(to left, rgba(255,255,255,0.8), transparent);
                pointer-events: none;
                z-index: 1;
            }
        }
        
        @media (max-width: 480px) {
            .table-container {
                margin: 0 -12px; /* Tighter margins for phones */
            }
        }
        
        .table-container::-webkit-scrollbar {
            height: 8px;
        }
        
        .table-container::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        .table-container::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        .table-container::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        .filter-btn {
            padding: 10px 16px;
            border: 1px solid #d1d5db;
            background: white;
            color: #6b7280;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
            font-size: 0.875rem;
        }
        
        .filter-btn:hover {
            border-color: #3b82f6;
            color: #1e40af;
            background: #f8fafc;
        }
        
        .filter-btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
        }
        
        .items-table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 20px 16px;
            text-align: left;
            font-weight: 700;
            color: #374151;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            border-bottom: 2px solid #e5e7eb;
        }
        
        td {
            padding: 16px;
            border-bottom: 1px solid #f3f4f6;
            vertical-align: middle;
            color: #374151;
        }
        
        tr:hover {
            background: #f8fafc;
        }
        
        .item-image {
            width: 64px;
            height: 64px;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .status-lost {
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }
        
        .status-found {
            background: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
        }
        
        .status-returned {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
        }
        
        .action-btn {
            padding: 8px 16px;
            margin: 2px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 600;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .mark-returned-btn {
            background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
            color: white;
        }
        
        .mark-returned-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(15, 118, 110, 0.25);
        }
        
        .delete-btn {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
        }
        
        .delete-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
        }
        
        .actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .category-tag {
            background: rgba(59, 130, 246, 0.1);
            color: #1e40af;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: capitalize;
            letter-spacing: 0.025em;
        }
        
        .hidden {
            display: none;
        }
        
        .loading {
            text-align: center;
            padding: 48px;
            color: #6b7280;
            font-style: italic;
            font-size: 1.125rem;
        }
        
        .no-items {
            text-align: center;
            padding: 48px 24px;
            color: #6b7280;
        }
        
        .no-items h3 {
            color: #374151;
            margin-bottom: 8px;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .status-lost {
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }
        
        .status-found {
            background: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
        }
        
        .status-returned {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 16px;
            }
            
            h1 {
                font-size: 1.875rem;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            .filter-controls {
                justify-content: center;
            }
            
            .header {
                flex-direction: column;
                gap: 16px;
                text-align: center;
            }
            
            .items-table {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
            }
            
            table {
                min-width: 800px;
            }
            
            .login-form {
                padding: 32px;
                margin: 32px auto;
            }
            
            /* Better mobile table styling */
            .admin-table {
                font-size: 0.8rem;
            }
            
            .admin-table th,
            .admin-table td {
                padding: 8px 6px;
            }
            
            /* Mobile button layout */
            .actions {
                flex-direction: column;
                gap: 6px;
                min-width: 90px;
                width: 90px;
            }
            
            .actions button {
                width: 100%;
                min-width: 80px;
                font-size: 0.7rem;
                padding: 6px 8px;
                height: 30px;
                border-radius: 4px;
            }
            
            /* Adjust column widths for mobile */
            .admin-table th:first-child,
            .admin-table td:first-child {
                width: 60px;
                min-width: 60px;
            }
            
            .admin-table th:nth-child(2),
            .admin-table td:nth-child(2) {
                width: 120px;
                min-width: 120px;
            }
            
            .admin-table th:nth-child(3),
            .admin-table td:nth-child(3) {
                width: 150px;
                min-width: 150px;
            }
            
            .admin-table th:last-child,
            .admin-table td:last-child {
                width: 90px;
                min-width: 90px;
            }
        }
        
        /* Extra small screens (phones) */
        @media (max-width: 480px) {
            .container {
                padding: 12px;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .filter-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
            
            .filter-btn {
                font-size: 0.75rem;
                padding: 8px 12px;
            }
            
            .admin-table {
                font-size: 0.75rem;
            }
            
            .admin-table th,
            .admin-table td {
                padding: 6px 4px;
            }
            
            /* Even smaller buttons for phones */
            .actions {
                min-width: 80px;
                width: 80px;
                gap: 4px;
            }
            
            .actions button {
                font-size: 0.65rem;
                padding: 4px 6px;
                height: 28px;
                min-width: 75px;
            }
            
            /* Tighter column widths for phones */
            .admin-table th:first-child,
            .admin-table td:first-child {
                width: 50px;
                min-width: 50px;
            }
            
            .admin-table th:nth-child(2),
            .admin-table td:nth-child(2) {
                width: 100px;
                min-width: 100px;
            }
            
            .admin-table th:nth-child(3),
            .admin-table td:nth-child(3) {
                width: 120px;
                min-width: 120px;
            }
            
            .admin-table th:last-child,
            .admin-table td:last-child {
                width: 80px;
                min-width: 80px;
            }
            
            /* Make images smaller on phones */
            .admin-table img {
                width: 40px !important;
                height: 40px !important;
            }
            
            /* Improve login form on phones */
            .login-form {
                padding: 24px;
                margin: 16px auto;
                width: calc(100% - 32px);
            }
        }
        
        .admin-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-top: 24px;
        }
        
        .admin-table th,
        .admin-table td {
            padding: 16px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: middle;
        }
        
        .admin-table th {
            background: #f8fafc;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }
        
        .admin-table td {
            color: #6b7280;
        }
        
        .admin-table img {
            border-radius: 8px;
            object-fit: cover;
            display: block;
        }
        
        .actions {
            display: flex;
            gap: 8px;
            flex-wrap: nowrap;
            justify-content: flex-start;
            align-items: center;
            min-width: 200px; /* Ensure enough space for buttons */
        }
        
        .actions button {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            min-width: 90px; /* Ensure consistent button width */
            height: 36px; /* Fixed height for all buttons */
            display: flex;
            align-items: center;
            justify-content: center;
            /* Touch-friendly improvements */
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        
        .mark-returned-btn {
            background: #10b981;
            color: white;
            min-width: 90px; /* Same as other buttons */
        }
        
        .mark-returned-btn:hover {
            background: #059669;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
        }
        
        .delete-btn {
            background: #ef4444;
            color: white;
            min-width: 90px; /* Same as other buttons */
        }
        
        .delete-btn:hover {
            background: #dc2626;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
        
        /* Responsive table */
        @media (max-width: 1200px) {
            .admin-table {
                font-size: 0.875rem;
            }
            
            .admin-table th,
            .admin-table td {
                padding: 12px 8px;
            }
            
            .actions {
                flex-direction: column;
                gap: 4px;
                min-width: 100px;
            }
            
            .actions button {
                width: 100%;
                min-width: 80px;
                font-size: 0.75rem;
                padding: 6px 12px;
                height: 32px;
            }
        }
        
        /* Ensure actions column has proper width */
        .admin-table th:last-child,
        .admin-table td:last-child {
            width: 200px;
            min-width: 200px;
        }
        
        @media (max-width: 1200px) {
            .admin-table th:last-child,
            .admin-table td:last-child {
                width: 120px;
                min-width: 120px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lost & Found Campus</h1>
        <p class="subtitle">Administrative Dashboard</p>
        
        <div class="login-form hidden" id="loginForm">
            <h2>Admin Login</h2>
            <input type="text" id="username" placeholder="Username" value="admin">
            <input type="password" id="password" placeholder="Password" value="admin123">
            <button onclick="login()">Sign In</button>
        </div>
        
        <div class="admin-panel hidden" id="adminPanel">
            <div class="header">
                <h2>Item Management</h2>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <div id="statsContainer"></div>
            
            <div class="filter-controls">
                <h3>Filter Items</h3>
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterItems('all')">All Items</button>
                    <button class="filter-btn" onclick="filterItems('lost')">Lost Only</button>
                    <button class="filter-btn" onclick="filterItems('found')">Found Only</button>
                    <button class="filter-btn" onclick="filterItems('returned')">Returned Only</button>
                </div>
            </div>
            
            <div class="table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th style="width: 80px;">Image</th>
                            <th style="width: 150px;">Title</th>
                            <th style="width: 200px;">Description</th>
                            <th style="width: 100px;">Category</th>
                            <th style="width: 80px;">Status</th>
                            <th style="width: 120px;">Location</th>
                            <th style="width: 100px;">Date</th>
                            <th style="width: 200px; min-width: 200px;">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="itemsTableBody">
                        <!-- Items will be loaded here -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        let currentItems = [];
        let currentFilter = 'all';
        
        // Utility function to truncate text
        function truncateText(text, maxLength) {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength).trim() + '...';
        }
        
        // Show login form on page load
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('loginForm').classList.remove('hidden');
        });
        
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('loginForm').classList.add('hidden');
                    document.getElementById('adminPanel').classList.remove('hidden');
                    loadItems();
                } else {
                    alert('Login failed: ' + result.error);
                }
            } catch (error) {
                alert('Login error: ' + error.message);
            }
        }
        
        function logout() {
            document.getElementById('adminPanel').classList.add('hidden');
            document.getElementById('loginForm').classList.remove('hidden');
            document.getElementById('username').value = 'admin';
            document.getElementById('password').value = 'admin123';
        }
        
        async function loadItems() {
            try {
                const response = await fetch('/api/admin/items');
                const data = await response.json();
                currentItems = data.items || [];
                updateStats();
                displayItems(currentItems);
            } catch (error) {
                console.error('Error loading items:', error);
            }
        }
        
        function updateStats() {
            const total = currentItems.length;
            const lost = currentItems.filter(item => item.status === 'lost').length;
            const found = currentItems.filter(item => item.status === 'found').length;
            const returned = currentItems.filter(item => item.status === 'returned').length;
            
            const statsContainer = document.getElementById('statsContainer');
            statsContainer.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card ${currentFilter === 'all' ? 'active' : ''}" onclick="filterItems('all')">
                        <div class="stat-number">${total}</div>
                        <div class="stat-label">Total Items</div>
                    </div>
                    <div class="stat-card ${currentFilter === 'lost' ? 'active' : ''}" onclick="filterItems('lost')">
                        <div class="stat-number">${lost}</div>
                        <div class="stat-label">Lost Items</div>
                    </div>
                    <div class="stat-card ${currentFilter === 'found' ? 'active' : ''}" onclick="filterItems('found')">
                        <div class="stat-number">${found}</div>
                        <div class="stat-label">Found Items</div>
                    </div>
                    <div class="stat-card ${currentFilter === 'returned' ? 'active' : ''}" onclick="filterItems('returned')">
                        <div class="stat-number">${returned}</div>
                        <div class="stat-label">Returned Items</div>
                    </div>
                </div>
            `;
        }
        
        function filterItems(status) {
            currentFilter = status;
            
            // Update filter button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Filter and display items
            let filteredItems = currentItems;
            if (status !== 'all') {
                filteredItems = currentItems.filter(item => item.status === status);
            }
            
            // Update stats cards active state
            document.querySelectorAll('.stat-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Update stats to reflect current filter
            updateStats();
            displayItems(filteredItems);
        }
        
        function displayItems(items) {
            const tbody = document.getElementById('itemsTableBody');
            
            if (items.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="no-items">
                            <h3>No items found</h3>
                            <p>Try adjusting your filter or check back later.</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = items.map(item => `
                <tr>
                    <td>
                        <img src="${item.image_url || '/api/placeholder/64/64'}" 
                             alt="${item.title}" 
                             style="width: 64px; height: 64px; object-fit: cover; border-radius: 8px;">
                    </td>
                    <td style="font-weight: 500; color: #374151;">${item.title}</td>
                    <td style="color: #6b7280; font-size: 0.875rem;">${truncateText(item.description, 60)}</td>
                    <td>
                        <span class="category-tag">${item.category}</span>
                    </td>
                    <td>
                        <span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span>
                    </td>
                    <td style="color: #6b7280; font-size: 0.875rem;">${item.location_found}</td>
                    <td style="color: #6b7280; font-size: 0.875rem;">${new Date(item.date_found).toLocaleDateString()}</td>
                    <td>
                        <div class="actions">
                            ${item.status !== 'returned' ? `
                                <button class="mark-returned-btn" onclick="markAsReturned('${item.id}')">
                                    Mark Returned
                                </button>
                            ` : ''}
                            <button class="delete-btn" onclick="deleteItem('${item.id}')">
                                Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        async function markAsReturned(itemId) {
            if (!confirm('Mark this item as returned?')) return;
            
            try {
                const response = await fetch(`/api/items/${itemId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status: 'returned',
                        notes: 'Item returned to owner via admin'
                    })
                });
                
                if (response.ok) {
                    loadItems(); // Reload to reflect changes
                    alert('Item marked as returned successfully!');
                } else {
                    alert('Failed to update item status');
                }
            } catch (error) {
                alert('Error updating item: ' + error.message);
            }
        }
        
        async function deleteItem(itemId) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) return;
            
            try {
                const response = await fetch(`/api/items/${itemId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadItems(); // Reload to reflect changes
                    alert('Item deleted successfully!');
                } else {
                    alert('Failed to delete item');
                }
            } catch (error) {
                alert('Error deleting item: ' + error.message);
            }
        }
        
        // Allow login with Enter key
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !document.getElementById('loginForm').classList.contains('hidden')) {
                login();
            }
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(admin_html.encode('utf-8'))

if __name__ == "__main__":
    # Test S3 connection on startup
    print("🔧 Testing S3 connection...")
    if test_s3_connection():
        print("✅ S3 connection successful!")
    else:
        print("⚠️  S3 connection failed - file uploads will not work")
    
    with socketserver.TCPServer(("", PORT), EnhancedRequestHandler) as httpd:
        print(f"\n🚀 Enhanced Lost & Found Campus API Server running at http://localhost:{PORT}")
        print("📱 Frontend should be available at http://localhost:3000")
        print("🔗 API endpoints:")
        print(f"   - GET http://localhost:{PORT}/api/items")
        print(f"   - GET http://localhost:{PORT}/api/items/{{id}}")
        print(f"   - POST http://localhost:{PORT}/api/items (with file upload support)")
        print("📦 Features: S3 file upload, multipart/form-data, JSON support")
        print("\n💡 Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            httpd.shutdown()