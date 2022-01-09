import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from auth import app, db, bcrypt
from auth.forms import(LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, RegistrationForm) #this needs to be updated
from auth.models import User #this needs to be updated
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from auth.recognizer import Recognizer #facial recognition

@app.route("/")

@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact Us')

@app.route("/viewaccount")
def viewaccount():
    return render_template('viewaccount.html', title='View Profile')

@app.route("/welcome")
def welcome():
    return render_template('welcome.html')



@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            name = Recognizer()
            if len(name)==0:
                flash('Face Not Found.', 'danger')
            else:
                if user.image_file == name[0]:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash('Login Successful, Your Face was Successfully Verified.', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('welcome'))
                else:
                    flash('Login Unsuccessful. User Face Not Found.', 'danger')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
            os.remove(picture_path)
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            current_user.face_reco_id = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.account = form.account.data
        current_user.debit = form.debit.data
        db.session.commit()
        flash('Your account has been updated successfully', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('You have entered an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated successfully', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        image_file = 0
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            image_file = picture_file
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if image_file == 0:
            flash('Please Upload Your Profile Picture.', 'danger')
            return redirect(url_for('register'))
            #user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        else:
            user = User(username=form.username.data, email=form.email.data, phone=form.phone.data, address=form.address.data, account=form.account.data, debit=form.debit.data, password=hashed_password, image_file = image_file, face_reco_id = image_file)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='noreply@demo.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('reset_token', token=token, _external=True)}
# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)
	pass
