from app import db

class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sequence_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Subtitle {self.id}: {self.text[:20]}...>'