import glob
import io
import os
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

import requests
from credentials import Credentials
from linkedin_api import Linkedin
from PIL import Image
from tqdm import tqdm


def clear_previous_data():
    """Remove all the raw data"""
    for file in glob.glob("../../data/raw/*"):
        os.remove(file)


def init_linkedin_api():
    """Initialize the connection to the LinkedIn API.

    Returns:
        object: API object.
    """
    username, password = Credentials.get_credentials("../../credentials.txt")
    return Linkedin(username, password)


def load_most_given_names() -> list[str]:
    """Load the most given French names between 1989 and 1998.
    This year range has been selected based on the LinkedIn age distribution
    in January 2023.

    Returns:
        list[str]: most given names.
    """
    boy_names = []
    girl_names = []

    with open(
        "../../data/external/most_given_boy_names_1989_1998_100.csv"
    ) as f:
        boy_names = f.read().splitlines()

    with open(
        "../../data/external/most_given_girl_names_1989_1998_100.csv"
    ) as f:
        girl_names = f.read().splitlines()

    return boy_names + girl_names


def download_profile_picture_by_name(name: str, sample_size: int):
    """Download the profile pictures of persons by name using the LinkedIn API.

    Args:
        name (str): profil's name.
        sample_size (int): number of retrieve profile picture.
    """
    FRANCE_GEO_URN = "105015875"

    api = init_linkedin_api()

    print(api)

    people = api.search_people(
        keyword_first_name=name,
        regions=[FRANCE_GEO_URN],
        limit=sample_size,
    )

    for person in tqdm(people, desc=f"{name}", leave=True):
        urn_id = person["urn_id"]

        # Check firstname to overcome compound firstname scenario
        # ("jean" != "jean-charles")
        profile = api.get_profile(urn_id=urn_id)
        if profile["firstName"] != name:
            continue

        # Retrieve profil picture
        picture_url = profile["displayPictureUrl"] + profile["img_800_800"]
        r = requests.get(picture_url)

        # Save picture
        img = Image.open(io.BytesIO(r.content))
        img.save(f"../../data/raw/{profile['firstName']}_{urn_id}.jpg")


if __name__ == "__main__":
    SAMPLE_LIMIT = 100

    clear_previous_data()

    names = load_most_given_names()
    # names = names[0:1]

    with ThreadPoolExecutor() as executor:
        executor.map(
            lambda args: download_profile_picture_by_name(*args),
            zip(names, repeat(SAMPLE_LIMIT)),
        )
