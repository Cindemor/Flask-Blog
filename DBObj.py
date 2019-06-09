from db import db

class DBObject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sitename = db.Column(db.String(20))
    pic_url = db.Column(db.Text)
