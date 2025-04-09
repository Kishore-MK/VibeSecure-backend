# models.py
from extensions import db
from datetime import datetime


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repo_url = db.Column(db.String, nullable=False)
    run_id = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.String(200), nullable=False)  
    __table_args__ = (
        db.UniqueConstraint('repo_url', name='uq_repo_url'),
        db.UniqueConstraint('run_id', name='uq_run_id'),
    )

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('run.id'))
    tool = db.Column(db.String(64))
    severity = db.Column(db.String(16))
    file_path = db.Column(db.String(512))
    line = db.Column(db.Integer)
    message = db.Column(db.Text)

    run = db.relationship("Run", backref=db.backref("issues", lazy=True))
   