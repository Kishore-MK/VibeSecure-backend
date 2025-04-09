from flask_sqlalchemy import SQLAlchemy
import os
from git import Repo, GitCommandError

import uuid

from extensions import db
from models import  Run



class RepositoryHandler:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.query.all()

    def get_by_id(self, id):
        return self.model.query.get(id)

    def create(self, data):
        new_record = self.model(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    def update(self, id, data):
        record = self.get_by_id(id)
        if record:
            for key, value in data.items():
                setattr(record, key, value)
            db.session.commit()
        return record

    def delete(self, id):
        record = self.get_by_id(id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
    
def clone_repo(repo_url, run_id, user, token=None, base_path="workspace"):
    path = os.path.join(base_path, run_id)
    os.makedirs(base_path, exist_ok=True)

    if token:
        # Inject token into HTTPS repo URL
        if repo_url.startswith("https://github.com/"):
            repo_url = repo_url.replace("https://", f"https://{token}@")
        else:
            raise ValueError("Repo URL must be HTTPS for token auth")

    try:
        print(f"🔄 Cloning {repo_url} into {path}...")
        Repo.clone_from(repo_url, path)
        print(f"✅ Cloned successfully.")
    except GitCommandError as e:
        print(f"❌ Git error: {e.stderr or str(e)}")
        raise

    user_id = user["id"]
    run = Run(repo_url=repo_url, run_id=run_id, user_id=user_id)
    db.session.add(run)
    db.session.commit()

    return run, path
