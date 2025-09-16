import qrcode
import os

if not os.path.exists("qrcodes"):
    os.makedirs("qrcodes")

product_id = "12345"
url = f"http://localhost:8000/dpp/{product_id}"

img = qrcode.make(url)
img.save(f"qrcodes/{product_id}.png")
print(f"QR code saved for product {product_id} in qrcodes folder!")
