import datetime
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from nts import app, db, bcrypt, mail
from nts.forms import (RegistrationForm, LoginForm, AddNoteForm, EditNoteForm, RequestResetForm,
                ResetPasswordForm, DeleteForm, AccountSettings, ProfileSettings, SecuritySettings)
from nts.models import User, Note
from nts.functions import note_picture, save_picture, override_url_for, delete_image
#from flask_mail import Message


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('notes'))
    return render_template('home.html', title='Home')


@app.route('/note/add', methods=['GET', 'POST'])
@login_required
def notes_add():
    form = AddNoteForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = note_picture(form.picture.data)
            note = Note(title=form.title.data, content=form.content.data,
                        privacy=form.privacy.data, author=current_user, image_file=picture_file)
            flash('Note has been created', 'success')
            db.session.add(note)
            db.session.commit()
            return redirect(url_for('note', note_id=note.id))
        else:
            note = Note(title=form.title.data, content=form.content.data,
                        privacy=form.privacy.data, author=current_user)
            flash('Note has been created', 'success')
            db.session.add(note)
            db.session.commit()
            return redirect(url_for('note', note_id=note.id))
    return render_template('notes/add.html', title='Add', form=form)


@app.route('/note/<int:note_id>')
def note(note_id):
    note = Note.query.get_or_404(note_id)
    token = note.get_share_token()
    if note.privacy == 'Private':
        if current_user == note.author:
            return render_template('notes/note.html', title='Note', note=note, token=token)
        else:
            flash('This note is not avaliable for you.' , 'danger')
            return redirect(url_for('home', access='fail'))
    else:
        return render_template('notes/note.html', title='Note', note=note, token=token)


@app.route('/note/share/<int:note_id>/<token>')
def share(note_id, token):
    note = Note.query.get_or_404(note_id)
    token = Note.verify_share_token(token)
    if token is None:
        flash('INVALID SHARE TOKEN', 'danger')
        return redirect(url_for('notes'))
    return render_template('notes/note.html', title='Share Note', note=note)


@app.route('/note/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def note_edit(note_id):
    form = EditNoteForm()
    note = Note.query.get_or_404(note_id)
    date = datetime.datetime.now()
    if note.author == current_user:
        if form.validate_on_submit():
            note.title = form.title.data
            note.content = form.content.data
            note.privacy = form.privacy.data
            note.author = current_user
            if form.picture.data:
                pic = note_picture(form.picture.data)
                note.image_file = pic
            db.session.commit()
            flash(f'Your note ["{note.title}"] has been updated.', 'success')
            return redirect(url_for('notes'))
        elif request.method == 'GET':
            form.title.data = note.title
            form.content.data = note.content
            form.privacy.data = note.privacy
    else:
        return redirect(url_for('notes'))
    return render_template('notes/edit.html', title="Edit", form=form, date=date, note=note)


@app.route('/note/delete/<int:note_id>', methods=['POST', 'GET'])
@login_required
def note_delete(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author == current_user:
        if note.image_file:
            file = note.image_file
            location = 'nts/static/note_background'
            delete_image(location, file)
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted.', 'info')
        return redirect(url_for('notes'))
    else:
        flash('An error occurred.', 'danger')
        return redirect(url_for('notes'))


@app.route('/notes')
@login_required
def notes():
    notes = Note.query.filter_by(
        author=current_user).all()
    return render_template('notes/notes.html', title='Notes', notes=notes)


@app.route('/notes/dashboard')
@login_required
def dash_notes():
    notes = Note.query.filter_by(
        author=current_user).order_by(Note.date_posted.desc())
    return render_template('notes/dashboard.html', title='Dashboard', notes=notes)


@app.route('/notes/dashboard/search')
@login_required
def dash_search():
    q = request.args.get('q')
    if q:
        notes = Note.query.filter_by(author=current_user).order_by(Note.date_posted.desc()).filter(Note.title.contains(q)
            | Note.content.contains(q)
            | Note.date_posted.contains(q) 
            | Note.id.contains(q)
        ).order_by(Note.date_posted.desc())
    else:
        notes = Note.query.filter_by(author=current_user).order_by(Note.date_posted.desc())
    return render_template('notes/dashboard_search.html', title='Dash/Search', notes=notes, q=q)


@app.route('/browse', methods=['POST', 'GET'])
def browse():
    notes = Note.query.filter_by(privacy='Public').order_by(Note.date_posted.desc()).all()
    return render_template('browse.html', notes=notes, title='Browse')


@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    if q:
        notes = Note.query.filter_by(privacy='Public').order_by(Note.date_posted.desc()).filter(Note.title.contains(q)
            | Note.content.contains(q)
            | Note.date_posted.contains(q) 
            | Note.id.contains(q)
        ).order_by(Note.date_posted.desc())
    else:
        notes = Note.query.filter_by(privacy='Public').order_by(Note.date_posted.desc())
    data = datetime.date.today()
    return render_template('search.html', title='Search', notes=notes, data=data, result=q)


# account path
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('account/login.html', title='Login', form=form, form3=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('account/register.html', title='Register', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/User/<string:username>')
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    notes = Note.query.filter_by(author=user).all()
    last_notes = Note.query.filter_by(privacy='Public').order_by(Note.date_posted.desc())
    return render_template('account/user.html', user=user, notes=notes, last_notes=last_notes, title='User')


@app.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileSettings()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
    image_file = url_for(
        'static', filename="profile_pics/" + current_user.image_file)
    return render_template('account/settings/profile_settings.html', title="Settings", form=form, image_file=image_file)


@app.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountSettings()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash('Please check form errors.', 'danger')
    return render_template('account/settings/account_settings.html', title="Settings", form=form)


@app.route('/settings/account/delete', methods=['GET', 'POST'])
@login_required
def delete_ac():
    form = DeleteForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password, form.password.data):
                user = current_user
                notes = Note.query.filter_by(author=user).delete()
                if user.image_file != 'default.jpg':
                    # to change
                    # location = r'C:\Users\Ja\Desktop\notesaver\nts\static\profile_pics'
                    location = '/nts/static/profile_pics'
                    file = user.image_file
                    delete_image(location, file)
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for('notes'))
            else:
                flash('Wrong password !' , 'danger')
        else:
            flash('Some error occurred' , 'danger')
    return render_template('account/settings/delete.html', form=form)


@app.route('/settings/security', methods=['GET', 'POST'])
@login_required
def security():
    form = SecuritySettings()
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)   
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Password changed!', 'success')
        else:
            flash('Password change fail. Check your password.', 'danger')
    return render_template('account/settings/security_settings.html', title="Settings", form=form, ip=ip_address)



def send_reset_email(user):
    #token = user.get_reset_token()
    #msg = Message('(noteSaver) Password Reset Request',
    #              sender='zsforum12@gmail.com', recipients=[user.email])
    #msg.body = f'''Enter this link to resert your password:
    #{url_for('reset_token', token=token, _external=True)}
    #If you did not requested this just ignore it.
#   '''
    #mail.send(msg)
    print('no email info')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login', password_reset="true"))
    return render_template('account/reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('account/reset_token.html', title='Reset Password', form=form)
# end of account path


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
