from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

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

current_subtitle_index = 0

def clear_database():
    try:
        num_deleted = db.session.query(Subtitle).delete()
        db.session.commit()
        print(f"The database has been cleared. {num_deleted} entries deleted")
    except Exception as e:
        print(f"Error while clearing data: {str(e)}")
        db.session.rollback()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/display')
def display():
    return render_template('subtitle_display.html')

@app.route('/control')
def control():
    return render_template('subtitle_control.html')

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
                language='de'
            )
            db.session.add(new_subtitle)

        db.session.commit()
        print(f"Loaded {len(lines)} subtitles \n Загружено {len(lines)} субтитров")
        return jsonify({'message': f'Subtitles successfully loaded. Total: {len(lines)} \n Субтитри успішно завантажено. Всього: {len(lines)}'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error loading subtitles: {str(e)} Ошибка при загрузке субтитров: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/subtitles/current', methods=['GET'])
def get_current_subtitle():
    global current_subtitle_index
    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    if not subtitles:
        return jsonify({'message': 'No subtitles available \n Немає доступних субтитрів'}), 404
    if current_subtitle_index >= len(subtitles):
        current_subtitle_index = len(subtitles) - 1
    subtitle = subtitles[current_subtitle_index]
    return jsonify({
        'id': subtitle.id,
        'text': subtitle.text,
        'language': subtitle.language,
        'sequence_number': subtitle.sequence_number,
        'start_time': subtitle.start_time,
        'end_time': subtitle.end_time,
        'message': 'Current subtitle \n Поточний субтитр'
    }), 200

@app.route('/api/subtitles/advance', methods=['POST'])
def advance_subtitle():
    global current_subtitle_index
    subtitles = Subtitle.query.order_by(Subtitle.sequence_number).all()
    if not subtitles:
        return jsonify({'message': 'No subtitles available \n Немає доступних субтитрів'}), 404
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
            'message': 'Moved to the next subtitle \n Перейшли до наступного субтитру'
        }), 200
    else:
        return jsonify({'message': 'End of subtitles reached \n Досягнуто кінця субтитрів'}), 200

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

@app.route('/api/subtitles/reset', methods=['POST'])
def reset_subtitle_index():
    global current_subtitle_index
    current_subtitle_index = 0
    return jsonify({'message': 'Subtitle index reset \n Індекс субтитрів скинуто'}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        should_clear = os.environ.get('CLEAR_DB_ON_STARTUP', 'true').lower()
        print(f"CLEAR_DB_ON_STARTUP installed in: {should_clear}")
        if should_clear == 'true':
            clear_database()
        else:
            print("The database is not cleared on startup. \n База даних не очищена під час запуску.")
        print(f"Total subtitles in the database: {Subtitle.query.count()} \n Усього субтитрів у базі: {Subtitle.query.count()}")
    app.run(host='0.0.0.0', port=5001, debug=True)