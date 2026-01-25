import os

from dotenv import load_dotenv

load_dotenv()

cockpit = (
    [os.getenv("IP")],
    {
        "_sudo": True,
        "_sudo_password": os.getenv("SUDO_PASSWORD"),
        "ssh_user": os.getenv("SSH_USER"),
        "ssh_key": os.getenv("SSH_KEY"),
        "gateway": os.getenv("GATEWAY"),
        "dns": os.getenv("DNS"),
    },
)
