from src.config import BASE_URL, PRODUCT_URLS, WINERY_PAGES
from src.db import (
    create_tables,
    insert_winery,
    update_winery_content,
    insert_product,
    insert_media,
)
from src.scraper import get_soup
from src.parser import parse_winery_page, parse_product_page


PAGE_TYPE_TO_FIELD = {
    "history": "history_text",
    "family-spirit": "family_spirit_text",
    "vineyard": "vineyard_text",
    "vine-to-wine": "vine_to_wine_text",
    "cellars": "cellar_text",
    "commitment": "commitment_text",
}


def main():
    # 1. create tables
    create_tables()
    # 2. insert winery and get winery_id
    winery_id = insert_winery("Joseph Perrier", BASE_URL)

    # 3. for each winery page, parse content and update winery record
    winery_data = {
        "history_text": None,
        "family_spirit_text": None,
        "vineyard_text": None,
        "vine_to_wine_text": None,
        "cellar_text": None,
        "commitment_text": None,
    }

    print(f"Starting winery-level ingestion for {len(WINERY_PAGES)} pages...")

    # 4. for each product page, parse content and insert product record linked to winery
    for page_type, page_url in WINERY_PAGES.items():
        print(f"Processing winery page: {page_type} -> {page_url}")
        soup = get_soup(page_url)
        page_data = parse_winery_page(soup, page_url, page_type)

        target_field = PAGE_TYPE_TO_FIELD.get(page_type)
        if target_field:
            winery_data[target_field] = page_data.get("page_text")

        if page_type == "family-spirit" and page_data.get("page_text"):
            winery_data["summary_text"] = page_data.get("page_text")

        for image_url in page_data.get("image_urls", []):
            insert_media(
                "image",
                image_url,
                source_page_url=page_data["source_url"],
                winery_id=winery_id,
            )

        for video_url in page_data.get("video_urls", []):
            insert_media(
                "video",
                video_url,
                source_page_url=page_data["source_url"],
                winery_id=winery_id,
            )

    # 5. after processing all winery pages, update winery record with parsed content
    update_winery_content(winery_id, winery_data)

    print(f"Starting product-level ingestion for {len(PRODUCT_URLS)} product pages...")

    # 6. for each product page, parse content and insert product record linked to winery
    for product_url in PRODUCT_URLS:
        print(f"Processing product page: {product_url}")
        soup = get_soup(product_url)
        product_data = parse_product_page(soup, product_url)

        product_id = insert_product(winery_id, product_data)

        for image_url in product_data["images"]:
            insert_media(
                "image",
                image_url,
                source_page_url=product_data["product_url"],
                product_id=product_id,
            )

    print("Ingestion complete.")


if __name__ == "__main__":
    main()