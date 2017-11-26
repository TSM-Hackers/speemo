"""Generate thumbnails using MICROSOFT API"""
import thumbnails_toolkit as tk
import os


filename = "temp_image.jpg"
img = tk.capture_snapshot(filename)
with open(filename, 'rb') as f:
    data = f.read()
os.remove(filename)

thumb = tk.get_thumbnail(data)

if thumb is not None:
    # Load the original image, fetched from the URL
    with open("photo_thumbnail.jpg", 'wb') as f:
        f.write(thumb)
    print("showing image")
