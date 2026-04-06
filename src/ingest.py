from src.config import BASE_URL, PRODUCT_URLS
from src.db import create_tables, insert_winery, insert_product, insert_media
from src.scraper import get_soup
from src.parser import parse_product_page


def main():
    create_tables()

    winery_id = insert_winery("Joseph Perrier", BASE_URL)

    print(f"Starting ingestion for {len(PRODUCT_URLS)} product pages...")

    for product_url in PRODUCT_URLS:
        print(f"Processing: {product_url}")
        soup = get_soup(product_url)
        product_data = parse_product_page(soup, product_url)

        product_id = insert_product(winery_id, product_data)

        for image_url in product_data["images"]:
            insert_media(product_id, "image", image_url, product_data["product_url"])

    print("Ingestion complete.")


if __name__ == "__main__":
    main()