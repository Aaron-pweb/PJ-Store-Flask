from app import create_app
import os

app = create_app()
# Fetches the URL from the docker-compose environment, handling the connection routing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///default.db'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
