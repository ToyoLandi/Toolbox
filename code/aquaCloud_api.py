# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# |                         Aqua SaaS API                                     |
# |                - Python Complete Script Example -                         |
# |                      Rev: Mar 27th, 2024                                  |
# |                                                                           |
# |     NOTE: This script is meant to be used as a working API example        |
# |     for all components (CWPP, CSPM, SCS) of Aqua SaaS. Including          |
# |     * authentication *, a common hurdle due to our unique "HMAC-256"      |
# |     signature requirements, and some other quality-of-life functions      |
# |     that we think you will find useful.                                   |
# |                                                                           | 
# |                                                 ~ Happy Automating!       |  
# |                                                                           | 
# |     // Written by Collin Spears, and a special thanks to Berto Trillo     |    
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import ssl
import json
import time
import hmac
import hashlib
from urllib.parse import urlparse
from requests.utils import DEFAULT_CA_BUNDLE_PATH

import jwt              # IMPORTANT: 'jwt' needs to be installed. Try pip!
import requests         # IMPORTANT: 'requests' needs to be installed. Try pip!

# [REQUIRED] Settings:
#   You * must * set these variables according to your environment. We are
#   using "strings" in this example for clarity. API_URL, and SCS_URL do not
#   need to be modified. If you prefer using environment variables for 
#   API_KEY, API_SECRET, and AQUA_URL, replace the string with...
#       
#       EXAMPLE = os.getenv("ENVVAR_NAME").
#
# NOTE: In this example, we actually fetch our AQUA_URL using get_aqua_url(),
# which is only used for Workload Protection calls. If you wish to forgo using
# your JWT token, replace `aqua_url` in example_api_cwpp() with AQUA_URL on
# line 157. 

AQUA_URL = 'https://abcd1234.cloud.aquasec.com'         # See NOTE above.
API_URL = "https://api.cloudsploit.com"
SCS_URL = "https://codesec.aquasec.com"
AQUA_CSP_ROLE = "cspears-test-role"                     # CRITICAL
API_KEY = ''                      # CRITICAL
API_SECRET = ''      # CRITICAL


def auth_headers(url: str, method: str, payload: str = "") -> dict:
    '''
    Handling the HMAC-256 signature creation logic, and setting headers for
    SaaS Aqua API Authentication, or for CSPM API calls. See example_cspm_api()
    for an example of the latter. 
    '''
    timestamp = str(int(time.time() * 1000))
    path = urlparse(url).path
    string = (timestamp + method + path + payload).replace(" ", "")
    secret_bytes = bytes(API_SECRET, "utf-8")
    string_bytes = bytes(string, "utf-8")
    sig = hmac.new(secret_bytes, msg=string_bytes, digestmod=hashlib.sha256).hexdigest()
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY,
        "x-signature": sig,
        "x-timestamp": timestamp,
        "content-type": "application/json",
    }
    curl_command = ("curl --request " + method 
        + " --header \"accept: application/json\" --header \"x-api-key: " 
        + API_KEY + "\" --header \"x-signature: " + sig 
        + "\" --header \"x-timestamp: " + timestamp 
        + "\" --header \"content-type: application/json\" --data \'" + payload 
        + "\' " + url)
    return headers

def auth_cwpp_headers(token: str = "") -> dict:
    '''
    Formatting the headers for Workload Protecion, and SCS API calls that use
    "Bearer Token". In this script, we fetch this token via gen_token()
    '''
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer" + " " + f"{token}"
    }
    return headers

def gen_token():
    '''
    Generate a token from the "cloudsploit" URL. We use this as a Bearer Token
    for Workload Protection and SCS API calls. 
    '''
    ssl._create_default_https_context = ssl._create_unverified_context
    url = f"{API_URL}/v2/tokens"
    method = 'POST'
    payload = json.dumps({"validity":240,"allowed_endpoints":["ANY"],"csp_roles":[AQUA_CSP_ROLE]})
    request = requests.post(url, data=payload, headers=auth_headers(url,method,payload))
    response_body = json.loads(request.text)
    token = response_body["data"]
    return token

def get_aqua_url(token):
    '''
    Using the JWT token to parse for the FQDN for cloud.aquasec.com

    If you wish to forgo this method, you can parse the URL yourself in one of 
    our Scanner deployment commands in the UI, and replace the AQUA_URL var at
    the head of this script.
    '''
    #### Decode JWT Token for URL ###
    decoded_parse = jwt.decode(token, options={"verify_signature": False})
    aqua_url = decoded_parse["csp_metadata"]["urls"]["ese_url"]
    return aqua_url

def example_api_cspm():
    '''
    A complete example for a CSPM API call including authentication.

    Example Endpoint: https://api.cloudsploit.com/v2/users
    '''
    print("--> Example CSPM API = '/v2/users'\n")
    ssl._create_default_https_context = ssl._create_unverified_context
    # Setting method, which is required for the CSPM signature headers.
    method = "GET"
    # STEP 1: Putting together our API endpoint string
    api_version = 'v2'
    api_endpoint = 'users'
    formatted_endpoint = f"/{api_version}/" + api_endpoint
    url = f"{API_URL}" + formatted_endpoint
    # STEP 2: Send our request to our API endpoint w/ proper headers.
    request = requests.get(url, headers=auth_headers(url,method))
    # STEP 3: Parse our JSON response
    request_response = json.loads(request.text)
    response = json.dumps(request_response, indent = 4, sort_keys = True)
    print(response)
    return response

def example_api_cwpp():
    '''
    A complete example Workload Protection API call, including authentication,
    and fetching the SaaS FQDN using get_aqua_url().

    Example Endpoint: https://abcd1234.cloud.aquasec.com/api/v2/license
    '''
    print("\n--> Example Workload Protection API = '/api/v2/license'\n")
    ssl._create_default_https_context = ssl._create_unverified_context
    # Putting together our API endpoint string
    api_version = 'v2'
    api_endpoint = 'license'
    formatted_endpoint = f"api/{api_version}/" + api_endpoint
    # STEP 1: Get a Cloudsploit Token...
    token = gen_token()
    # STEP 2: Get the FQDN URL for "cloud.aquasec.com" from our token.
    #   And declare the full API endpoint string here.
    aqua_url = "https://" + get_aqua_url(token)
    endpoint_url = f"{aqua_url}/" + formatted_endpoint
    # STEP 3: Send our request to our API endpoint w/ proper headers.
    request = requests.get(endpoint_url, headers=auth_cwpp_headers(token))
    # STEP 4: Parse our JSON response
    request_response = json.loads(request.text)
    response = json.dumps(request_response, indent = 4, sort_keys = True)
    print(response)
    return response

def example_api_scs():
    '''
    A complete example Supply Chain Sec API call, including authentication.

    Example Endpoint: https://codesec.aquasec.com/api/v1/scans/results
    '''
    print("\n--> Example Supply Chain API = '/api/v1/scans/results'\n")
    ssl._create_default_https_context = ssl._create_unverified_context
    # Putting together our API endpoint string
    api_version = 'v1'
    api_endpoint = 'scans/results'
    formatted_endpoint = f"api/{api_version}/" + api_endpoint
    # STEP 1: Get a Cloudsploit Token...
    token = gen_token()
    # STEP 2: Declare our SCS URL + API endpoint
    endpoint_url = f"{SCS_URL}/" + formatted_endpoint
    # STEP 3: Send our request to our API endpoint w/ proper headers. SCS uses
    # the same method as CWPP, but w/ a different root URL.
    request = requests.get(endpoint_url, headers=auth_cwpp_headers(token))
    # STEP 4: Parse our JSON response
    request_response = json.loads(request.text)
    response = json.dumps(request_response, indent = 4, sort_keys = True)
    print(response)
    return response

# MAIN - We run the lines here when this file is exec'd.
# ex.) python3 /path/to/script.py
if __name__ == "__main__":
    print('''
    ╔═════════════════════════════════════════╗
    ║            Aqua SaaS API                ║
    ║   - Python Complete Script Example -    ║
    ║          Rev: Mar 27th, 2024            ║
    ╚═════════════════════════════════════════╝''')
    # An example for CSPM. 
    example_api_cspm()
    # An example for CWPP.
    example_api_cwpp()
    # An example for SCS
    example_api_scs()
