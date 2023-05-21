from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Regatta, Sponsor, Organizer, User, Crew, Participant
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note') 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)

            db.session.add(new_note)
            db.session.commit()

            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    regatta = db.session.query(Regatta).all()
    return render_template("events.html", user=current_user, regatta=regatta)

@views.route('/archive', methods=['GET', 'POST'])
@login_required
def archive():
    return render_template("archive.html", user=current_user)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/events/info/<int:regatta_id>', methods=['GET', 'POST'])
@login_required
def event_info(regatta_id):
    regatta = Regatta.query.filter_by(id=regatta_id).first()
    sponsors = Sponsor.query.filter_by(regatta_id=regatta_id)

    orgId = db.select(Organizer.user_id).filter_by(regatta_id=regatta_id)
    orgInfo = User.query.filter_by(id=orgId).first()

    crews = Crew.query.filter_by(regatta_id=regatta_id)

    return render_template("event_info.html", user=current_user, regatta=regatta, sponsors=sponsors, organizer=orgInfo, crews=crews)