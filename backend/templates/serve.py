#!/usr/bin/env python3
"""
Simple HTTP server for serving the OAuth test template.

This script serves the HTML template with proper CORS headers
to allow communication with the FastAPI backend.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, parse_qs


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # Handle auth success redirect
        if self.path.startswith('/auth-success'):
            # Parse query parameters and redirect to main page with parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Build redirect URL with parameters
            params = []
            for key, values in query_params.items():
                if values:
                    params.append(f"{key}={values[0]}")
            
            redirect_url = f"/oauth_test.html?{'&'.join(params)}"
            
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()
            return
        
        # Handle login error redirect
        elif self.path.startswith('/login'):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            params = []
            for key, values in query_params.items():
                if values:
                    params.append(f"{key}={values[0]}")
            
            redirect_url = f"/oauth_test.html?{'&'.join(params)}"
            
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()
            return
        
        # Default behavior for other requests
        super().do_GET()
    
    def log_message(self, format, *args):
        """Override to provide better logging"""
        print(f"[{self.date_time_string()}] {format % args}")


def main():
    """Start the HTTP server"""
    port = 3000
    
    # Check if port is provided as argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Change to the templates directory
    template_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(template_dir)
    
    # Start server
    with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Starting OAuth test server...")
        print(f"📂 Serving files from: {template_dir}")
        print(f"🔗 Server running at: http://localhost:{port}")
        print(f"🧪 OAuth test page: http://localhost:{port}/oauth_test.html")
        print(f"")
        print(f"⚙️  Make sure your FastAPI server is running on http://localhost:8000")
        print(f"🔑 Make sure your .env file has FRONTEND_URL=http://localhost:{port}")
        print(f"")
        print(f"Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 Server stopped")


if __name__ == "__main__":
    main() 