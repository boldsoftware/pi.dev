import os


def is_prod():
    return env() == "prod"


def env():
    return os.environ.get("ENV", "dev")
