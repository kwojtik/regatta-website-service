from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Regatta, Organizer, Participant, Crew, Boat, Sponsor
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import json
from sqlalchemy import update

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfulyy!', category='success')
                login_user(user, remember=True)

                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be valid.', category='error')
        elif len(first_name) < 2:
            flash('Name must be longer than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            flash('Account created!', category='success')
            #login_user(user, remember=True)
            return redirect(url_for('views.home'))


    return render_template("sign_up.html", user=current_user)

@auth.route('/events/create', methods=['GET', 'POST'])
@login_required
def event_create():
    if request.method == 'POST':
        rname = request.form.get('rname')
        country = request.form.get('country')
        place = request.form.get('place')
        adress = request.form.get('adress')
        rdate = datetime.strptime(request.form.get('rdate'), '%Y-%m-%d')
        rtime = request.form.get('rtime')
        rinfo = request.form.get('reginfo')

        regNameCheck = Regatta.query.filter_by(regname=rname).first()
        if(regNameCheck):
            flash('Regatta with that name already exists!', category='error')
        elif len(rname) < 1:
            flash('Regatta name should be longer than 1 character.', category='error')
        elif not country or not place or not rdate or not rtime:
            flash('Every field should filled', category='error')
        else:
            new_regatta = Regatta(regname=rname, regstart=rtime, regattadate=rdate, country=country, place=place, address=adress, regInfo=rinfo)
            db.session.add(new_regatta)
            db.session.commit()

            userid = current_user.id
            regid = db.select(Regatta.id).filter_by(regname=rname)

            for i in range(1, 6):
                sponsorName = request.form.get(f'sponsorName_{i}')
                donation = request.form.get(f'donation_{i}')

                if sponsorName and donation:
                    new_sponsor = Sponsor(sponsor_name=sponsorName, donation=donation, regatta_id=regid)
                    db.session.add(new_sponsor)
                    db.session.commit()

            new_organizer = Organizer(user_id=userid, regatta_id=regid)
            db.session.add(new_organizer)
            db.session.commit()

            flash('Regatta created!', category='success')

            return redirect(url_for('views.events'))
        
    return render_template("event_create.html", user=current_user)


@auth.route('/events/sign_up/<int:regatta_id>', methods=['GET', 'POST'])
@login_required
def event_signup(regatta_id):
    regatta = Regatta.query.get(regatta_id)   

    if request.method == 'POST':
        crewName = request.form.get('crewName')
        members = request.form.getlist('member')
        boatName = request.form.get('boatName')
        boatModel = request.form.get('boatModel')
        boatType = request.form.get('boatType')
        boatRegNo = request.form.get('boatRegNo')

        tmp = True

        if not crewName or not boatName or not boatModel or not boatType  or not boatRegNo:
            flash('All fields should be filled', category='error')
            tmp = False
        else:
            findBoatId = Boat.query.filter_by(reg_no=boatRegNo).first()
            boatid = db.select(Boat.id).filter_by(reg_no=boatRegNo)

            if not findBoatId:
                new_Boat = Boat(boat_name=boatName, model=boatModel, type=boatType, reg_no=boatRegNo)
                db.session.add(new_Boat)
                db.session.commit()
                boatid = db.select(Boat.id).filter_by(reg_no=boatRegNo)
            else:
                update(Boat).where(id == boatid).values(boat_name=boatName, model=boatModel, type=boatType)
                db.session.commit()


            new_crew = Crew(crew_name=crewName, regatta_id=regatta_id, boat_id=boatid)
            db.session.add(new_crew)
            db.session.commit()

            findCrewId = Crew.query.filter_by(crew_name=crewName, regatta_id=regatta_id).first()

            for i in range(len(members)):
                crewMate = User.query.filter_by(email=members[i]).first()
                if crewMate:
                    new_Participant = Participant(user_id=crewMate.id, crew_id=findCrewId.id)
                    db.session.add(new_Participant)
                    db.session.commit()
                else:
                    tmp = False
                    flash('User doesn\'t exists.', category='error')

            if tmp: 
                flash('Registered!', category='success')


    return render_template('event_sign_up.html', user=current_user, regatta=regatta)

