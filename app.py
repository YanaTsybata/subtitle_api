from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import csv
from io import StringIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subtitles.db'
db = SQLAlchemy(app)

class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sequence_number = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.Float, nullable=False)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Subtitle {self.id}: {self.text[:20]}...>'

# subtitles tracking:
current_subtitle_index = 0

@app.route('/')
def home():
    with open('templates/index.html', 'r') as file:
        template = file.read()
    return render_template_string('index.html')

@app.route('/api/subtitles/upload', methods=['POST'])
def upload_subtites():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        #read csv
        stream = StringIO(data)
        csv_reader = csv.DictReader(stream)

        for row in csv_reader:
            new_subtitle = Subtitle(
                sequence_number=int(row['sequence_number']),
                start_time=float(row['start_time']),
                end_time=float(row['end_time']),
                text=row['text'],
                language=row['language']
            )
            db.session.add(new_subtitle)
        db.session.commit()
        return jsonify({'message': 'Subtitles uploaded succesfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)