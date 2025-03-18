import os
from app import create_app
from app.core.config import config

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=config.DEBUG
    ) 