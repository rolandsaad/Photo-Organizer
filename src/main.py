from organize_photos_by_event import organize_media
from datetime import timedelta

if __name__ == '__main__':
    # Example usage with configuration dictionary
    config = {
        'input_folders': [
                        'D:/CloudStation/_Need Organization/Roland Phone - Older',
                        'D:/CloudStation/_Need Organization/Roland Phone - OnePlus5',
                        'D:/CloudStation/_Need Organization/Roland Phone - Samsung Galaxy S21',
                        'D:/CloudStation/_Need Organization/Roland Phone - Samsung Galaxy S24',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S24',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S10/Camera',
                        'D:/CloudStation/_Need Organization/Mado Phone - Samsung Galaxy S20/Camera',
                        ],
        'event_output_folder': 'D:/CloudStation/_Need Organization/Sorted3',
        'large_event_output_folder': 'D:/CloudStation/_Need Organization/Sorted3_Large',
        'large_event_threshold': 20,
        'event_time_threshold': timedelta(minutes=45)
    }
    organize_media(config)