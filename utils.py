# utils.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import uuid
import copy
import re
import json
import shutil

def fetch_page(url, headers):
    print(f"[INFO] Fetching page: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print("[INFO] Page fetched successfully.")
        return response.text
    except Exception as e:
        print(f"[ERROR] Error fetching page: {url}. Error: {str(e)}")
        return None

def get_image_folder(base_url):
    parsed_url = urlparse(base_url)
    path = parsed_url.path.strip("/")
    if path:
        folder = f"{path.replace('/', '_')}_images"
    else:
        folder = f"{parsed_url.netloc}_images"
    print(f"[INFO] Using images folder: {folder}")
    return folder

def process_images(soup, base_url, headers, images_folder):
    print("[INFO] Processing images...")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"[INFO] Created folder: {images_folder}")
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        absolute_src = urljoin(base_url, src)
        print(f"[INFO] Processing image: {absolute_src}")
        try:
            img_response = requests.get(absolute_src, headers=headers, timeout=30)
            img_response.raise_for_status()
            filename = os.path.basename(urlparse(absolute_src).path)
            if not filename or '.' not in filename:
                filename = f"{uuid.uuid4()}.jpg"
            local_path = os.path.join(images_folder, filename)
            with open(local_path, 'wb') as f:
                f.write(img_response.content)
            print(f"[INFO] Saved image: {local_path}")
            img['src'] = local_path
        except Exception as e:
            print(f"[ERROR] Failed to process image: {absolute_src}. Error: {str(e)}")
            continue
    return soup

def extract_meta(soup, fallback_title):
    print("[INFO] Extracting meta information...")
    meta_og = soup.find("meta", property="og:title")
    meta_name = soup.find("meta", attrs={"name": "title"})
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_title = (meta_og.get("content") or meta_name.get("content")).strip() if (meta_og or meta_name) else fallback_title
    meta_description = meta_desc_tag.get("content").strip() if meta_desc_tag else "Meta description not found"
    print(f"[INFO] Meta title: {meta_title}")
    print(f"[INFO] Meta description: {meta_description}")
    return meta_title, meta_description

def extract_all_meta(soup):
    print("[INFO] Extracting all meta tags...")
    meta_tags = {}
    for meta in soup.find_all("meta"):
        key = meta.get("name") or meta.get("property")
        content = meta.get("content")
        if key and content:
            meta_tags[key] = content.strip()
    print(f"[INFO] Extracted meta tags: {meta_tags}")
    return meta_tags

def clean_content(soup):
    print("[INFO] Cleaning content...")
    for unwanted in soup(['script', 'style']):
        unwanted.decompose()
    allowed_tags = ["p", "a", "ul", "ol", "li"]
    content_soup = copy.deepcopy(soup.body or soup)
    for tag in content_soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            tag.attrs = {}
    content_str = re.sub(r'\s+', ' ', str(content_soup)).strip()
    print("[INFO] Content cleaned.")
    return content_str

def zip_images(images_folder):
    print(f"[INFO] Zipping images in folder: {images_folder}")
    zip_path = shutil.make_archive(images_folder, 'zip', images_folder)
    print(f"[INFO] Images zipped to: {zip_path}")
    return zip_path

def process_url(url, headers):
    print(f"[INFO] Processing URL: {url}")
    html = fetch_page(url, headers)
    if not html:
        print("[ERROR] Failed to fetch HTML, aborting process.")
        return None
    soup = BeautifulSoup(html, "html.parser")
    h1_tag = soup.find("h1")
    page_title = h1_tag.get_text(strip=True) if h1_tag and h1_tag.get_text(strip=True) else (soup.title.get_text(strip=True) if soup.title else "Title not found")
    print(f"[INFO] Page title: {page_title}")
    meta_title, meta_description = extract_meta(soup, page_title)
    meta_tags = extract_all_meta(soup)
    permalink = url
    images_folder = get_image_folder(url)
    soup = process_images(soup, url, headers, images_folder)
    content = clean_content(soup)
    zip_file_path = zip_images(images_folder)
    return {
        "page_title": page_title,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "meta_tags": meta_tags,
        "permalink": permalink,
        "content": content,
        "zip_file_path": zip_file_path
    }

def send_property_with_zip(prop_name, prop_value, zip_file_path, webhook_url):
    payload = {"property": prop_name, "value": prop_value}
    print(f"[INFO] Sending property '{prop_name}' with value '{prop_value}' using zip file: {zip_file_path}")
    try:
        with open(zip_file_path, "rb") as f_zip:
            files = {
                "data": (None, json.dumps(payload, ensure_ascii=False), "application/json"),
                "zip_file": (os.path.basename(zip_file_path), f_zip, "application/zip")
            }
            response = requests.post(webhook_url, files=files, timeout=30)
            print(f"[INFO] Property '{prop_name}' sent. Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error sending property '{prop_name}'. Error: {str(e)}")

def send_all_properties(bundle, webhook_url):
    zip_file_path = bundle.pop("zip_file_path")
    print("[INFO] Sending all properties with the zipped images file...")
    for key, value in bundle.items():
        send_property_with_zip(key, value, zip_file_path, webhook_url)
