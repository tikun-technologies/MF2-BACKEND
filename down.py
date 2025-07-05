import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Step 1: Fetch the web page
url = "https://www.olaelectric.com/motorcycles"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Extract image and video URLs
image_urls = [urljoin(url, img['src']) for img in soup.find_all('img') if img.get('src')]
video_urls = []

for tag in soup.find_all(['video', 'source']):
    for attr in ['src', 'data-src', 'data-video']:
        if tag.get(attr):
            video_urls.append(urljoin(url, tag[attr]))

# Step 3: Create folders
os.makedirs("content/images", exist_ok=True)
os.makedirs("content/videos", exist_ok=True)

# Step 4: Download assets
def download_files(urls, dest_folder):
    for file_url in urls:
        try:
            filename = os.path.basename(urlparse(file_url).path)
            if not filename:
                continue
            filepath = os.path.join(dest_folder, filename)
            print(f"Downloading {file_url} → {filepath}")
            r = requests.get(file_url, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        except Exception as e:
            print(f"❌ Failed to download {file_url}: {e}")

download_files(image_urls, "content/images")
download_files(video_urls, "content/videos")
