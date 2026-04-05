from urllib.parse import urljoin


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


def _extract_image_urls(soup):
    image_urls = []
    seen = set()

    # Primary: target the specific Elementor widget container for the main product image
    for img in soup.select('div[data-id="0a1830f"] img'):
        src = img.get("src") or img.get("data-src")
        if not src or src in seen:
            continue
        seen.add(src)
        image_urls.append(src)

    # Fallback: if nothing found, use class-based filter but restrict to current cuvée
    if not image_urls:
        for img in soup.select("img.wvs-archive-product-image"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue
            if "blanc-de-blancs" not in src.lower():
                continue
            if src in seen:
                continue
            seen.add(src)
            image_urls.append(src)

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

    image_urls = [urljoin(url, img_url) for img_url in _extract_image_urls(soup)]
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