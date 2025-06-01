import os
import shutil
from datetime import timedelta
from media_loader import get_all_media

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')  # Supported photo file types
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')  # Supported video file types


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


def create_unique_event_folder(base, suffix, timestamp):
    # Append the year to the base path and create the year folder if it doesn't exist
    year_folder_path = os.path.join(base, timestamp.strftime('%Y'))
    os.makedirs(year_folder_path, exist_ok=True)

    # Append event folder name
    date_str = timestamp.strftime('%Y_%m_%d')
    full_path = os.path.join(year_folder_path, f"{date_str}{suffix}")
    
    # Ensure the full path is unique otherwise increment the counter and append it to the name
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(year_folder_path, f"{date_str} - {counter:03d}{suffix}")
        counter += 1

    # Append the suffix to the event name
    os.makedirs(full_path, exist_ok=True)
    return full_path

def copy_with_unique_name(src_path, dest_folder):
    base_name = os.path.basename(src_path)
    name, ext = os.path.splitext(base_name)
    dest_path = os.path.join(dest_folder, base_name)
    
    # Ensure the destination path is unique otherwise increment the counter and append it to the name
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
        counter += 1

    shutil.copy2(src_path, dest_path)
    return dest_path

def organize_media(config):
    input_folders = config['input_folders']
    event_output_folder = config['event_output_folder']
    large_event_output_folder = config.get('large_event_output_folder', event_output_folder)
    large_event_threshold = config.get('large_event_threshold', 20)
    event_time_threshold = config.get('event_time_threshold', timedelta(minutes=45))

    media = get_all_media(input_folders)
    events = cluster_media(media, event_time_threshold)

    print(f"Total events identified: {len(events)}")

    copied_files = 0

    for i, event in enumerate(events):
        destination = event_output_folder
        suffix = ""
        if len(event) > large_event_threshold :
            destination = large_event_output_folder
            suffix = f" ({len(event)} files)"

        folder = create_unique_event_folder(destination, suffix, event[0][0])
        if len(event) > large_event_threshold:
            print(f"Event {i + 1}: Created folder '{folder}' with {len(event)} files.")
        for _, path in event:
            try:
                copy_with_unique_name(path, folder)
                copied_files += 1
            except Exception as e:
                print(f"Failed to copy '{path}' to '{folder}': {e}")

    print("\nSummary:")
    print(f"  Total media files found: {len(media)}")
    print(f"  Total media files copied: {copied_files}")