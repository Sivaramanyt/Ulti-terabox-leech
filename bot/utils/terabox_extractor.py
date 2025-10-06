"""
Terabox URL processor - Supports multiple domains
"""

import requests
from config import LOGGER

def extract_terabox_info(url):
    """
    Extract file info from Terabox URLs
    Supports: terabox.com, teraboxurl.com, terasharelink.com
    """
    try:
        print(f"🔍 Processing URL: {url}")
        LOGGER.info(f"Processing URL: {url}")
        
        # Supported domains
        supported_domains = [
            'terabox.com', 
            'teraboxurl.com', 
            'terasharelink.com',
            '1024tera.com',
            'momerybox.com',
            'tibibox.com',
            '4funbox.co'
        ]
        
        # Check if URL is supported
        is_supported = any(domain in url.lower() for domain in supported_domains)
        if not is_supported:
            raise Exception("URL not supported. Please use Terabox, TeraboxURL, or Terasharelink URLs")
        
        # Extract surl from different formats
        surl = None
        if 'surl=' in url:
            surl = url.split('surl=')[-1].split('&')[0]
        elif '/s/' in url:
            surl = url.split('/s/')[-1].split('?')[0].split('#')[0]
        
        if not surl:
            raise Exception("Could not extract file ID from URL")
        
        print(f"📋 Extracted surl: {surl}")
        LOGGER.info(f"Extracted surl: {surl}")
        
        # Try different API endpoints
        api_endpoints = [
            "https://www.terabox.com/api/shorturlinfo",
            "https://teraboxurl.com/api/shorturlinfo",
            "https://terasharelink.com/api/shorturlinfo"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.terabox.com/',
            'Origin': 'https://www.terabox.com'
        }
        
        params = {
            'shorturl': surl,
            'root': '1'
        }
        
        # Try each API endpoint
        for api_url in api_endpoints:
            try:
                print(f"🌐 Trying API: {api_url}")
                response = requests.get(api_url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('errno') == 0 and data.get('list'):
                        print(f"✅ Success with API: {api_url}")
                        file_list = data.get('list', [])
                        
                        if file_list:
                            file_info = file_list[0]
                            result = {
                                'filename': file_info.get('server_filename', 'Unknown'),
                                'size': file_info.get('size', 0),
                                'download_url': file_info.get('dlink', ''),
                                'type': 'file'
                            }
                            
                            print(f"📁 File found: {result['filename']}")
                            LOGGER.info(f"File extracted: {result}")
                            return result
            
            except Exception as e:
                print(f"❌ API {api_url} failed: {e}")
                continue
        
        # If all APIs failed
        raise Exception("All API endpoints failed. The link might be invalid or expired.")
        
    except Exception as e:
        print(f"❌ Terabox extraction error: {e}")
        LOGGER.error(f"Terabox extraction error: {e}")
        raise Exception(f"Failed to process link: {str(e)}")

def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"
