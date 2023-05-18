from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Regatta, Organizer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime

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

        if len(rname) < 1:
            flash('Regatta name should be longer than 1 character.', category='error')
        elif not country or not place or not rdate or not rtime:
            flash('Every field should filled', category='error')
        else:
            new_regatta = Regatta(regname=rname, regstart=rtime, regattadate=rdate, country=country, place=place, address=adress)
            db.session.add(new_regatta)
            db.session.commit()

            userid = current_user.id
            regid = db.select(Regatta.id).filter_by(regname=rname)
            #regid = reg.id

            new_organizer = Organizer(user_id=userid, regatta_id=regid)
            db.session.add(new_organizer)
            db.session.commit()

            flash('Regatta created!', category='success')

            return redirect(url_for('views.events'))
        
    return render_template("event_create.html", user=current_user)