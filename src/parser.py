from urllib.parse import urljoin, urlparse


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


# Helper to provide include patterns for images based on product URL slug
def _image_include_patterns_for_url(url: str) -> list[str]:
    slug = url.rstrip("/").split("/")[-1].lower()

    mapping = {
        "cuvee-royale-brut": ["brut-royal", "brut_royal"],
        "cuvee-royale-brut-nature": ["nature"],
        "cuvee-royale-brut-blanc-de-blancs": ["blanc-de-blancs", "blanc_de_blancs"],
        "cuvee-royale-demi-sec": ["demi-sec", "demi_sec"],
        "cuvee-royale-vintage-2009": ["crv2009", "2009"],
        "cuvee-royale-vintage-2012": ["crv2012", "2012"],
        "cuvee-royale-vintage-2013": ["crv2013", "2013"],
        "cuvee-royale-vintage-2018": ["vintage", "2018"],
        "josephine-2014": ["josephine", "jo2014", "2014"],
        "josephine-2008": ["josephine", "jo2008", "2008"],
        "la-cote-a-bras-2008": ["cab2008", "la-cab", "cote-a-bras", "2008"],
        "la-cote-a-bras-2009": ["cab2009", "cab200920102011", "la-cab", "cote-a-bras", "2009"],
        "la-cote-a-bras-2012": ["cab2012", "la-cab", "cote-a-bras", "2012"],
        "la-cote-a-bras-2013": ["la-cab", "cote-a-bras", "2013"],
        "la-cote-a-bras-2016": ["la-cab", "cote-a-bras", "2016"],
    }

    return mapping.get(slug, [])


def _extract_image_urls(soup, url):
    image_urls = []
    seen = set()
    include_patterns = _image_include_patterns_for_url(url)

    excluded_keywords = [
        "patrimoine",
        "savoir-faire",
        "actu",
        "logo",
        "james-suckling",
        "wine-enthusiast",
        "drink-business",
        "bettane",
        "bernard-burtschy",
        "decanter",
        "dwwa",
        "le-point",
        "transparentes",
        "xavier-lavictoire",
        "magnum-cuvee-200",
        "jeroboam-cuvee-200",
        "le-ciergelot",
        "versionheader",
        "header",
    ]

    og_image = soup.select_one('meta[property="og:image"]')
    if og_image and og_image.get("content"):
        og_image_url = urljoin(url, og_image.get("content"))
        lower_og = og_image_url.lower()
        if not any(keyword in lower_og for keyword in excluded_keywords):
            if not include_patterns or any(pattern in lower_og for pattern in include_patterns):
                seen.add(og_image_url)
                image_urls.append(og_image_url)

    for img in soup.select("img.wvs-archive-product-image, .elementor-widget-image img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        absolute_src = urljoin(url, src)
        lower_src = absolute_src.lower()

        if absolute_src in seen:
            continue
        if "/wp-content/uploads/" not in lower_src:
            continue
        if not lower_src.endswith((".webp", ".png", ".jpg", ".jpeg")):
            continue
        if any(keyword in lower_src for keyword in excluded_keywords):
            continue
        if include_patterns and not any(pattern in lower_src for pattern in include_patterns):
            continue

        seen.add(absolute_src)
        image_urls.append(absolute_src)

    return image_urls


def _extract_datasheet_url(soup):
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        text = _clean_text(link.get_text(" ", strip=True)) or ""
        if ".pdf" in href.lower() or "data sheet" in text.lower():
            return href
    return None


def _extract_key_value_details(soup):
    details = {}

    heading_nodes = soup.select("p.elementor-heading-title")
    for i in range(len(heading_nodes) - 1):
        key = _clean_text(heading_nodes[i].get_text(" ", strip=True))
        value = _clean_text(heading_nodes[i + 1].get_text(" ", strip=True))
        if not key or not value:
            continue

        key_lower = key.lower()
        if key_lower in {
            "chardonnay",
            "pinot noir",
            "pinot meunier",
            "operating temperature",
            "ageing potential",
        }:
            details[key_lower] = value

    for container in soup.select(".elementor-widget-text-editor .elementor-widget-container"):
        children = [child for child in container.find_all(["h5", "h6"], recursive=False)]
        current_key = None
        for child in children:
            tag_name = child.name.lower()
            text = _clean_text(child.get_text(" ", strip=True))
            if not text:
                continue

            if tag_name == "h5":
                current_key = text.lower()
            elif tag_name == "h6" and current_key:
                details[current_key] = text
                current_key = None

    return details


def extract_product_links(soup):
    product_links = []
    seen = set()

    for link in soup.select("a[href]"):
        href = link.get("href", "").strip()
        if not href:
            continue

        absolute_url = urljoin("https://www.josephperrier.com", href)
        parsed = urlparse(absolute_url)
        path = parsed.path.rstrip("/")

        if "/en/champagnes-et-cuvees/" not in path:
            continue

        if path == "/en/champagnes-et-cuvees":
            continue

        relative_part = path.replace("/en/champagnes-et-cuvees/", "", 1).strip("/")
        if not relative_part or "/" in relative_part:
            continue

        normalized_url = f"https://www.josephperrier.com{path}/"
        if normalized_url in seen:
            continue

        seen.add(normalized_url)
        product_links.append(normalized_url)

    return product_links


def parse_product_page(soup, url):
    title = None

    og_title = soup.select_one('meta[property="og:title"]')
    if og_title and og_title.get("content"):
        title = _clean_text(og_title.get("content"))

    if not title:
        page_title = soup.find("title")
        if page_title:
            raw_title = _clean_text(page_title.get_text(" ", strip=True))
            if raw_title:
                title = raw_title.split("|")[0].strip()

    description = None
    og_description = soup.select_one('meta[property="og:description"]')
    if og_description and og_description.get("content"):
        description = _clean_text(og_description.get("content"))

    if not description:
        description_node = soup.select_one(".woocommerce-product-details__short-description, .elementor-widget-text-editor p")
        if description_node:
            description = _clean_text(description_node.get_text(" ", strip=True))

    image_urls = _extract_image_urls(soup, url)
    details = _extract_key_value_details(soup)
    datasheet_url = _extract_datasheet_url(soup)
    if datasheet_url:
        datasheet_url = urljoin(url, datasheet_url)

    grape_parts = []
    for grape in ["chardonnay", "pinot noir", "pinot meunier"]:
        if grape in details:
            grape_parts.append(f"{grape.title()} {details[grape]}")
    grape_varieties = ", ".join(grape_parts) if grape_parts else None

    return {
        "name": title,
        "product_url": url,
        "description": description,
        "images": image_urls,
        "datasheet_url": datasheet_url,
        "grape_varieties": grape_varieties,
        "operating_temperature": details.get("operating temperature"),
        "ageing_potential": details.get("ageing potential"),
        "aging": details.get("aging"),
        "reserve_wines": details.get("reserve wines"),
        "dosage": details.get("dosage"),
        "crus_assembles": details.get("crus assemblés") or details.get("crus assembles"),
    }