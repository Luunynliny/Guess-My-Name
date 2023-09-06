class Credentials:
    def get_credentials():
        with open("../credentials.txt", "r") as f:
            return f.readline().split(",")
