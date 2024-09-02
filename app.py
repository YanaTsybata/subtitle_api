from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLAlALCHEMY_DATABASE_URI'] = 'sqlite:///subtitles.db'
db = SQLAlchemy(app)

class Subtitles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sequence_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Subtitle {self.id}: {self.text[:20]}...>'

# get subtitle
@app.route('/api/subtitles/next', methods=['GET'])
def get_next_subtitle():
    current_subtitle = Subtitle.query.order_by(Subtitle.sequence_number).first()
    if current_subtitle:
        return jsonify({
            'id': current_subtitle.id,
            'text': current_subtitle.text,
            'language': current_subtitle.language
        })
    else:
        return jsonify({'message': 'No subtitles available'}),

@app.route('/api/subtitles/advance', methods=['Post'])
def advance_subtitle():
    pass

# add new subtitle
@app.route('/api/subtitles', methods=['POST'])
def add_subtitle():
    pass

# all subtitless
@app.route('/api/subtitles', methods=['GET'])
def get_all_subtitles():
    pass

@app.route('/')
def home():
    return '<h1>FLASK REST API</h1>'


if __name__ == "__main__":
    app.run(debug=True)