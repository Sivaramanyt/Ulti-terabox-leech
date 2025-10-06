"""
Terabox Direct Link Generator - Optimized Version
Memory efficient for free tier hosting
"""

from requests import get
from json import loads
from urllib.parse import urlparse
import re

class DirectDownloadLinkException(Exception):
    """Custom exception for direct download link errors"""
    pass

def terabox(url):
    """
    Extract direct download links from Terabox URLs
    Supports both single files and folders
    """
    
    if 'terabox.com' not in url:
        raise DirectDownloadLinkException("ERROR: Invalid Terabox URL")
    
    try:
        # Extract surl from different URL formats
        if 'surl=' in url:
            surl = url.split('surl=')[-1].split('&')[0]
        elif '/s/' in url:
            surl = url.split('/s/')[-1].split('?')[0]
        else:
            raise DirectDownloadLinkException("ERROR: Cannot extract surl from URL")
        
        # API endpoint
        api_url = "https://www.terabox.com/api/shorturlinfo"
        
        # Headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.terabox.com/',
            'Origin': 'https://www.terabox.com'
        }
        
        # Parameters
        params = {
            'shorturl': surl,
            'root': '1'
        }
        
        # Make request
        response = get(api_url, params=params, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise DirectDownloadLinkException(f"ERROR: HTTP {response.status_code}")
        
        try:
            data = response.json()
        except:
            raise DirectDownloadLinkException("ERROR: Invalid JSON response")
        
        # Check response
        if data.get('errno') != 0:
            error_msg = data.get('errmsg', 'Unknown error')
            raise DirectDownloadLinkException(f"ERROR: {error_msg}")
        
        file_list = data.get('list', [])
        if not file_list:
            raise DirectDownloadLinkException("ERROR: No files found")
        
        # Return single file info
        if len(file_list) == 1:
            file_info = file_list[0]
            return {
                'filename': file_info.get('server_filename', 'Unknown'),
                'size': file_info.get('size', 0),
                'download_url': file_info.get('dlink', ''),
                'type': 'file'
            }
        
        # Multiple files
        else:
            contents = []
            total_size = 0
            
            for file_info in file_list:
                if file_info.get('dlink'):
                    contents.append({
                        'filename': file_info.get('server_filename', ''),
                        'size': file_info.get('size', 0),
                        'download_url': file_info.get('dlink', ''),
                        'path': file_info.get('path', '')
                    })
                    total_size += file_info.get('size', 0)
            
            return {
                'contents': contents,
                'total_size': total_size,
                'type': 'folder'
            }
            
    except DirectDownloadLinkException:
        raise
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")
