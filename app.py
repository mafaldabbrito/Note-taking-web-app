# app.py
from flask import Flask, render_template , url_for, request, redirect        # import flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)             # create an app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Note %r>' % self.id

@app.route("/", methods=['GET', 'POST'])                  
def index():
    if request.method == 'POST':
        note_content = request.form['content']
        new_note = Note(content=note_content)
        
        try:
            db.session.add(new_note)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your note'
        
    else:
        notes = Note.query.order_by(Note.date_created).all()
        return render_template('index.html', notes=notes)
    

@app.route('/delete/<int:id>')
def delete(id):
    note_to_delete = Note.query.get_or_404(id)
    
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that note'

@app.route('/edit/<int:id>', methods= ['GET', 'POST'])
def edit (id):
    
    note = Note.query.get_or_404(id)
    
    if request.method == 'POST':
        note.content = request.form['content']
        
        try: 
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue editing your note'
    else:
        return render_template('edit.html', note=note)
                    
            
if __name__ == "__main__":        # on running python app.py
    app.run(debug=True)                     # run the flask app
    