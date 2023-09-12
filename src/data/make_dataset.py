import glob
import io
import os

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
        list[str]: _description_
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


def retrieve_profiles_by_names(
    api, names: list[str], sample_size: int
) -> list[str]:
    """_summary_

    Args:
        api (object): LinkedIn API.
        names (list[str]): profile names we want to search.
        sample_size (int): number of retrieve profile for each name.

    Returns:
        list[str]: list of profile urn_id.
    """
    FRANCE_GEO_URN = "105015875"

    urn_ids = []

    for name in tqdm(names, desc="Retrieving profiles urn_id"):
        people = api.search_people(
            keyword_first_name=name,
            regions=[FRANCE_GEO_URN],
            limit=sample_size,
        )

        for person in tqdm(people, desc=f"{name}", leave=False):
            urn_id = person["urn_id"]

            # Check firstname to overcome compound firstname scenario
            # ("jean" != "jean-charles")
            profile = api.get_profile(urn_id=urn_id)
            if profile["firstName"] != name:
                continue

            urn_ids.append(urn_id)

    return urn_ids


def download_profile_picture(api, urn_id: str, name: str):
    """Download the profile picture of a person using the LinkedIn API
    and the person's urn_id.

    Args:
        api (object): API object.
        urn_id (str): profil's urn_id.
        name (str): profil's name.
    """
    profile = api.get_profile(urn_id=urn_id)
    picture_url = profile["displayPictureUrl"] + profile["img_800_800"]

    # Save profil picture
    r = requests.get(picture_url)
    img = Image.open(io.BytesIO(r.content))
    img.save(f"../../data/raw/{profile['firstName']}_{urn_id}.jpg")


if __name__ == "__main__":
    SAMPLE_LIMIT = 10

    clear_previous_data()

    names = load_most_given_names()

    api = init_linkedin_api()
    urn_ids = retrieve_profiles_by_names(
        api=api, names=names, sample_size=SAMPLE_LIMIT
    )

    for urn_id in tqdm(urn_ids, desc="Doawnloading profiles picture"):
        download_profile_picture(api=api, urn_id=urn_id)
