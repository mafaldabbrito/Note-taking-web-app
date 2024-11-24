# app.py
from flask import Flask, render_template , url_for, request, redirect        # import flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)             # create an app instance

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'









class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Note %r>' % self.id
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    
    
    def __repr__(self):
        return '<User %r>' % self.id
    
    
class ResgisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/home')
            else:
                return 'Invalid Password'
    
    
    
    return render_template("login.html" , form=form)

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route("/register", methods=['GET', 'POST'])
def register():
    
    form = ResgisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    
    
    return render_template("register.html", form=form)



@app.route("/home", methods=['GET', 'POST'])
@login_required          
def home():
    if request.method == 'POST':
        note_title = request.form['title']
        note_content = request.form['content']
        new_note = Note(content=note_content, title=note_title)
        
        try:
            db.session.add(new_note)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your note'
        
    else:
        notes = Note.query.order_by(Note.date_created).all()
        return render_template('home.html', notes=notes)
    

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    note_to_delete = Note.query.get_or_404(id)
    
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that note'

@app.route('/edit/<int:id>', methods= ['GET', 'POST'])
@login_required
def edit (id):
    
    note = Note.query.get_or_404(id)
    
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        
        try: 
            db.session.commit()
            return redirect('/view/'+str(note.id))
        except:
            return 'There was an issue editing your note'
    else:
        return render_template('edit.html', note=note)
                    
                    
@app.route('/view/<int:id>', methods= ['GET'])
@login_required
def view (id):
    
    note = Note.query.get_or_404(id)
    
    if request.method == 'GET':
        return render_template('view.html', note=note)
                    
            
if __name__ == "__main__":        # on running python app.py
    app.run(debug=True)                     # run the flask app
    