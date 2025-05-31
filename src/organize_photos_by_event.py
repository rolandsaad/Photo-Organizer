import os
import shutil
from datetime import datetime, timedelta
from PIL import Image
from PIL.ExifTags import TAGS
import mimetypes
from collections import defaultdict
import re

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')  # Supported photo file types
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')  # Supported video file types


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
    # Try to find YYYYMMDD in filename
    match = re.search(r'(20\d{2})(\d{2})(\d{2})', filename)
    if match:
        try:
            return datetime.strptime(''.join(match.groups()), "%Y%m%d")
        except Exception:
            pass

    # Fallback: Try to parse common timestamp formats from filename
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

    for base_path in folder_paths:
        print(f"Scanning folder: {base_path}")
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                file_lower = file.lower()
                if file_lower.endswith(SUPPORTED_IMAGE_EXTENSIONS):
                    dt = get_exif_datetime(full_path)
                    image_count += 1
                elif file_lower.endswith(SUPPORTED_VIDEO_EXTENSIONS):
                    dt = parse_datetime_from_filename(file)
                    video_count += 1
                else:
                    continue

                if dt:
                    media.append((dt, full_path))

    print(f"Total media found: {len(media)}")
    print(f"  Images: {image_count}")
    print(f"  Videos: {video_count}")
    return sorted(media, key=lambda x: x[0]), image_count, video_count


def cluster_media(files, event_time_threshold):
    events = []
    current_event = []

    for i, (timestamp, path) in enumerate(files):
        if not current_event:
            current_event.append((timestamp, path))
            continue

        last_time = current_event[-1][0]
        same_day = timestamp.date() == current_event[0][0].date()
        time_diff = timestamp - last_time

        if same_day and time_diff < event_time_threshold:
            current_event.append((timestamp, path))
        else:
            events.append(current_event)
            current_event = [(timestamp, path)]

    if current_event:
        events.append(current_event)

    return events


def create_event_folder(base, timestamp, counter, num_files, large=False):
    date_str = timestamp.strftime('%Y_%m_%d')
    base_name = date_str if counter == 1 else f"{date_str} - {counter - 1:03d}"
    folder_name = f"{base_name} ({num_files} files)" if large else base_name
    full_path = os.path.join(base, folder_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def organize_media(config):
    input_folders = config['input_folders']
    event_output_folder = config['event_output_folder']
    large_event_output_folder = config.get('large_event_output_folder', event_output_folder)
    large_event_threshold = config.get('large_event_threshold', 20)
    event_time_threshold = config.get('event_time_threshold', timedelta(minutes=45))

    media, image_count, video_count = get_all_media(input_folders)
    events = cluster_media(media, event_time_threshold)

    print(f"Total events identified: {len(events)}")

    day_counters = defaultdict(int)
    copied_files = 0

    for i, event in enumerate(events):
        event_date = event[0][0].strftime('%Y_%m_%d')
        day_counters[event_date] += 1
        is_large = len(event) > large_event_threshold
        destination = large_event_output_folder if is_large else event_output_folder
        folder = create_event_folder(destination, event[0][0], day_counters[event_date], len(event), large=is_large)
        if len(event) > large_event_threshold:
            print(f"Event {i + 1}: Created folder '{folder}' with {len(event)} files.")
        for _, path in event:
            try:
                shutil.copy2(path, folder)
                copied_files += 1
            except Exception as e:
                print(f"Failed to copy '{path}' to '{folder}': {e}")

    print("\nSummary:")
    print(f"  Total media files found: {len(media)}")
    print(f"  Total media files copied: {copied_files}")
    print(f"  Images copied: {image_count}")
    print(f"  Videos copied: {video_count}")


if __name__ == '__main__':
    # Example usage with configuration dictionary
    config = {
        'input_folders': [
                        'D:/CloudStation/_Need Organization/Roland Phone - Samsung Galaxy S21',
                        'D:/CloudStation/_Need Organization/Roland Phone - Samsung Galaxy S24',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S24',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S20/Camera',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S10/Camera'
                        ],
        'event_output_folder': 'D:/CloudStation/_Need Organization/Sorted2',
        'large_event_output_folder': 'D:/CloudStation/_Need Organization/Sorted2_Large',
        'large_event_threshold': 20,
        'event_time_threshold': timedelta(minutes=45)
    }
    organize_media(config)