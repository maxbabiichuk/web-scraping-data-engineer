from bs4 import BeautifulSoup
import re
from langdetect import detect, DetectorFactory
from typing import List, Dict
import yaml
import dateparser

PATTERN_AD_LIBRARY_ID = r"Ідентифікатор бібліотеки:\s*(.*)"
PATTERN_PUBLISHED_DATE = r"Початок показу:(.*)р."
PATTERN_AD_CREATIVE_BODY = "Реклама"

# To ensure consistent results, you can set the seed.
DetectorFactory.seed = 0
config = yaml.safe_load(open("schema.yaml"))
canonical_schema = config["canonical_schema"]
field_mapping = config["field_mapping"]


def get_canonical_data(html_content: str, locale: str) -> List[Dict]:
    all_records = get_data_from_html(html_content)
    canonical_data = []
    seen = set()

    for record in all_records:
        mapped = map_to_canonical(record, locale)
        key = tuple(mapped.get(field) for field in canonical_schema.keys())
        if key not in seen:
            seen.add(key)
        canonical_data.append(mapped)

    print("Data transformed to canonical format")
    return canonical_data


def get_data_from_html(html_content: str) -> List[Dict]:
    result = []
    soup = BeautifulSoup(html_content, "html.parser")
    for content in soup.contents:
        result.append(parse_html_element(content))
    return result


def parse_html_element(element) -> Dict:
    result = dict()
    # Find all <br> tags and replace them with a space
    for br in element.find_all("br"):
        br.replace_with("******")
    txt = element.get_text(separator="\n")

    match = re.search(PATTERN_AD_LIBRARY_ID, txt)
    if match:
        result["ad_library_id"] = match.group(1).strip()

    match = re.search(PATTERN_PUBLISHED_DATE, txt)
    if match:
        # runtime_locale = locale
        # date_obj = dateparser.parse(result, languages=[runtime_locale])
        result["published_date"] = match.group(1).strip()

    # Find all 'img' tags
    img_tags = element.find_all("img")
    # Iterate through the list of 'img' tags and print their 'src' attribute
    image_exists = False
    if img_tags:
        for img in img_tags:
            # src = img.get("src")
            alt = img.get("alt", "No alt attribute")
            # print(f"  - SRC: {src}, ALT: {alt}")
            if len(alt) > 0 and alt in txt:
                # print(f"advertiser_name: {alt}")
                result["advertiser_name"] = alt
            else:
                image_exists = True

    # Find all 'video' tags
    video_tags = element.find_all("video")
    if image_exists and video_tags:
        result["media_type"] = "both"
    elif image_exists:
        result["media_type"] = "image-only"
    elif video_tags:
        result["media_type"] = "video-only"
    else:
        result["media_type"] = "none"

    ad_creative_body = get_lines_after_ad(txt)
    result["ad_creative_body"] = ad_creative_body
    result["ad_creative_body_lang"] = infer_language_from_ad(ad_creative_body)

    return result


def get_lines_after_ad(text: str) -> str:
    lines = text.splitlines()
    result = []
    capture = False
    expect_separator = False

    for line in lines:
        clean = line.strip()

        if capture:
            if not clean:
                break
            if expect_separator:
                if set(clean) == {"*"}:
                    expect_separator = False
                    continue
                else:
                    break
            else:
                if set(clean) == {"*"}:
                    break
                result.append(clean)
                expect_separator = True
        if clean == PATTERN_AD_CREATIVE_BODY:
            capture = True

    return " ".join(result)


def infer_language_from_ad(ad_text: str) -> str:
    try:
        language_code = detect(ad_text)
        return language_code
    except Exception as e:
        # Handle cases where the text is too short or has no recognizable language.
        return None


def parse_date(value, locale):
    if not value:
        return None
    try:
        return dateparser.parse(value, languages=[locale])
    except:
        # raise (f"Failed to parse date: {value}")
        return None


def map_to_canonical(record, locale="en"):
    canonical = {}
    for field, types in canonical_schema.items():
        value = None
        for alt in field_mapping[field]:
            if alt in record and record[alt] not in [None, ""]:
                value = record[alt]
                break
        if types == "string":
            canonical[field] = str(value).strip() if value else None
        elif types == "datetime":
            canonical[field] = parse_date(value, locale)
        else:
            canonical[field] = None
    return canonical
