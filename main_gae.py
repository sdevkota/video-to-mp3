# Google App Engine entry point
import os
import subprocess
import sys

# Set environment variables for Streamlit
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '8080'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

if __name__ == '__main__':
    # Run Streamlit app
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', 
                   '--server.port=8080', '--server.address=0.0.0.0', '--server.headless=true'])
