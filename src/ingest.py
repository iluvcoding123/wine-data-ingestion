from src.db import create_tables, insert_winery, insert_product, insert_media

create_tables()

winery_id = insert_winery("Joseph Perrier", "https://www.josephperrier.com")

product_id = insert_product(
    winery_id,
    "Test Wine",
    "https://example.com",
    "Test description"
)

insert_media(product_id, "image", "https://example.com/image.jpg")