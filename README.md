This solution provides a simple yet effective way to share files. Here's how to use it:

1. Save the code as `file_share.py`

2. Install the required package:
```bash
pip install qrcode pillow
```

3. Run the server:
```bash
python file_share.py --directory /path/to/share --port 8000
```

Key features:
- Works with dynamic IPs (uses your local IP automatically)
- Generates QR code for easy mobile access
- Clean web interface for file browsing
- Direct download links
- No third-party dependencies except for QR code generation
- Shows file sizes and modification times
- Mobile-friendly interface

To make it accessible from outside your network:
1. Set up port forwarding on your router to forward port 8000 (or your chosen port) to your computer's local IP
2. Find your public IP (you can use `curl ifconfig.me` in terminal)
3. Share the URL: `http://your_public_ip:8000`

Security considerations:
- Only share what you intend to share - be careful with the directory you choose
- The server is basic HTTP - don't use it for sensitive files
- Consider implementing basic authentication if needed
- Make sure your firewall settings allow the connection

