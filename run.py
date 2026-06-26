import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create app
app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug, port=port, host='0.0.0.0')