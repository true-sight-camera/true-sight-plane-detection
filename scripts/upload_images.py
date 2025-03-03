#!/usr/bin/env python3

'''
Run this script to local storage on the server (temporary solution)
Usage:
    python3 scripts/upload_image.py <path_to_image> [<path_to_image2> ...]
'''

import requests
import sys
import os

# Endpoint URL (adjust host/port as needed)
API_URL = "http://localhost:5000/api/store_image"

def upload_image(file_path: str):
    """
    Reads the file at file_path in binary mode and uploads it
    to the Flask endpoint as the request body.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found - {file_path}")
        return

    with open(file_path, 'rb') as f:
        # Send the file's bytes as the request data
        response = requests.post(API_URL, data=f.read())
    
    if response.status_code == 200:
        print(f"Uploaded {file_path} successfully.")
        print("Response:", response.json())
    else:
        print(f"Failed to upload {file_path}.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

def main():
    """
    Usage: python upload_image.py <path_to_image> [<path_to_image2> ...]
    """
    if len(sys.argv) < 2:
        print("Usage: python upload_image.py <image_path> [<image_path2> ...]")
        sys.exit(1)
    
    # Upload each file provided in the command line arguments
    for file_path in sys.argv[1:]:
        upload_image(file_path)

if __name__ == "__main__":
    main()
