import io

import requests
from linkedin_api import Linkedin
from PIL import Image

from credentials import Credentials

if __name__ == "__main__":
    # Connect to LinkedIn API
    username, password = Credentials.get_credentials()
    api = Linkedin(username, password)

    # Retrieve a profile's information
    profile = api.get_profile("thomas-mattone")
    public_id = profile["public_id"]
    picture_url = profile["displayPictureUrl"] + profile["img_800_800"]

    # Save profile picture
    r = requests.get(picture_url)
    img = Image.open(io.BytesIO(r.content))
    img.save(f"../data/raw/{public_id}.jpg")
