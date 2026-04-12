#!/usr/bin/env python3
import json
import re
from pathlib import Path

messages_dir = Path(__file__).parent.parent / "admin_web" / "messages"
src_dir = Path(__file__).parent.parent / "admin_web" / "src"


def load_json(filename):
    with open(messages_dir / filename, encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(messages_dir / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_duplicate_keys(json_obj):
    duplicates = []
    for section, content in json_obj.items():
        if not isinstance(content, dict):
            continue
        keys = list(content.keys())
        seen = {}
        for i, key in enumerate(keys):
            if key in seen:
                duplicates.append({"section": section, "key": key})
            else:
                seen[key] = i
    return duplicates


def sort_json_keys(json_obj):
    result = {}
    for section in sorted(json_obj.keys()):
        result[section] = {}
        for key in sorted(json_obj[section].keys()):
            result[section][key] = json_obj[section][key]
    return result


KNOWN_NS = {
    "common", "dashboard", "nav", "knowledge", "dialogues", "templates",
    "checklists", "users", "departments", "analytics", "invitations",
    "settings", "meetings", "escalations", "auth", "pagination",
}


def get_used_keys():
    """
    Collect all t("...") keys from .tsx files as full "namespace.key" paths.
    Keys already in "namespace.key" format are kept as-is.
    Bare keys (no dot, or unrecognised prefix) fall back to the "common" namespace.
    """
    used = set()

    for tsx_file in src_dir.rglob("*.tsx"):
        content = tsx_file.read_text(encoding="utf-8")
        for match in re.findall(r'\bt\(["\']([^"\']+)["\']', content):
            if "{" in match or len(match) <= 1:
                continue
            dot = match.find(".")
            if dot > 0 and match[:dot] in KNOWN_NS:
                used.add(match)
            elif "." not in match:
                used.add(f"common.{match}")

    return used


def remove_unused_keys(json_obj, unused_keys):
    result = json.loads(json.dumps(json_obj))
    for full_key in unused_keys:
        parts = full_key.split(".")
        if len(parts) == 2:
            section, key = parts
            if section in result and key in result[section]:
                del result[section][key]
    return result


def main():
    en_json = load_json("en.json")
    ru_json = load_json("ru.json")

    print("=== SORTING KEYS ALPHABETICALLY AND REMOVING UNUSED ===")
    sorted_en = sort_json_keys(en_json)
    sorted_ru = sort_json_keys(ru_json)
    print("✓ Initial sort complete")

    print("\n=== CHECKING FOR DUPLICATE KEYS ===")
    en_duplicates = find_duplicate_keys(en_json)
    ru_duplicates = find_duplicate_keys(ru_json)

    if en_duplicates:
        print("DUPLICATES IN EN.JSON:")
        for d in en_duplicates:
            print(f"  - {d['section']}.{d['key']}")
    else:
        print("en.json: No duplicates")

    if ru_duplicates:
        print("DUPLICATES IN RU.JSON:")
        for d in ru_duplicates:
            print(f"  - {d['section']}.{d['key']}")
    else:
        print("ru.json: No duplicates")

    if not en_duplicates and not ru_duplicates:
        print("✓ No duplicate keys found")

    used_keys = get_used_keys()

    missing_en = []
    missing_ru = []

    for full_key in sorted(used_keys):
        ns, _, key = full_key.partition(".")
        if key not in en_json.get(ns, {}):
            missing_en.append(full_key)
        if key not in ru_json.get(ns, {}):
            missing_ru.append(full_key)

    unused_en = []
    unused_ru = []

    for section in en_json.keys():
        for key in en_json[section].keys():
            if f"{section}.{key}" not in used_keys:
                unused_en.append(f"{section}.{key}")

    for section in ru_json.keys():
        for key in ru_json[section].keys():
            if f"{section}.{key}" not in used_keys:
                unused_ru.append(f"{section}.{key}")

    print("\n=== MISSING KEYS IN EN.JSON (used in code but not in JSON) ===")
    if not missing_en:
        print("None!")
    else:
        for k in missing_en:
            print(f"  - {k}")

    print("\n=== MISSING KEYS IN RU.JSON (used in code but not in JSON) ===")
    if not missing_ru:
        print("None!")
    else:
        for k in missing_ru:
            print(f"  - {k}")

    print("\n=== UNUSED KEYS IN EN.JSON (in JSON but not used in code) ===")
    if not unused_en:
        print("None!")
    else:
        for k in unused_en:
            print(f"  - {k}")

    print("\n=== UNUSED KEYS IN RU.JSON (in JSON but not used in code) ===")
    if not unused_ru:
        print("None!")
    else:
        for k in unused_ru:
            print(f"  - {k}")

    clean_en = remove_unused_keys(en_json, unused_en)
    clean_ru = remove_unused_keys(ru_json, unused_ru)

    sorted_clean_en = sort_json_keys(clean_en)
    sorted_clean_ru = sort_json_keys(clean_ru)

    save_json("en.json", sorted_clean_en)
    save_json("ru.json", sorted_clean_ru)

    if unused_en or unused_ru:
        print("\n✓ Removed unused keys from JSON files")

    print("\n=== SUMMARY ===")
    print(f"Unique t() keys used: {len(used_keys)}")
    print(f"Missing in en.json:   {len(missing_en)}")
    print(f"Missing in ru.json:   {len(missing_ru)}")
    print(f"Unused in en.json:    {len(unused_en)}")
    print(f"Unused in ru.json:    {len(unused_ru)}")


if __name__ == "__main__":
    main()
