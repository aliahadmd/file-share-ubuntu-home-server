#!/usr/bin/env python3
import http.server
import socketserver
import os
import argparse
import urllib.parse
import socket
import qrcode
from pathlib import Path
import sys
from datetime import datetime, timedelta
import json

class FileShareHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)
        
    def do_GET(self):
        # Decode URL-encoded path
        parsed_path = urllib.parse.unquote(self.path)
        
        # Handle root path
        if parsed_path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Generate file listing with direct download links
            content = self.generate_directory_listing()
            self.wfile.write(content.encode())
            return
            
        # Handle file downloads
        try:
            return super().do_GET()
        except Exception as e:
            self.send_error(404, f"File not found: {parsed_path}")
            
    def generate_directory_listing(self):
        """Generate an HTML directory listing with improved styling and functionality."""
        path = self.translate_path(self.path)
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Share Directory</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .file-list { list-style: none; padding: 0; }
                .file-item {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .file-item:hover { background-color: #f5f5f5; }
                .file-link {
                    text-decoration: none;
                    color: #2196F3;
                }
                .file-info {
                    color: #666;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Files Available for Download</h2>
                <ul class="file-list">
        """
        
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "Directory not found")
            return
            
        for name in sorted(file_list):
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            # Skip hidden files
            if name.startswith('.'):
                continue
                
            # Get file information
            file_size = os.path.getsize(fullname)
            mod_time = datetime.fromtimestamp(os.path.getmtime(fullname))
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
                
            html += f"""
                <li class="file-item">
                    <a href="{urllib.parse.quote(linkname)}" class="file-link">{displayname}</a>
                    <span class="file-info">
                        {size_str} | {mod_time.strftime('%Y-%m-%d %H:%M:%S')}
                    </span>
                </li>
            """
            
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        return html

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate a QR code for the given URL."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    qr_filename = "share_link_qr.png"
    qr.make_image(fill_color="black", back_color="white").save(qr_filename)
    return qr_filename

def main():
    parser = argparse.ArgumentParser(description='Simple File Sharing Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
    parser.add_argument('--directory', type=str, default='.', help='Directory to share')
    args = parser.parse_args()
    
    # Ensure the directory exists
    share_dir = os.path.abspath(args.directory)
    if not os.path.exists(share_dir):
        print(f"Error: Directory '{share_dir}' does not exist")
        sys.exit(1)
        
    # Set up the server
    handler = lambda *args: FileShareHandler(*args, directory=share_dir)
    
    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            local_ip = get_local_ip()
            share_url = f"http://{local_ip}:{args.port}"
            
            # Generate QR code
            qr_file = generate_qr_code(share_url)
            
            print(f"\n🚀 File Share Server is running!")
            print(f"📂 Sharing directory: {share_dir}")
            print(f"🔗 Access your files at: {share_url}")
            print(f"📱 QR Code generated: {qr_file}")
            print("\nPress Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n⛔ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()