import json

INPUT_FILE = "final_upv_data.json"
OUTPUT_FILE = "final_upv_data_classified.json"  

# =====================
# URL CLASSIFICATION
# =====================
def classify_url(url: str) -> str:
    u = url.lower()

    if "about/officials" in u or "official" in u:
        return "officials"
    elif "admission/undergraduate" in u:
        return "admissions_undergraduate"
    elif "admission/graduate" in u:
        return "admissions_graduate"
    elif "admission/high-school" in u:
        return "admissions_highschool"
    elif "admission" in u:
        return "admissions"
    elif "news" in u:
        return "news"
    elif "features" in u:
        return "features"
    elif "events" in u:
        return "events"
    elif "employment" in u:
        return "careers"
    elif "about" in u:
        return "about"
    elif "research" in u:
        return "research"
    elif "upviews" in u or "quarter-issue" in u or "bimonthly-issue" in u:
        return "upviews"
    else:
        return "general"


# =====================
# LOAD
# =====================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} pages from {INPUT_FILE}")

# =====================
# CLASSIFY
# =====================
type_counts = {}

for item in data:
    url = item.get("url", "")
    item["type"] = classify_url(url)

    # Count for summary
    t = item["type"]
    type_counts[t] = type_counts.get(t, 0) + 1

# =====================
# SAVE
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nDone! Updated {len(data)} pages.")
print(f"Saved to {OUTPUT_FILE}\n")

# =====================
# SUMMARY
# =====================
print("Type breakdown:")
for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {t:<30} {count} pages")