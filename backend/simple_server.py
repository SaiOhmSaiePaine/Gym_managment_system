#!/usr/bin/env python3
"""
Simple HTTP server for Lost & Found Campus API
Using only built-in Python libraries for compatibility
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8000

# Mock data
mock_items = [
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

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        """Send CORS headers to allow requests from React app"""
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
    def _send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == '/':
            self._send_json_response({
                "message": "Lost & Found Campus API",
                "version": "1.0.0"
            })
        elif path == '/api/items':
            self._handle_get_items(query_params)
        elif path.startswith('/api/items/'):
            item_id = path.split('/')[-1]
            self._handle_get_item(item_id)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/items':
            self._handle_create_item()
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def _handle_get_items(self, query_params):
        """Handle GET /api/items with filtering and pagination"""
        # Get query parameters
        page = int(query_params.get('page', ['1'])[0])
        search = query_params.get('search', [''])[0]
        category = query_params.get('category', [''])[0]
        status = query_params.get('status', [''])[0]
        per_page = 10
        
        # Filter items
        filtered_items = mock_items.copy()
        
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
        
        response = {
            "items": paginated_items,
            "total": total,
            "page": page,
            "per_page": per_page
        }
        
        self._send_json_response(response)
    
    def _handle_get_item(self, item_id):
        """Handle GET /api/items/{id}"""
        for item in mock_items:
            if item['id'] == item_id:
                self._send_json_response(item)
                return
        
        self._send_json_response({"error": "Item not found"}, 404)
    
    def _handle_create_item(self):
        """Handle POST /api/items"""
        try:
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                item_data = json.loads(post_data.decode('utf-8'))
                
                # Generate a new ID
                new_id = str(len(mock_items) + 1)
                item_data['id'] = new_id
                
                # Add to our mock database
                mock_items.append(item_data)
                
                # Return the created item
                self._send_json_response(item_data, 201)
            else:
                self._send_json_response({"error": "No data provided"}, 400)
                
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"🚀 Lost & Found Campus API Server running at http://localhost:{PORT}")
        print("📱 Frontend should be available at http://localhost:3000")
        print("🔗 API endpoints:")
        print(f"   - GET http://localhost:{PORT}/api/items")
        print(f"   - GET http://localhost:{PORT}/api/items/{{id}}")
        print("\n💡 Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            httpd.shutdown() 