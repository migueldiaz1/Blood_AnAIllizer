import os
import json
import tempfile
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# --- ¡NUEVAS IMPORTACIONES! ---
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from datetime import datetime, timezone

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- ¡NUEVA CONFIGURACIÓN! ---
# Lee la configuración desde las variables de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar las extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- ¡NUEVOS MODELOS DE BASE DE DATOS! ---
# Reemplazan a users.json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    # ¡Guardamos la contraseña hasheada, NUNCA en texto plano!
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # Relación: Un usuario puede tener muchas entradas de timeline
    timelines = db.relationship('Timeline', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Reemplaza a timeline_data.json
class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    # Usamos el tipo JSON nativo de PostgreSQL para guardar los resultados
    results = db.Column(db.JSON, nullable=True)
    # Clave foránea para vincular con el usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Timeline {self.id} for User {self.user_id}>'
    
    # Función para convertir el objeto a un diccionario (para JSON)
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'results': self.results,
            'user_id': self.user_id
        }

# --- ENDPOINTS DE API (Re-escritos) ---

@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'error': 'El usuario o email ya existe'}), 409

        # Hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Crear nuevo usuario
        new_user = User(
            username=username,
            email=email,
            name=name,
            password_hash=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()

        # Crear un token de acceso para el nuevo usuario
        access_token = create_access_token(identity={'id': new_user.id, 'username': new_user.username})
        
        return jsonify({
            'success': True,
            'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email},
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        user = User.query.filter_by(username=username).first()

        # Verificar usuario y contraseña hasheada
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Crear y devolver token de acceso
            access_token = create_access_token(identity={'id': user.id, 'username': user.username})
            return jsonify({
                'success': True,
                'user': {'id': user.id, 'username': user.username, 'email': user.email},
                'access_token': access_token
            })
        
        return jsonify({'error': 'Credenciales inválidas'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Endpoints de Timeline (¡Ahora Seguros!) ---

@app.route('/api/timeline', methods=['GET'])
@jwt_required()  # <-- ¡Esto protege la ruta!
def get_timeline():
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']

        # Buscar las entradas de timeline solo para este usuario
        timeline_entries = Timeline.query.filter_by(user_id=user_id).order_by(Timeline.date.asc()).all()
        
        # Convertir a formato JSON
        timeline_data = [entry.to_dict() for entry in timeline_entries]
        
        return jsonify({'success': True, 'timeline': timeline_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-timeline', methods=['POST'])
@jwt_required()  # <-- ¡Esto protege la ruta!
def save_timeline():
    try:
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']
        
        data = request.json
        timeline_data = data.get('timeline', []) # Se espera una lista de resultados

        # El frontend parece guardar toda la timeline junta, 
        # pero una mejor API guardaría una entrada a la vez.
        # Asumiendo que `data` es UNA entrada de timeline
        # (Basado en tu main.js que parece agregar una a la vez)
        
        new_entry = Timeline(
            date=datetime.fromisoformat(data.get('date')),
            results=data.get('results'), # El objeto JSON con los resultados
            user_id=user_id
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Timeline guardado', 'entry': new_entry.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# --- Tus otros endpoints (no necesitan cambios por ahora) ---

@app.route('/api/analyze', methods=['POST'])
@jwt_required() # <-- ¡Protegido!
def analyze_reports():
    # ... (Tu lógica de análisis de PDF) ...
    # (El resto de tu código de mock analysis está bien para probar)
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        report_date = request.form.get('date', pd.Timestamp.now().strftime('%Y-%m-%d'))
        
        # ... (Mock results) ...
        mock_results = generate_mock_analysis(files[0].filename, report_date)
        
        return jsonify({
            'success': True,
            'results': mock_results,
            'summary': calculate_summary(mock_results),
            'report_date': report_date
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
@jwt_required() # <-- ¡Protegido!
def generate_pdf():
    # ... (Tu lógica de generación de PDF) ...
    return send_file(tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name, 
                     as_attachment=True, download_name='mock_report.pdf')

# --- Funciones Mock (sin cambios) ---
def generate_mock_analysis(filename, date):
    return [
        {'test': 'Glucose', 'value': 95, 'unit': 'mg/dL', 'refLow': 70, 'refHigh': 100, 'status': 'Normal', 'file': filename, 'date': date},
        {'test': 'Cholesterol Total', 'value': 185, 'unit': 'mg/dL', 'refLow': 0, 'refHigh': 200, 'status': 'Normal', 'file': filename, 'date': date},
    ]
def calculate_summary(results):
    return {'normal': len(results), 'near': 0, 'abnormal': 0, 'total': len(results)}
def generate_mock_pdf(report_type, results):
    return b'Mock PDF content'

# --- Configuración de arranque ---
if __name__ == '__main__':
    # Creará las tablas si no existen antes del primer request
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)