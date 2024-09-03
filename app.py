from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subtitles.db'
db = SQLAlchemy(app)

class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sequence_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Subtitle {self.id}: {self.text[:20]}...>'

# subtitles tracking:
current_subtitle_index = 0


# get subtitle
@app.route('/api/subtitles/next', methods=['GET'])
def get_next_subtitle():
    global current_subtitle_index
    
    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    
    if current_subtitle_index < len(subtitles):

        current_subtitle = subtitles[current_subtitle_index]

        return jsonify({
            'id': current_subtitle.id,
            'text': current_subtitle.text,
            'language': current_subtitle.language,
            'sequence_number': current_subtitle.sequence_number
        })
    else:
        return jsonify({'message': 'No more subtitles available'}), 404


@app.route('/api/subtitles/advance', methods=['Post'])
def advance_subtitle():
    global current_subtitle_index
    current_subtitle_index += 1

    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    
    if current_subtitle_index < len(subtitles):

        return jsonify({'message': 'Advanced to next subtitle'}), 200
    else:

        current_subtitle_index = len(subtitles) - 1
        return jsonify({'message': 'Reached the end of subtitles'}), 200


# add new subtitle
@app.route('/api/subtitles', methods=['POST'])
def add_subtitle():
    data = request.json

    if not all(key in ('text', 'language', 'sequence_number')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_subtitle = Subtitle(
        text=data['text'],
        language=data['language'],
        sequence_number=data['sequence_number']
    )

    db.session.add(new_subtitle)
    db.session.commit()

    return jsonify({
        'id': new_subtitle.id,
        'text': new_subtitle.text,
        'language': new_subtitle.language,
        'sequence_number': new_subtitle.sequence_number
    }), 201  

# all subtitless
@app.route('/api/subtitles', methods=['GET'])
def get_all_subtitles():
 
    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    
    subtitles_list = [{
        'id': subtitle.id,
        'text': subtitle.text,
        'language': subtitle.language,
        'sequence_number': subtitle.sequence_number
    } for subtitle in subtitles]

    return jsonify(subtitles_list)


@app.route('/')
def home():
    return '<h1>FLASK REST API</h1>'


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    