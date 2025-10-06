"""
Terabox URL processor - FIXED FOR ACTUAL API RESPONSE
Uses: https://wdzone-terabox-api.vercel.app/api
"""

import requests
from urllib.parse import quote
from config import LOGGER

def speed_string_to_bytes(size_str):
    """Convert size string to bytes (exactly like anasty17)"""
    size_str = size_str.replace(" ", "").upper()
    
    if "KB" in size_str:
        return float(size_str.replace("KB", "")) * 1024
    elif "MB" in size_str:
        return float(size_str.replace("MB", "")) * 1024 * 1024
    elif "GB" in size_str:
        return float(size_str.replace("GB", "")) * 1024 * 1024 * 1024
    elif "TB" in size_str:
        return float(size_str.replace("TB", "")) * 1024 * 1024 * 1024 * 1024
    else:
        try:
            return float(size_str.replace("B", ""))
        except:
            return 0

def extract_terabox_info(url):
    """
    Extract file info using wdzone-terabox-api - FIXED FOR ACTUAL RESPONSE
    """
    try:
        print(f"🔍 Processing URL: {url}")
        LOGGER.info(f"Processing URL: {url}")
        
        # If it's already a direct file URL, return it
        if "file" in url:
            return url
        
        # Use wdzone-terabox-api
        apiurl = f"https://wdzone-terabox-api.vercel.app/api?url={quote(url)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }
        
        print(f"🌐 API URL: {apiurl}")
        LOGGER.info(f"Making API request to: {apiurl}")
        
        # Make API request
        response = requests.get(apiurl, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status: {response.status_code}")
        
        req = response.json()
        print(f"📄 API Response: {req}")
        LOGGER.info(f"API response: {req}")
        
        # Check for successful response (FIXED FOR ACTUAL API)
        if "✅ Status" in req and req["✅ Status"] == "Success":
            # New API format with emoji keys
            extracted_info = req.get("📜 Extracted Info", [])
        elif "Status" in req and req["Status"] == "Success":
            # Old API format without emojis
            extracted_info = req.get("Extracted Info", [])
        else:
            # Check for error
            if "❌ Status" in req and req["❌ Status"] == "Error":
                error_msg = req.get("📜 Message", "Unknown error")
                raise Exception(f"API Error: {error_msg}")
            elif "Status" in req and req["Status"] == "Error":
                error_msg = req.get("Message", "Unknown error")
                raise Exception(f"API Error: {error_msg}")
            else:
                raise Exception("Invalid API response format")
        
        if not extracted_info:
            raise Exception("No files found")
        
        # Process first file (FIXED FOR ACTUAL KEYS)
        data = extracted_info[0]
        
        # Handle both emoji and non-emoji keys
        filename = data.get("📂 Title") or data.get("Title", "Unknown")
        size_str = data.get("📏 Size") or data.get("Size", "0 B")
        download_url = data.get("🔽 Direct Download Link") or data.get("Direct Download Link", "")
        
        result = {
            'filename': filename,
            'size': speed_string_to_bytes(size_str.replace(" ", "")),
            'download_url': download_url,
            'type': 'file'
        }
        
        print(f"✅ File info extracted: {result}")
        LOGGER.info(f"File extracted: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Terabox extraction error: {e}")
        LOGGER.error(f"Terabox extraction error: {e}")
        raise Exception(f"Failed to process Terabox link: {str(e)}")

def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"
        
