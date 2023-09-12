import glob
import io
import os

import requests
from credentials import Credentials
from linkedin_api import Linkedin
from PIL import Image


def init_linkedin_api():
    """Initialize the connection to the LinkedIn API.

    Returns:
        object: API object.
    """
    username, password = Credentials.get_credentials("../../credentials.txt")
    return Linkedin(username, password)


def clear_previous_data():
    """Remove all the raw data"""
    for file in glob.glob("../../data/raw/*"):
        os.remove(file)


def download_profile_picture(api, urn_id: str, name: str):
    """Download the profile picture of a person using the LinkedIn API
    and the person's urn_id.

    Args:
        api (object): API object.
        urn_id (str): profil's urn_id.
        name (str): profil's name.
    """
    profile = api.get_profile(urn_id=urn_id)

    # Check firstname to overcome compound firsname scenario
    # ("jean" != "jean-charles")
    if profile["firstName"] != name:
        return

    picture_url = profile["displayPictureUrl"] + profile["img_800_800"]

    # Save profil picture
    r = requests.get(picture_url)
    img = Image.open(io.BytesIO(r.content))
    img.save(f"../../data/raw/{name}_{urn_id}.jpg")


if __name__ == "__main__":
    NAME = "Jean"
    SAMPLE_LIMIT = 10
    FRANCE_GEO_URN = "105015875"

    clear_previous_data()

    api = init_linkedin_api()
    people = api.search_people(
        keyword_first_name=NAME, regions=[FRANCE_GEO_URN], limit=SAMPLE_LIMIT
    )

    for person in people:
        download_profile_picture(api=api, urn_id=person["urn_id"], name=NAME)
