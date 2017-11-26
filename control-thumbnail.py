"""Generate thumbnails using MICROSOFT API"""
import thumbnails_toolkit as tk

thumb = tk.get_thumbnail()

if thumb is not None:
    # Load the original image, fetched from the URL
    with open("photo_thumbnail.jpg", 'wb') as f:
        f.write(thumb)
    print("showing image")
