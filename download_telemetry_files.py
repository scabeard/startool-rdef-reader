"""
Download all telemetry files from NASA's umbra archive

This script downloads all RDEF files from https://umbra.nascom.nasa.gov/pub/tlm_files/
and organizes them into a structured folder system.
"""

import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")


def download_file(url, local_path, session):
    """
    Download a single file with retry logic.
    
    Args:
        url (str): URL to download from
        local_path (str): Local path to save file
        session (requests.Session): HTTP session for downloads
    """
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading: {url}")
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded: {local_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to download {url} after {max_retries} attempts")
                return False


def get_directory_listing(url, session):
    """
    Get the directory listing from an HTML page.
    
    Args:
        url (str): URL to get directory listing from
        session (requests.Session): HTTP session
        
    Returns:
        list: List of (name, href) tuples for files and directories
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        
        # Find all links in the page
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href != '../':
                name = link.text.strip()
                if not name:
                    name = href
                links.append((name, href))
        
        return links
        
    except Exception as e:
        logger.error(f"Failed to get directory listing for {url}: {e}")
        return []


def download_recursive(base_url, local_base_dir, session, max_depth=3, current_depth=0):
    """
    Recursively download files from the telemetry archive.
    
    Args:
        base_url (str): Base URL to start downloading from
        local_base_dir (str): Local directory to save files
        session (requests.Session): HTTP session
        max_depth (int): Maximum directory depth to traverse
        current_depth (int): Current directory depth
    """
    if current_depth >= max_depth:
        logger.info(f"Reached max depth ({max_depth}), stopping recursion")
        return
    
    logger.info(f"Processing directory: {base_url}")
    
    # Get directory listing
    items = get_directory_listing(base_url, session)
    if not items:
        logger.warning(f"No items found in {base_url}")
        return
    
    for name, href in items:
        item_url = urljoin(base_url, href)
        local_path = os.path.join(local_base_dir, name)
        
        # Check if it's a directory (ends with /) or file
        if href.endswith('/') or name.endswith('/'):
            # It's a directory
            logger.info(f"Found directory: {name}")
            dir_path = local_path.rstrip('/')
            create_directory(dir_path)
            download_recursive(item_url, dir_path, session, max_depth, current_depth + 1)
            
        else:
            # It's a file
            # Only download RDEF files (.REL, .SDU) and related formats
            if name.lower().endswith(('.rel', '.sdu', '.txt', '.doc')):
                logger.info(f"Found file: {name}")
                download_file(item_url, local_path, session)
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
    
    # Create session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'NASA-RDEF-Reader/1.0 (Educational/Research Purpose)'
    })
    
    logger.info(f"Starting download from: {base_url}")
    logger.info(f"Saving to: {local_base_dir}")
    
    try:
        # Start recursive download
        download_recursive(base_url, local_base_dir, session)
        
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
