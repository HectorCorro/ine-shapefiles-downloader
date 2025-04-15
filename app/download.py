import os
import requests
from bs4 import BeautifulSoup
import zipfile
from io import BytesIO

def get_shapefile_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)
    zip_links = [link['href'] for link in links if link['href'].endswith('.zip')]
    return zip_links

def download_and_extract_zip(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    response = requests.get(url)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(output_dir)
    print(f"Descargado y extraído: {url}")
