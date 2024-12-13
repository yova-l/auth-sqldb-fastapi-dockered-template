import requests

# Base URL for the FastAPI server
BASE_URL = "http://127.0.0.1:8000"  # Change this to your server's actual URL

# Test data
username = "myuser"
password = "123456"
pageid = "fsd456fdg456fdg654"
auth_message = {"msg": "This is a secured test message"}
public_message = {"msg": "This is a public test message"}

# Step 1: Test the /token endpoint to get the access token
def get_access_token():
    url = f"{BASE_URL}/token"
    data = {"username": username, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Failed to get access token:", response.json())
        return None

# Step 2: Test the /authreq/{pageid} endpoint (requires authentication)
def test_authreq_endpoint(token):
    url = f"{BASE_URL}/authreq/{pageid}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=auth_message, headers=headers)
    print("Auth endpoint response:", response.status_code, response.json())

# Step 3: Test the /noauthreq endpoint (no authentication needed)
def test_noauthreq_endpoint():
    url = f"{BASE_URL}/noauthreq"
    response = requests.get(url, params={"msg": "This is a public test message"}, json={"msg": "This is a public test message"})  # Use GET with query parameters
    print("No auth endpoint response:", response.status_code, response.json())

# Run the tests
if __name__ == "__main__":
    print("Testing /token endpoint...")
    token = get_access_token()
    if token:
        print("Testing /authreq/{pageid} endpoint...")
        test_authreq_endpoint(token)

    print("Testing /noauthreq endpoint...")
    test_noauthreq_endpoint()
