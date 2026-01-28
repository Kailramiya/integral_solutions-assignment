
import os
import sys


# Ensure imports like `from app import create_app` work even when launched from repo root.
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)

