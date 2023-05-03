import requests
import sys

# Simple health check script to ensure api is available before
# running containers depending on Prefect API being available
r = requests.get('http://localhost:4200/api')

if r.status_code!= 200:
    sys.exit(1)     # abnormal termination (fail the health check)
