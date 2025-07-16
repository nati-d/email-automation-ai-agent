#!/usr/bin/env python3
"""
Test Network Connectivity

This script tests network connectivity to SMTP servers to diagnose connection issues.
"""

import socket
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_port_connectivity(host, port, timeout=10):
    """Test if a port is reachable"""
    try:
        print(f"🔍 Testing connection to {host}:{port}...")
        start_time = time.time()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        elapsed = time.time() - start_time
        
        if result == 0:
            print(f"   ✅ Connection successful ({elapsed:.2f}s)")
            return True
        else:
            print(f"   ❌ Connection failed (error code: {result})")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def test_dns_resolution(host):
    """Test DNS resolution"""
    try:
        print(f"🔍 Testing DNS resolution for {host}...")
        ip = socket.gethostbyname(host)
        print(f"   ✅ Resolved to {ip}")
        return True
    except Exception as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False

def test_smtp_servers():
    """Test connectivity to common SMTP servers"""
    print("🌐 Network Connectivity Test")
    print("=" * 50)
    
    # Get current SMTP settings
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    print(f"📧 Current SMTP Settings:")
    print(f"   Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    print()
    
    # Test DNS resolution
    dns_ok = test_dns_resolution(smtp_server)
    print()
    
    if not dns_ok:
        print("❌ DNS resolution failed. Check your internet connection.")
        return
    
    # Test current SMTP server
    print("📧 Testing current SMTP server...")
    current_ok = test_port_connectivity(smtp_server, smtp_port)
    print()
    
    # Test alternative SMTP servers
    print("🔄 Testing alternative SMTP servers...")
    
    smtp_servers = [
        ("smtp.gmail.com", 587),
        ("smtp.gmail.com", 465),
        ("smtp-mail.outlook.com", 587),
        ("smtp.mail.yahoo.com", 587),
        ("8.8.8.8", 53),  # Google DNS - should always work
    ]
    
    results = []
    for server, port in smtp_servers:
        if server != smtp_server or port != smtp_port:
            result = test_port_connectivity(server, port, timeout=5)
            results.append((server, port, result))
            time.sleep(1)  # Small delay between tests
    
    print()
    print("📊 Test Results Summary:")
    print("=" * 30)
    
    if current_ok:
        print(f"✅ Current SMTP server ({smtp_server}:{smtp_port}) is reachable")
    else:
        print(f"❌ Current SMTP server ({smtp_server}:{smtp_port}) is not reachable")
    
    print()
    print("Alternative servers:")
    for server, port, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {server}:{port}")
    
    print()
    if not current_ok:
        print("🔧 Troubleshooting Suggestions:")
        print("   1. Check Windows Firewall settings")
        print("   2. Try a different SMTP port (465 instead of 587)")
        print("   3. Check if your antivirus is blocking connections")
        print("   4. Try using a different network (mobile hotspot)")
        print("   5. Check if your ISP is blocking SMTP ports")
    else:
        print("✅ Network connectivity looks good!")
        print("   The issue might be with SMTP authentication or configuration.")

def test_local_network():
    """Test basic internet connectivity"""
    print("🌐 Testing basic internet connectivity...")
    
    # Test Google DNS
    google_ok = test_port_connectivity("8.8.8.8", 53, timeout=5)
    
    # Test Google.com
    google_web_ok = test_port_connectivity("google.com", 80, timeout=5)
    
    print()
    if google_ok and google_web_ok:
        print("✅ Basic internet connectivity is working")
    else:
        print("❌ Basic internet connectivity issues detected")
        print("   Check your network connection and DNS settings")

def main():
    """Main function"""
    print("🚀 Network Connectivity Test for Email Agent API")
    print("=" * 60)
    
    # Test basic connectivity first
    test_local_network()
    print()
    
    # Test SMTP servers
    test_smtp_servers()
    
    print()
    print("💡 If SMTP connections are failing but internet works:")
    print("   - Try using port 465 with SSL instead of port 587 with TLS")
    print("   - Check Windows Firewall settings")
    print("   - Temporarily disable antivirus software")
    print("   - Try using a different network (mobile hotspot)")

if __name__ == "__main__":
    main() 