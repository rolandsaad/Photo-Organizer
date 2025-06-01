# media_loader.py
import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import re
from collections import defaultdict

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')

def get_exif_datetime(img_path):
    try:
        img = Image.open(img_path)
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == 'DateTimeOriginal':
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading EXIF from {img_path}: {e}")
    return None

def parse_datetime_from_filename(filename):
    match = re.search(r'(20\d{2})(\d{2})(\d{2})', filename)
    if match:
        try:
            return datetime.strptime(''.join(match.groups()), "%Y%m%d")
        except Exception:
            pass
    try:
        return datetime.strptime(filename, "%Y-%m-%d %H-%M-%S")
    except Exception:
        pass
    try:
        return datetime.strptime(filename, "%Y%m%d_%H%M%S")
    except Exception:
        pass
    return None

def get_all_media(folder_paths):
    media = []
    image_count = 0
    video_count = 0
    skip_count = 0
    yearly_media_count = defaultdict(int)
    dt_unknown = datetime(1900, 1, 1, 0, 0, 0);

    for base_path in folder_paths:
        print(f"Scanning folder: {base_path}")
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                file_lower = file.lower()
                if file_lower.endswith(SUPPORTED_IMAGE_EXTENSIONS):
                    dt = get_exif_datetime(full_path)
                    if dt:
                        image_count += 1
                        yearly_media_count[dt.year] += 1
                        media.append((dt, full_path))
                    else:
                        media.append((dt_unknown, full_path));
                elif file_lower.endswith(SUPPORTED_VIDEO_EXTENSIONS):
                    dt = parse_datetime_from_filename(file)
                    if dt:
                        video_count += 1
                        yearly_media_count[dt.year] += 1
                        media.append((dt, full_path))
                    else:
                        media.append((dt_unknown, full_path));
                else:
                    print(f"Unsupported file type: {file} in {root}")
                    skip_count += 1
    print(f"Total media found: {len(media)}")
    print(f"  Skipped: {skip_count}")
    print(f"  Images: {image_count}")
    print(f"  Videos: {video_count}")
    print("  Media per year:")
    for year, count in sorted(yearly_media_count.items()):
        print(f"    {year}: {count}")
    return sorted(media, key=lambda x: x[0])
