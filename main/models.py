from main import db
from flask_sqlalchemy import SQLAlchemy


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Text)
    send_message = db.Column(db.Text)
    read_title = db.Column(db.Text)
    read_image_url = db.Column(db.Text)
    is_good = db.Column(db.Text)
    read_date = db.Column(db.Text)

    def __repr__(self):
        return """
        Entry id: {} send_message: {} read_title: {}
        read_image_url: {} is_good: {} read_date: {}"
        """.format(self.id, self.send_message, self.read_title, self.read_image_url, self.is_good, self.read_date)
def init():
    db.create_all()