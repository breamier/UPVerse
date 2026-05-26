import json

OLD_FILE = "final_upv_data.json"
NEW_FILE = "empty.json"

OUTPUT_FILE = "test.json"

# LOAD FILES


with open(OLD_FILE, "r", encoding="utf-8") as f:
    old_data = json.load(f)

with open(NEW_FILE, "r", encoding="utf-8") as f:
    new_data = json.load(f)

# CREATE URL MAP

merged = {}

# add old data first
for item in old_data:

    url = item.get("url")

    if url:
        merged[url] = item

# replace/update with new data
for item in new_data:

    url = item.get("url")

    if url:
        merged[url] = item


# FINAL LIST =====================================================


final_data = list(merged.values())


# SAVE


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_data,
        f,
        indent=2,
        ensure_ascii=False
    )

# =====================================================
# SUMMARY
# =====================================================

print("=" * 50)
print("MERGE COMPLETE")
print("=" * 50)

print(f"Old entries : {len(old_data)}")
print(f"New entries : {len(new_data)}")
print(f"Final total : {len(final_data)}")

print(f"\nSaved to: {OUTPUT_FILE}")