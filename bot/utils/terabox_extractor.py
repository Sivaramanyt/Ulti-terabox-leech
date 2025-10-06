"""
Terabox URL processor - Using anasty17's exact method
API: https://wdzone-terabox-api.vercel.app/api
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
    Extract file info from Terabox URLs - ANASTY17's EXACT METHOD
    Uses: https://wdzone-terabox-api.vercel.app/api
    """
    try:
        print(f"🔍 Processing URL: {url}")
        LOGGER.info(f"Processing URL: {url}")
        
        # If it's already a direct file URL, return it
        if "file" in url:
            return url
        
        # Use anasty17's exact API
        apiurl = f"https://wdzone-terabox-api.vercel.app/api?url={quote(url)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }
        
        print(f"🌐 Using API: {apiurl}")
        LOGGER.info(f"Making API request to: {apiurl}")
        
        # Make API request (exactly like anasty17)
        response = requests.get(apiurl, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status: {response.status_code}")
        
        req = response.json()
        print(f"📄 API Response: {req}")
        LOGGER.info(f"API response: {req}")
        
        # Check for successful response (exactly like anasty17)
        if "Status" not in req:
            raise Exception("File not found!")
        
        if req.get("Status") == "Error":
            error_msg = req.get("Message", "Unknown error")
            raise Exception(f"API Error: {error_msg}")
        
        # Extract file information (exactly like anasty17)
        if "Extracted Info" not in req:
            raise Exception("No file information found in API response")
        
        extracted_info = req["Extracted Info"]
        if not extracted_info:
            raise Exception("No files found")
        
        # Process first file (like anasty17 for single files)
        data = extracted_info[0]
        
        result = {
            'filename': data["Title"],
            'size': speed_string_to_bytes(data["Size"].replace(" ", "")),
            'download_url': data["Direct Download Link"],
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
        
