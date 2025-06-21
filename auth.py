import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()


def get_cookies():
    # Step 1: Start a session
    session = requests.Session()



    # Step 2: Go to initial page (triggers redirect)
    initial_url = "https://obs.itu.edu.tr/ogrenci"
    initial_resp = session.get(initial_url, allow_redirects=True)

    # Follow the redirect to the actual login page
    login_url = initial_resp.url
    print(f"[DEBUG] Redirected to login page: {login_url}")

    # Step 3: Fetch login page HTML
    resp = session.get(login_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Step 4: Extract ASP.NET form fields
    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": soup.find("input", {"name": "__VIEWSTATE"})["value"],
        "__VIEWSTATEGENERATOR": soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"],
        "__EVENTVALIDATION": soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
        "ctl00$ContentPlaceHolder1$hfAppName": "Öğrenci Bilgi Sistemi",
        "ctl00$ContentPlaceHolder1$hfToken": "",
        "ctl00$ContentPlaceHolder1$hfVerifier": "",
        "ctl00$ContentPlaceHolder1$hfCode": "",
        "ctl00$ContentPlaceHolder1$hfState": "",
        "ctl00$ContentPlaceHolder1$tbUserName": os.getenv("username"),
        "ctl00$ContentPlaceHolder1$tbPassword": os.getenv("password"),
        "ctl00$ContentPlaceHolder1$btnLogin": "Giriş / Login"
    }

    # Step 5: Submit credentials (POST to login URL from redirect)
    login_resp = session.post(login_url, data=payload, allow_redirects=False)

    # Step 6: Follow redirect after successful login
    if login_resp.status_code == 302:
        redirect_url = login_resp.headers["Location"]
        print(f"[DEBUG] Redirect after login: {redirect_url}")

        # Get final authenticated page
        final_resp = session.get(redirect_url)


        # Step 7: Confirm if we're on the student page
        if "/ogrenci" in final_resp.url or "OBS" in final_resp.text:
            print("[+] Login successful. Student dashboard loaded.")
            
            cookies = session.cookies.get_dict()
            print("[+] Session cookies:")
            for name, value in cookies.items():
                cookies_str = ";".join([f"{name}={value}" for name, value in cookies.items()])
                print(cookies_str)
                return cookies_str
        else:
            print("[-] Unexpected page after login.")
            print(final_resp.url)
            return

    else:
        print("[-] Login failed.")
        print(login_resp.status_code, login_resp.text[:500])
        return 0

    return 

def get_jwt():
    """
    Calls the JWT endpoint with preformatted cookie string from get_cookies(),
    and returns the Bearer token.
    """
    # Endpoint
    url = "https://obs.itu.edu.tr/ogrenci/auth/jwt"

    # Get cookie string from your implemented function
    cookie_string = get_cookies()

    # Headers with manual cookie string
    headers = {
        "Cookie": cookie_string,
        "Accept": "application/json"
    }


    response = requests.get(url, headers=headers)


    if response.status_code != 200:
        raise Exception(f"Failed to get JWT. Status: {response.status_code}, Body: {response.text[:500]}")

    token = response.text.strip().strip('"')

    if not token or "." not in token:
        raise ValueError("Invalid JWT token returned.")

    return token

