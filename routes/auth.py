import os, requests
from flask import Blueprint, redirect, request, session, jsonify

bp = Blueprint('auth', __name__)
# auth.py


GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@bp.route("/auth/github")
def login_github():
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user"
    )

@bp.route("/auth/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    # Exchange code for access token
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        },
    )
    token_json = token_res.json()
    access_token = token_json.get("access_token")
    session["access_token"] = {
        "access_token": access_token        
    }
    print(access_token)

    if not access_token:
        return jsonify(token_json), 400

    # Get user info
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    )
    user = user_res.json()
    

    session["user"] = {
        "id": user["id"],
        "name": user["name"],
        "avatar": user["avatar_url"],
        "username": user["login"],
        
    }

    # Redirect to frontend with user info (encoded in query string)
    Redirect_url = f"http://localhost:5173/auth/success"
    return redirect(Redirect_url)

@bp.route("/auth/user")
def get_user():
    user = session.get("user")
    print(user)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "Unauthorized"}), 401
    
    
@bp.route("/auth/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200
