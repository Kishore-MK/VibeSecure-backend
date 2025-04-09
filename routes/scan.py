# routes/scan.py
import hashlib
import os
from flask import Blueprint, request, jsonify,session
from services.repo_handler import clone_repo
from services.tool_runner import run_bandit, run_flake8, run_radon
from models import Run, Issue
from extensions import db

bp = Blueprint("scan", __name__, url_prefix="/scan")


@bp.route("/issues/<string:run_id>")
def get_issues(run_id):
    run = Run.query.filter_by(run_id=run_id).first()
    from models import Issue
    results = Issue.query.filter_by(run_id=run.id).all()
    return jsonify([
        {
            "tool": i.tool,
            "severity": i.severity,
            "file": i.file_path,
            "line": i.line,
            "message": i.message
        } for i in results
    ])

@bp.route("/submit", methods=["POST"])
def submit_repo():
    data = request.json
    repo_url = data.get("repo_url")
    if not repo_url:
        return {"error": "No repo_url provided"}, 400
    
    if not repo_url.endswith(".git"):
        repo_url += ".git"

    existing_run = Run.query.filter_by(repo_url=repo_url).first()
    if existing_run:
        run_id = existing_run.run_id
        issues = Issue.query.filter_by(run_id=existing_run.id).all()
        path = os.path.join("workspace", run_id)
        if os.path.exists(path) and os.path.isdir(os.path.join(path, ".git")):
            print(f"✅ Repo already cloned at {path}, skipping.")
            return {
        "run_id": existing_run.run_id,
        "issue_count": len(issues)
    }, 200
        else:
            print(f"⚠️ Record exists, but folder is missing. Re-cloning.")

    run_id = get_repo_hash(repo_url)
    
    user = session.get("user")
    if not user:
        print("⚠️ User not authenticated.")
        return {"error": "Unauthorized"}, 401
    run, path = clone_repo(repo_url,run_id,user)

    # Run tools
    issues = run_bandit(path) + run_flake8(path) + run_radon(path)

    # Insert issues into DB
    for issue in issues:
        db_issue = Issue(
            run_id=run.id,
            tool=issue["tool"],
            file_path=issue["file"],
            line=issue["line"],
            severity=issue["severity"],
            message=issue["message"]
        )
        db.session.add(db_issue)
    db.session.commit()

    return {
        "run_id": run.run_id,
        "issue_count": len(issues)
    }, 200

def get_repo_hash(repo_url):
    return hashlib.sha256(repo_url.encode()).hexdigest()[:12]

@bp.route("/runs", methods=["GET"])
def get_user_runs():
    user = session.get("user")
    if not user:
        return {"error": "Unauthorized"}, 401
    
    runs = Run.query.filter_by(user_id=user["id"]).order_by(Run.created_at.desc()).limit(5).all()

    return jsonify([
        {
            "repo_url": run.repo_url,
            "run_id": run.run_id,
            "created_at": run.created_at.isoformat()
        }
        for run in runs
    ])