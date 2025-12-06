"""
Simple download script for NASA telemetry files

This script downloads files from the NASA umbra archive without external dependencies.
"""

import os
import re
import urllib.request
import urllib.parse
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")


def get_directory_listing(url):
    """
    Get directory listing by parsing HTML.
    
    Args:
        url (str): URL to get directory listing from
        
    Returns:
        list: List of (name, href) tuples for files and directories
    """
    try:
        logger.info(f"Fetching directory listing: {url}")
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Simple regex to find links
        links = []
        # Look for href="..." patterns
        href_pattern = r'href="([^"]*)"'
        matches = re.findall(href_pattern, html)
        
        for href in matches:
            if href and href != '../':
                # Extract name from href or find it in the HTML
                name = href
                # Try to find the text between <a href="...">text</a>
                link_pattern = f'href="{re.escape(href)}"[^>]*>([^<]*)</a>'
                text_matches = re.findall(link_pattern, html)
                if text_matches:
                    name = text_matches[0].strip()
                if not name:
                    name = href
                
                links.append((name, href))
        
        logger.info(f"Found {len(links)} items in {url}")
        return links
        
    except Exception as e:
        logger.error(f"Failed to get directory listing for {url}: {e}")
        return []


def download_file(url, local_path):
    """
    Download a single file.
    
    Args:
        url (str): URL to download from
        local_path (str): Local path to save file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading: {url}")
        
        # Set up request with headers
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'NASA-RDEF-Reader/1.0 (Educational/Research Purpose)')
        
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        
        # Save the file
        with open(local_path, 'wb') as f:
            f.write(data)
        
        logger.info(f"Successfully downloaded: {local_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False


def download_recursive(base_url, local_base_dir, max_depth=3, current_depth=0):
    """
    Recursively download files from the telemetry archive.
    
    Args:
        base_url (str): Base URL to start downloading from
        local_base_dir (str): Local directory to save files
        max_depth (int): Maximum directory depth to traverse
        current_depth (int): Current directory depth
    """
    if current_depth >= max_depth:
        logger.info(f"Reached max depth ({max_depth}), stopping recursion")
        return
    
    logger.info(f"Processing directory: {base_url}")
    
    # Get directory listing
    items = get_directory_listing(base_url)
    if not items:
        logger.warning(f"No items found in {base_url}")
        return
    
    for name, href in items:
        item_url = urllib.parse.urljoin(base_url, href)
        local_path = os.path.join(local_base_dir, name)
        
        # Check if it's a directory (ends with /) or file
        if href.endswith('/') or name.endswith('/'):
            # It's a directory
            logger.info(f"Found directory: {name}")
            dir_path = local_path.rstrip('/')
            create_directory(dir_path)
            download_recursive(item_url, dir_path, max_depth, current_depth + 1)
            
        else:
            # It's a file
            # Only download RDEF files (.REL, .SDU) and related formats
            if name.lower().endswith(('.rel', '.sdu', '.txt', '.doc')):
                logger.info(f"Found file: {name}")
                if download_file(item_url, local_path):
                    # Be respectful to the server
                    time.sleep(1)
            else:
                logger.debug(f"Skipping file: {name}")


def main():
    """Main function to download all telemetry files."""
    base_url = "https://umbra.nascom.nasa.gov/pub/tlm_files/"
    local_base_dir = "nasa_telemetry_archive"
    
    # Create base directory
    create_directory(local_base_dir)
    
    logger.info(f"Starting download from: {base_url}")
    logger.info(f"Saving to: {local_base_dir}")
    
    try:
        # Start recursive download
        download_recursive(base_url, local_base_dir)
        
        logger.info("Download completed!")
        
        # Show summary
        total_files = sum(len(files) for _, _, files in os.walk(local_base_dir))
        logger.info(f"Total files downloaded: {total_files}")
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Download failed: {e}")


if __name__ == "__main__":
    main()
