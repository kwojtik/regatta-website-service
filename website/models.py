from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Regatta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regname = db.Column(db.String(256))
    regstart = db.Column(db.Time)
    regattadate = db.Column(db.Data)
    country = db.Column(db.String(100))
    place = db.Column(db.String(100))
    address = db.Column(db.String(100))

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_name = db.Column(db.String(100))
    donation = db.Column(db.Integer)
    regatta_id = db.Column(db.Integer, db.ForeignKey('regatta.id'))

class Organizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    regatta_id = db.Column(db.Integer, db.ForeignKey('regatta.id'))

class Boat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boat_name = db.Column(db.String(100))
    model = db.Column(db.String(100))
    type = db.Column(db.String(100))
    reg_no = db.Column(db.String(20))

class Crew(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crew_name = db.Column(db.String(100))
    regatta_id = db.Column(db.Integer, db.ForeignKey('regatta.id'))
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'))

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placement = db.Column(db.Integer)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))
    regatta_id = db.Column(db.Integer, db.ForeignKey('regatta.id'))