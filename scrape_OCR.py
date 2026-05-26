# =====================================================
# OCR Webpage Scraper for UPVerse
# =====================================================
# PURPOSE:
# Extract OCR text from webpage images/posters
# and save them in your existing JSON format.
#
# INSTALL:
# pip install requests beautifulsoup4 playwright easyocr pillow numpy
# playwright install
#
# OUTPUT FORMAT:
# {
#   "url": "...",
#   "title": "...",
#   "content": "... OCR INCLUDED ...",
#   "type": "webpage"
# }
# =====================================================

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import easyocr
import numpy as np
import io
import json
import re
import time

# =====================================================
# CONFIG
# =====================================================

START_URLS = [
"https://www.upv.edu.ph/index.php/announcements/call-for-nominations-for-the-next-chairperson-of-the-department-of-chemistry",
"https://www.upv.edu.ph/index.php/events/2020-upv-alumni-zoomcoming-events`",
"https://www.upv.edu.ph/index.php/events/women-s-month-2020",
"https://www.upv.edu.ph/index.php/events/73rd-anniversary-of-the-up-presence-in-iloilo",
"https://www.upv.edu.ph/index.php/events/arts-month-2020",
"https://www.upv.edu.ph/index.php/events/upv-celebrates-pakua-2019",
"https://www.upv.edu.ph/index.php/events/the-5th-international-conference-on-fisheries-and-aquatic-sciences",
"https://www.upv.edu.ph/index.php/events/event-2019-graduate-research-conference-2",
"https://www.upv.edu.ph/index.php/announcements/call-for-nomination-for-the-next-chair-of-the-pe-department",
"https://www.upv.edu.ph/index.php/announcements/notice-of-auction-sale",
"https://www.upv.edu.ph/index.php/announcements?start=200",
"https://www.upv.edu.ph/index.php/announcements/search-for-the-next-cas-dean-2024",
"https://www.upv.edu.ph/index.php/announcements/congratulations-to-the-winners-of-the-2023-literature-awards",
"https://www.upv.edu.ph/index.php/announcements/call-for-nominations-for-the-next-dean-of-the-college-of-management-2",
"https://www.upv.edu.ph/index.php/announcements/webinars-for-up-staff-november-2021",
"https://www.upv.edu.ph/index.php/announcements/immediate-liquidation-of-outstanding-cash-advances-2",
"https://www.upv.edu.ph/index.php/announcements/bus-schedule-for-paskua-2025",
"https://www.upv.edu.ph/index.php/announcements/call-for-nomination-for-the-director-of-the-office-of-continuing-education-and-pahinungod"
]

OUTPUT_FILE = "upv_ocr_pages.json"

REQUEST_DELAY = 1

MIN_IMAGE_SIZE = 300


# OCR =====================================================

print("Loading OCR model...")

reader = easyocr.Reader(['en'], gpu=False)



# HELPERS =====================================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()




# PLAYWRIGHT HTML =====================================================


def get_rendered_html(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(url, timeout=60000)

        page.wait_for_load_state("networkidle")

        html = page.content()

        browser.close()

        return html



# OCR IMAGE =====================================================

def extract_image_ocr(img_url):

    try:

        response = requests.get(img_url, timeout=20)

        image = Image.open(
            io.BytesIO(response.content)
        )

        width, height = image.size

        # Skip tiny images/icons/logos
        if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
            return ""

        result = reader.readtext(
            np.array(image),
            detail=0
        )

        text = "\n".join(result)

        return clean_text(text)

    except Exception as e:

        print(f"Failed OCR: {img_url}")
        print(e)

        return ""



# MAIN =====================================================

documents = []

for url in START_URLS:

    print("=" * 60)
    print(f"Scraping: {url}")
    print("=" * 60)

    try:

        html = get_rendered_html(url)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        
        # TITLE

        title = (
            soup.title.string.strip()
            if soup.title
            else "No Title"
        )

        
        # MAIN CONTENT
    

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(class_="item-page")
            or soup.body
        )

        page_text = ""

        if main_content:

            page_text = main_content.get_text(
                separator=" "
            )

        page_text = clean_text(page_text)

    
        # IMAGE OCR
    

        ocr_texts = []

        images = soup.find_all("img")

        print(f"Found {len(images)} images")

        for img in images:

            src = img.get("src")

            if not src:
                continue

            img_url = urljoin(url, src)

            print(f"OCR image: {img_url}")

            ocr_text = extract_image_ocr(
                img_url
            )

            if ocr_text:

                ocr_texts.append(ocr_text)

            time.sleep(REQUEST_DELAY)

        combined_ocr = "\n".join(ocr_texts)

        
        # FINAL CONTENT

        final_content = page_text

        if combined_ocr:

            final_content += (
                "\n\n[IMAGE OCR]\n"
                + combined_ocr
            )

        # SAVE FORMAT

        documents.append({
            "url": url,
            "title": title,
            "content": final_content,
            "type": "webpage"
        })

    except Exception as e:

        print(f"Error scraping: {url}")
        print(e)


# SAVE JSON

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        documents,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n" + "=" * 60)
print("OCR SCRAPING COMPLETE")
print("=" * 60)
print(f"Pages saved: {len(documents)}")
print(f"Output file: {OUTPUT_FILE}")
print("=" * 60)