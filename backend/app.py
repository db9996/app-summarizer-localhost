import os
import logging
import traceback
import sys
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, Blueprint, request, jsonify, redirect, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
from datetime import datetime
from flask_session import Session
from flask_dance.consumer import oauth_authorized
from werkzeug.middleware.proxy_fix import ProxyFix
try:
    from .config import Config
    from .models import db, User, Summary, SummaryHistory
except ImportError:
    from config import Config
    from models import db, User, Summary, SummaryHistory


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
load_dotenv()

print("PWD:", os.getcwd())
print("sys.path:", sys.path)
print("Files:", os.listdir("."))
print("GOOGLE_OAUTH_CLIENT_ID value:", repr(os.environ.get("GOOGLE_OAUTH_CLIENT_ID")))
print("GOOGLE_OAUTH_CLIENT_SECRET value:", repr(os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")))
print("Google Cloud API Key:", os.getenv("GOOGLE_CLOUD_API_KEY"))
print("MARKER FLASK FILE:", __file__, "CWD:", os.getcwd())
print("FLASK RUNNING FROM:", os.getcwd(), __file__)
print("Google Client ID:", os.getenv("GOOGLE_OAUTH_CLIENT_ID"))


app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "postgresql://db9996:Devu2021@localhost:5432/appsummarizer2"
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "supersecret")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://frontend-vite-bo2r.onrender.com",
        "http://localhost:5001",
        "https://app-summarizer-frontend.netlify.app"
    ]
}}, supports_credentials=True)

jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "api.login"
login_manager.init_app(app)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecret"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "superjwtsecret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "postgresql://db9996:Devu2021@localhost:5432/appsummarizer2"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = "Content-Type"
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6380/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6380/0"
app.config.from_object(Config)

from flask import request, redirect

#@app.before_request
#def enforce_http_in_oauth():
#    if request.path.startswith("/api/oauth/") and not request.is_secure:
#        url = request.url.replace("http://", "http://", 1)
#        return redirect(url, code=302)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/api/whoami', methods=['GET'])
@jwt_required()
def whoami():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "email": user.email,
        "id": user.id,
        "oauth_provider": user.oauth_provider
    })

@app.before_request
def debug_session():
    if request.path == "/api/oauth/google/google/authorized":
        print("SESSION DATA:", dict(session))
        print("REQUEST ARGS:", request.args)

# --- OAuth Blueprints ---
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_url="https://app-summarizer-localhost-production.up.railway.app/api/oauth/google/google/authorized"
)
google_bp.authorization_url_params = {"prompt": "select_account"}

def get_or_create_oauth_user(oauth_id, email, name, provider):
    user = User.query.filter((User.oauth_id == oauth_id) | (User.email == email)).first()
    if not user:
        user = User(
            username=None,
            email=email,
            password=None,
            oauth_provider=provider,
            oauth_id=oauth_id
        )
        db.session.add(user)
        db.session.commit()
    return user

from flask_jwt_extended import create_access_token

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    print("[DEBUG] --- Google OAuth Callback Triggered ---")
    print("[DEBUG] Token received from Google:", token)
    try:
        if not token:
            print("[ERROR] No token returned from Google")
            return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?error=OAuthFailed")
        # Google userinfo endpoint (with user access token)
        resp = blueprint.session.get("/oauth2/v2/userinfo")
        print("[DEBUG] Response status code:", resp.status_code)
        print("[DEBUG] resp.ok:", resp.ok)
        if not resp.ok:
            print("[ERROR] Failed to fetch userinfo:", resp.text)
            return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?error=OAuthFailed")
        user_info = resp.json()
        print("[DEBUG] User info payload:", user_info)
        oauth_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", "Google User")
        if not email or not oauth_id:
            print("[ERROR] Missing email or oauth_id in user info:", user_info)
            return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?error=OAuthFailed")
        user = get_or_create_oauth_user(oauth_id, email, name, "google")
        print("[DEBUG] Created or loaded user:", user)
        login_user(user)
        print("[DEBUG] Successfully logged in OAuth user:", user)

        # ------ FIX: JWT for React App ------
        jwt_token = create_access_token(identity=str(user.id))
        print("[DEBUG] JWT token created:", jwt_token)
        # Redirect with JWT as a query param:
        return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?jwt={jwt_token}")
    except Exception as ex:
        # This helps catch exceptions like bad credentials, HTTP errors, etc.
        import traceback
        print("[ERROR] Exception in google_logged_in:", ex)
        traceback.print_exc()
        return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?error=OAuthFailed")



app.register_blueprint(google_bp, url_prefix="/api/oauth/google")

# --- API Blueprint ---
api_bp = Blueprint('api', __name__, url_prefix='/api')

@app.errorhandler(Exception)
def catch_all_exceptions(e):
    print("UNHANDLED EXCEPTION:", e, file=sys.stderr)
    traceback.print_exc()
    if (
        "mismatching_state" in str(e)
        or "CSRF" in str(e)
        or "state not equal" in str(e)
    ):
        return redirect(f"{FRONTEND_ORIGIN}/oauth-callback?error=OAuthFailed")
    return jsonify({"msg": f"Server error: {str(e)}"}), 500

@app.route('/api/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"msg": f"Hello {user.email}, you are authorized!"})

@api_bp.route("/health")
def health():
    return jsonify({"status": "healthy"})

@api_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"msg": "Missing username, email, or password"}), 400
    if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
        return jsonify({"msg": "Username or Email already exists"}), 409
    user = User(
        username=data["username"],
        password=data["password"],  # Hash in production!
        email=data["email"],
        oauth_provider=None,
        oauth_id=None
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"msg": "Missing username or password"}), 400
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token}), 200

# --- ALL API ROUTES BELOW THIS POINT USE JWT AUTH! ---

@api_bp.route("/summarize", methods=["POST"])
@jwt_required()
def summarize_post():
    print("API endpoint hit!")
    try:
        data = request.get_json(force=True, silent=True)
        print("Parsed input:", data)
        if not (isinstance(data, dict) and "text" in data and isinstance(data["text"], str)):
            return jsonify({"msg": "Bad input: request body must be JSON with 'text' string"}), 400
        text = data["text"]
        user_id = get_jwt_identity()
        from tasks import my_summarize_task
        summary = Summary(text=text, summary="", user_id=user_id)
        db.session.add(summary)
        db.session.commit()
        print("Dispatching celery task!")
        task = my_summarize_task.apply_async(args=[text, summary.id])
        print(f"Task dispatched: {task.id}")
        return jsonify({"task_id": task.id, "summary_id": summary.id}), 202
    except Exception as e:
        traceback.print_exc()
        return jsonify({"msg": str(e)}), 500

@api_bp.route("/task/<string:task_id>", methods=["GET"])
@jwt_required()
def get_task_status(task_id):
    from tasks import my_summarize_task
    task = my_summarize_task.AsyncResult(task_id)
    if task.state == "SUCCESS":
        return jsonify({"state": "SUCCESS", "summary": task.result})
    elif task.state == "FAILURE":
        return jsonify({"state": "FAILURE"}), 500
    return jsonify({"state": task.state})

@api_bp.route("/summaries", methods=["GET"])
@jwt_required()
def get_summaries():
    user_id = get_jwt_identity()
    summaries = Summary.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": s.id,
        "text": s.text,
        "summary": s.summary,
        "created_at": s.created_at
    } for s in summaries])

@api_bp.route("/summary/<int:summary_id>", methods=["GET"])
@jwt_required()
def get_summary_by_id(summary_id):
    summary = Summary.query.get(summary_id)
    if summary:
        return jsonify({
            "id": summary.id,
            "text": summary.text,
            "summary": summary.summary,
            "created_at": summary.created_at
        })
    return jsonify({"msg": "Summary not found"}), 404

@api_bp.route("/summary", methods=["PUT"])
@jwt_required()
def update_summary():
    user_id = get_jwt_identity()
    summary_id = request.json.get("id")
    new_summary = request.json.get("summary")
    if not summary_id or new_summary is None:
        return jsonify({"msg": "Both 'id' and 'summary' fields are required"}), 400
    summary = Summary.query.get(summary_id)
    if not summary or summary.user_id != int(user_id):
        return jsonify({"msg": "Summary not found or unauthorized"}), 404
    summary.summary = new_summary
    db.session.commit()
    return jsonify({"msg": "Summary updated"})

@api_bp.route("/summary/<int:summary_id>", methods=["DELETE"])
@jwt_required()
def delete_summary(summary_id):
    user_id = get_jwt_identity()
    summary = Summary.query.get(summary_id)
    if summary and summary.user_id == int(user_id):
        db.session.delete(summary)
        db.session.commit()
        return jsonify({"msg": "Summary deleted"})
    return jsonify({"msg": "Not found"}), 404

# Register Blueprint to app
app.register_blueprint(api_bp)

from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError

@app.errorhandler(NoAuthorizationError)
def handle_no_auth(e):
    return jsonify({"msg": "No authorization header"}), 401

@app.errorhandler(InvalidHeaderError)
def handle_bad_header(e):
    return jsonify({"msg": "Bad auth header"}), 422

@app.route('/')
def home():
    return "Backend Restored!"

print("Flask server starting, registered routes:", app.url_map)
logging.basicConfig(filename="flask_error.log", level=logging.DEBUG)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)


