class Credentials:
    def get_credentials(filepath):
        with open(filepath, "r") as f:
            return f.readline().split(",")
