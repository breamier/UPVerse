# pip install requests beautifulsoup4 playwright pymupdf pdfplumber easyocr pillow tqdm
# playwright install

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import fitz  # PyMuPDF
import os
import time
import tempfile

BASE_URL = "https://www.upv.edu.ph/"

#  IMPORTANT PAGES

start_pages = [
"https://www.upv.edu.ph/index.php/employment/computer-maintenance-technologist-i-dic",
"https://www.upv.edu.ph/index.php/employment/computer-maintenance-technologist-iii-dic",
"https://www.upv.edu.ph/index.php/employment/school-credits-evaluator-grad-school",
"https://www.upv.edu.ph/index.php/employment/security-guard-iii-ssf-2",
"https://www.upv.edu.ph/index.php/employment/special-police-major-ssf-2",
"https://www.upv.edu.ph/index.php/employment/university-research-associate-i-ttbdo-3",
"https://www.upv.edu.ph/index.php/employment/university-research-associate-i-ia-2",
"https://www.upv.edu.ph/index.php/employment/administrative-officer-ii-administrative-officer-i-profed",
"https://www.upv.edu.ph/index.php/employment/laboratory-technician-ii-sotech-6",
"https://www.upv.edu.ph/index.php/employment/master-fisherman-i-imfo",
"https://www.upv.edu.ph/index.php/employment/security-officer-iv-ssf",
"https://www.upv.edu.ph/index.php/employment/administrative-assistant-ii-administrative-assistant-osa",
"https://www.upv.edu.ph/index.php/employment/university-extension-specialist-ii-ia-2",
"https://www.upv.edu.ph/index.php/employment/guidance-services-specialist-iii-osa",
"https://www.upv.edu.ph/index.php/employment/administrative-officer-iv-administrative-officer-ii-our",
"https://www.upv.edu.ph/index.php/employment/special-police-major-ssf",
"https://www.upv.edu.ph/index.php/employment/information-systems-analyst-iii-our",
"https://www.upv.edu.ph/index.php/employment/administrative-assistant-ii-clerk-iv-ifpt",
"https://www.upv.edu.ph/index.php/employment/administrative-aide-iii-clerk-i-our",
"https://www.upv.edu.ph/index.php/employment/chief-administrative-officer-supply-officer-v-spso"
]

#  MANUAL PDF LINKS =====================================================

manual_pdfs = [
    # pdf links
]

# SETTINGS =====================================================

MAX_PAGES = 40
MAX_PDF_PAGES = 30
REQUEST_DELAY = 1

visited = set()
documents = []

# REMOVE UNWANTED SECTIONS =====================================================

def remove_unwanted_sections(soup):

    # Remove unwanted tags
    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "noscript",
        "svg",
    ]):
        tag.decompose()

    # Remove unwanted IDs
    remove_ids = [
        "sp-bottom",
        "sp-footer",
        "sp-header",
        "mod-search-searchword",
    ]

    for section_id in remove_ids:

        section = soup.find(id=section_id)

        if section:
            section.decompose()

    # Remove unwanted classes
    remove_classes = [
        "breadcrumb",
        "socials",
        "share-buttons",
        "sidebar",
    ]

    for class_name in remove_classes:

        for section in soup.find_all(class_=class_name):
            section.decompose()


# EXTRACT MAIN CONTENT =====================================================

def extract_main_content(soup):

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(class_="item-page")
        or soup.find(class_="blog")
        or soup.body
    )

    return main_content


# CLEAN TEXT =====================================================

def clean_text(text):

    return " ".join(text.split())


# PDF EXTRACTION =====================================================

def extract_pdf_text(pdf_url):

    try:

        print(f"\nExtracting PDF: {pdf_url}")

        response = requests.get(pdf_url, timeout=15)

        time.sleep(REQUEST_DELAY)

        # Create temporary PDF safely
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(response.content)

            temp_path = temp_file.name

        doc = fitz.open(temp_path)

        # Skip massive PDFs
        if len(doc) > MAX_PDF_PAGES:

            print(
                f"Skipping huge PDF "
                f"({len(doc)} pages)"
            )

            doc.close()

            os.remove(temp_path)

            return ""

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        os.remove(temp_path)

        return clean_text(text)

    except Exception as e:

        print(f"Failed PDF extraction: {pdf_url}")
        print(e)

        return ""


# START CRAWLING =====================================================

to_visit = start_pages.copy()

while to_visit and len(visited) < MAX_PAGES:

    url = to_visit.pop(0)

    if url in visited:
        continue

    visited.add(url)

    print(f"\nScraping: {url}")

    try:

        response = requests.get(url, timeout=10)

        time.sleep(REQUEST_DELAY)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove junk
        remove_unwanted_sections(soup)

        # Get main content only
        main_content = extract_main_content(soup)

        if not main_content:
            continue

        text = main_content.get_text(
            separator=" "
        )

        clean_page_text = clean_text(text)

        title = (
            soup.title.string.strip()
            if soup.title
            else "No Title"
        )

        
        # SAVE WEBPAGE =====================================================
        

        documents.append({
            "url": url,
            "title": title,
            "content": clean_page_text,
            "type": "webpage"
        })

        
        # FIND LINKS =====================================================
        

        # for a in soup.find_all("a", href=True):

        #     href = a["href"]

        #     full_url = urljoin(
        #         BASE_URL,
        #         href
        #     )

        #     # Remove URL fragments
        #     full_url = full_url.split("#")[0]

        #     # Only crawl UPV pages
        #     if "upv.edu.ph" not in full_url:
        #         continue

        #     # Skip social media
        #     if any(social in full_url for social in [
        #         "facebook.com",
        #         "twitter.com",
        #         "x.com",
        #         "instagram.com",
        #         "youtube.com",
        #         "linkedin.com"
        #     ]):
        #         continue

        #     # HANDLE PDFs =====================================================

        #     if full_url.endswith(".pdf"):

        #         if full_url not in visited:

        #             visited.add(full_url)

        #             pdf_text = extract_pdf_text(
        #                 full_url
        #             )

        #             if pdf_text:

        #                 documents.append({
        #                     "url": full_url,
        #                     "title": "PDF Document",
        #                     "content": pdf_text,
        #                     "type": "pdf"
        #                 })

        #         continue

        #     # SKIP OTHER FILE TYPES =====================================================

        #     if full_url.endswith((
        #         ".jpg",
        #         ".jpeg",
        #         ".png",
        #         ".gif",
        #         ".webp",
        #         ".doc",
        #         ".docx",
        #         ".xls",
        #         ".xlsx",
        #         ".ppt",
        #         ".pptx",
        #         ".zip"
        #     )):
        #         continue


        #     # ADD TO CRAWL QUEUE =====================================================


        #     if (
        #         full_url not in visited
        #         and full_url not in to_visit
        #     ):
        #         to_visit.append(full_url)

    except Exception as e:

        print(f"\nError scraping: {url}")
        print(e)



# PDF EXTRACTION =====================================================

for pdf_url in manual_pdfs:

    if pdf_url in visited:
        continue

    visited.add(pdf_url)

    pdf_text = extract_pdf_text(pdf_url)

    if pdf_text:

        documents.append({
            "url": pdf_url,
            "title": "Manual PDF",
            "content": pdf_text,
            "type": "pdf"
        })



# SAVE JSON =====================================================

with open(
    "upv_data.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        documents,
        f,
        indent=2,
        ensure_ascii=False
    )





print("\n====================================")
print("SCRAPING COMPLETE")
print(f"Documents collected: {len(documents)}")
print("Saved to upv_data.json")
