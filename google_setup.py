import os

from core import config
from core.notification.gmail import Gmail
from core.storage.google_drive import GoogleDrive

if __name__ == '__main__':
    items = os.listdir('.')
    if 'gmail_v1_token.json' not in items:
        Gmail().initialize_service()
    if 'drive_v3_token.json' not in items:
        gd = GoogleDrive()
        gd.initialize_service()
        if 'google_drive_folder_id' not in config.global_instance:
            folder_id = gd.create_folder('nico_crawler')
            config.save('config_secret.json', kvps={'google_drive_folder_id': folder_id})
