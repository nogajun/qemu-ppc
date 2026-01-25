import os

from dotenv import load_dotenv

load_dotenv()

cockpit = (
    ["192.168.0.202"],
    {
        "_sudo": True,
        "_sudo_password": os.getenv("SUDO_PASSWORD"),
        "ssh_user": os.getenv("SSH_USER"),
        "ssh_key": os.getenv("SSH_KEY"),
    },
)
