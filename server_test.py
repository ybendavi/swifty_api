from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from flask import Flask, redirect, abort, request, Response
import time

app = Flask(__name__)
oauth = None
token_expires_in = None
token = None

class User:
    login: str
    email: str
    first_name: str
    last_name: str
    image_url: str

    def __init__(self, login, email, first_name, last_name, image_url):
        self.login = login
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.image_url = image_url

@app.before_request
def check_https_and_api_key():
    # API key check
    api_key = request.headers.get("X-API-KEY")
    load_dotenv()
    API_KEY = os.getenv("SERVER_SECRET")
    print(API_KEY)
    if api_key != API_KEY:
        print('abort')
        abort(401)
def get_oauth():
    global oauth
    global token_expires_in
    global token
    if oauth is None or token_expires_in < token['expires_in']:
        # Charger les variables d'environnement
        load_dotenv()

        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        token_url = os.getenv("AUTHORIZATION_ENDPOINT")  # https://api.intra.42.fr/oauth/token

        # Authentification OAuth2 (client_credentials grant)
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
        token_expires_in = token['expires_in']
    return oauth

@app.route('/search', methods=['GET'])
def search():
    print('search')
    login = request.args.get('login')
    oauth = get_oauth()
    user = get_user_by_login(oauth, login)
    time.sleep(1)
    if user['status_code'] != 200:
        return Response('{"error": "' + user['error'] + '"}', status=user['status_code'], mimetype="application/json")
        return get_user_by_login(oauth, login)
    else:
        userid = user['userid']
        skills = get_skills(oauth, user_id=userid)
        projects = get_projects(oauth, user_id=userid)
    
        return {
            "status_code": user['status_code'],
            "user": user['user'],
            "skills": skills,
            "projects": projects
        }
        


def interpret_status_code(status_code):
    messages = {
        400: "The request is malformed",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Page or resource is not found",
        422: "Unprocessable entity",
        500: "We have a problem with our server. Please try again later.",
        "Connection refused": "Most likely cause is not using HTTPS."
    }

    return messages.get(status_code, "Unknown error code")
def get_skills(oauth, user_id):
    response = oauth.get("https://api.intra.42.fr/v2/cursus_users", params={"filter[user_id]":user_id})
    print(f"Response status code skill: {response.status_code}")
    skills = response.json()[0]["skills"]
    for skill in skills:
        del skill["id"]
    return skills

def get_projects(oauth, user_id):
    response = oauth.get("https://api.intra.42.fr/v2/projects_users", params={"filter[user_id]":user_id})
    print(f"Response status code project: {response.status_code}")
    projects = []
    for project in response.json():
        if project["status"] == "finished":
            projects.append(
                {"name": project['project']['name'],
                "final_mark": project['final_mark'],
                "status": project['status']
                })
    return projects

def get_user_by_login(oauth, login):
    response = oauth.get("https://api.intra.42.fr/v2/users", params={"filter[login]":login})
    #print(f"Response status code: {response.status_code}")
    #print(response.json())
    if response.status_code != 200:
        return {
            "status_code": response.status_code,
            "error": interpret_status_code(response.status_code)
        }
    elif response.status_code == 200 and len(response.json()) > 0:
        json_response = response.json()[0] 
        user = {
            "login": json_response['login'],
            "email": json_response['email'],
            "first_name": json_response['first_name'],
            "last_name": json_response['last_name'],
            "image_url": json_response['image']['link'],
            "phone": json_response['phone'],
            "wallet": json_response['wallet'],
        }
        return {
            "status_code": response.status_code,
            "user": user,
            "userid": json_response['id']
        }
    else:
        print(response.json())
        print(f"login: {login}")
        return {
            "status_code": 201,
            "error": "User not found"
        }



def main():
    app.run(host='0.0.0.0', port=5000, debug=True)
    #print(f"Response col: {df}")
    return
    userid = df.id.values[0]
    df1 = get_skills(oauth, user_id=userid)
    #df = pd.DataFrame(response.json())
    print(f"Response col: {df1}")

if __name__ == "__main__":
    main()