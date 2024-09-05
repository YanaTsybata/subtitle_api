from flask import Flask, request, jsonify, render_template
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
    return render_template('index.html')

@app.route('/api/subtitles/upload', methods=['POST'])
def upload_subtitles():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        lines = data.strip().split('\n')
        
        for i, line in enumerate(lines, start=1):
            new_subtitle = Subtitle(
                sequence_number=i,
                start_time=float(i),
                end_time=float(i+1),
                text=line.strip(),
                language='auto'
            )
            db.session.add(new_subtitle)

        db.session.commit()
        return jsonify({'message': 'Субтитри успішно завантажено'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# get subtitle
@app.route('/api/subtitles/next', methods=['GET'])
def get_current_subtitle():
    global current_subtitle_index
    subtitle = Subtitle.query.order_by(Subtitle.sequence_number).offset(current_subtitle_index).first()
    if subtitle:
        return jsonify({
            'id': subtitle.id,
            'text': subtitle.text,
            'language': subtitle.language,
            'sequence_number': subtitle.sequence_number,
            'start_time': subtitle.start_time,
            'end_time': subtitle.end_time
        }), 200
    else:
        return jsonify({'message': 'Немає доступних субтитрів'}), 404

@app.route('/api/subtitles/advance', methods=['POST'])
def advance_subtitle():
    global current_subtitle_index    
    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    
    if current_subtitle_index < len(subtitles) - 1:
        current_subtitle_index += 1
        subtitle = subtitles[current_subtitle_index]
        return jsonify({
            'id': subtitle.id,
            'text': subtitle.text,
            'language': subtitle.language,
            'sequence_number': subtitle.sequence_number,
            'start_time': subtitle.start_time,
            'end_time': subtitle.end_time,
            'message': 'Advanced to next subtitle'
        }), 200
    else:

        current_subtitle_index = len(subtitles) - 1
        return jsonify({'message': 'Reached the end of subtitles'}), 200

# all subtitles
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
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)