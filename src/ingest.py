from src.config import TEST_PRODUCT_URL
from src.db import create_tables, insert_winery, insert_product, insert_media
from src.scraper import get_soup
from src.parser import parse_product_page

def main():
    create_tables()

    winery_id = insert_winery(
        "Joseph Perrier",
        "https://www.josephperrier.com/en"
    )

    soup = get_soup(TEST_PRODUCT_URL)
    product_data = parse_product_page(soup, TEST_PRODUCT_URL)

    product_id = insert_product(
        winery_id,
        product_data["name"],
        product_data["product_url"],
        product_data["description"]
    )

    for image_url in product_data["images"]:
        insert_media(
            product_id,
            "image",
            image_url,
            product_data["product_url"]
        )

    print("Ingestion complete.")

if __name__ == "__main__":
    main()