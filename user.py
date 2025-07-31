from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os #works with file paths and fodler creation
import fitz  # PyMuPDF-extracts text from pdfs
import docx #reads .docx files
from datetime import datetime
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    surname = db.Column(db.Text, nullable=False)
    userType = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<User {self.name} {self.surname} – {self.userType}>'
# Create DB tables
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        user_type = request.form['userType']

        new_user = User(name=name, surname=surname, userType=user_type)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('register'))

    return render_template('user/register.html')
if __name__ == '__main__':
    app.run(debug=True)
