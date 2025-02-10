from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import csv
from io import StringIO
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jouw-email@example.com'
app.config['MAIL_PASSWORD'] = 'jouw-wachtwoord'
app.secret_key = 'jouwgeheimesleutel'

mail = Mail(app)
db = SQLAlchemy(app)

class Vacature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    functie = db.Column(db.String(100), nullable=False)
    locatie = db.Column(db.String(100), nullable=False)
    dienstverband = db.Column(db.String(50), nullable=False)

class Sollicitatie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    motivatie = db.Column(db.Text, nullable=False)
    vacature_id = db.Column(db.Integer, db.ForeignKey('vacature.id'), nullable=False)
    goedgekeurd = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vacatures')
def vacatures():
    vacatures = Vacature.query.all()
    return render_template('vacatures.html', vacatures=vacatures)

@app.route('/solliciteren/<int:vacature_id>', methods=['GET', 'POST'])
def solliciteren(vacature_id):
    vacature = Vacature.query.get_or_404(vacature_id)
    if request.method == 'POST':
        naam = request.form['naam']
        email = request.form['email']
        motivatie = request.form['motivatie']
        nieuwe_sollicitatie = Sollicitatie(naam=naam, email=email, motivatie=motivatie, vacature_id=vacature_id)
        db.session.add(nieuwe_sollicitatie)
        db.session.commit()
        flash('Uw sollicitatie is succesvol ingediend!', 'success')
        return redirect(url_for('vacatures'))
    return render_template('solliciteren.html', vacature=vacature)

@app.route('/beheer')
def beheer():
    sollicitaties = Sollicitatie.query.all()
    return render_template('beheer.html', sollicitaties=sollicitaties)

@app.route('/sollicitatie/goedkeuren/<int:id>', methods=['POST'])
def sollicitatie_goedkeuren(id):
    sollicitatie = Sollicitatie.query.get_or_404(id)
    sollicitatie.goedgekeurd = True
    db.session.commit()
    msg = Message('Sollicitatie Goedgekeurd', sender='jouw-email@example.com', recipients=[sollicitatie.email])
    msg.body = f'Beste {sollicitatie.naam},\n\nUw sollicitatie is goedgekeurd! Wij nemen spoedig contact met u op.\n\nMet vriendelijke groet,\nSM Uitzendbureau'
    mail.send(msg)
    flash('Sollicitatie goedgekeurd en e-mail verzonden.', 'success')
    return redirect(url_for('beheer'))

@app.route('/export_sollicitaties')
def export_sollicitaties():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Naam', 'Email', 'Motivatie', 'Vacature ID', 'Goedgekeurd'])
    sollicitaties = Sollicitatie.query.all()
    for s in sollicitaties:
        writer.writerow([s.naam, s.email, s.motivatie, s.vacature_id, s.goedgekeurd])
    output.seek(0)
    return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=sollicitaties.csv'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
