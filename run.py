import os
import sys

from dotenv import load_dotenv

from app import create_app

# Load environment variables based on command line argument
env_file = '.env'
if len(sys.argv) > 1:
    if sys.argv[1] == 'homologation':
        env_file = '.env.homologation'
        print('Running in homologation environment')
    elif sys.argv[1] == 'production':
        env_file = '.env.production'
        print('Running in production environment')
    else:
        print(f'Running in {sys.argv[1]} environment')
        env_file = f'.env.{sys.argv[1]}'
else:
    print('Running in development environment')

# Load the appropriate environment file
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()  # Fall back to .env

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=True,
        extra_files=[
            'app/templates/base.html',
            'app/modules/file_manager/templates/index.html',
            'app/modules/time_calculator/templates/time_calculator.html',
            'app/static/css/style.css',
        ],
    )
