from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import qrcode
import uuid
import os
import io
import base64
from datetime import datetime, timedelta
import hashlib
import time
import secrets

app = Flask(__name__)
CORS(app, origins="*")


TOKENS = {}

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'rootpassword'),
        database=os.environ.get('DB_NAME', 'attendance_db')
    )

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            role ENUM('admin','instructor','student') NOT NULL DEFAULT 'student',
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100) UNIQUE NOT NULL,
            course_name VARCHAR(100) NOT NULL,
            instructor_id VARCHAR(50) NOT NULL,
            qr_token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_attendance (student_id, session_id)
        )
    """)
    try:
        cursor.execute(
            "INSERT IGNORE INTO users (user_id, name, email, role, password_hash) VALUES (%s,%s,%s,%s,%s)",
            ('admin', 'Admin', 'admin@pharos.edu', 'admin', hash_pw('admin123'))
        )
    except:
        pass
    conn.commit()
    cursor.close()
    conn.close()


def get_current_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    return TOKENS.get(token)

def require_role(*roles):
    u = get_current_user()
    if not u:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    if u['role'] not in roles:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    return None


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id=%s AND password_hash=%s", (user_id, hash_pw(password)))
    user = cursor.fetchone()
    cursor.close(); conn.close()
    if user:
        token = secrets.token_hex(32)
        TOKENS[token] = {'user_id': user['user_id'], 'name': user['name'], 'role': user['role']}
        return jsonify({'success': True, 'token': token, 'user_id': user['user_id'], 'name': user['name'], 'role': user['role']})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    TOKENS.pop(token, None)
    return jsonify({'success': True})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    u = get_current_user()
    if not u:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    data = request.json
    old_pw = data.get('old_password', '').strip()
    new_pw = data.get('new_password', '').strip()
    if len(new_pw) < 4:
        return jsonify({'success': False, 'message': 'Password must be at least 4 characters'}), 400
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id=%s AND password_hash=%s", (u['user_id'], hash_pw(old_pw)))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
    cursor.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (hash_pw(new_pw), u['user_id']))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'success': True, 'message': 'Password changed successfully'})


@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    err = require_role('admin')
    if err: return err
    role = request.args.get('role')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if role:
        cursor.execute("SELECT id, user_id, name, email, role, created_at FROM users WHERE role=%s ORDER BY created_at DESC", (role,))
    else:
        cursor.execute("SELECT id, user_id, name, email, role, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    for u in users:
        u['created_at'] = u['created_at'].strftime('%Y-%m-%d %H:%M')
    cursor.close(); conn.close()
    return jsonify({'users': users})

@app.route('/api/admin/users', methods=['POST'])
def admin_add_user():
    err = require_role('admin')
    if err: return err
    data = request.json
    user_id = data.get('user_id', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'student')
    password = data.get('password', '').strip()
    if not user_id or not name or not password:
        return jsonify({'success': False, 'message': 'User ID, Name, and Password are required'}), 400
    if role not in ('instructor', 'student'):
        return jsonify({'success': False, 'message': 'Role must be instructor or student'}), 400
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, role, password_hash) VALUES (%s,%s,%s,%s,%s)",
            (user_id, name, email, role, hash_pw(password))
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': f'User ID "{user_id}" already exists'}), 409
    cursor.close(); conn.close()
    return jsonify({'success': True, 'message': f'{role.capitalize()} "{name}" added successfully'})

@app.route('/api/admin/users/<uid>', methods=['DELETE'])
def admin_delete_user(uid):
    err = require_role('admin')
    if err: return err
    if uid == 'admin':
        return jsonify({'success': False, 'message': 'Cannot delete admin'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=%s", (uid,))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'success': True, 'message': 'User deleted'})

@app.route('/api/admin/users/<uid>/reset-password', methods=['POST'])
def admin_reset_password(uid):
    err = require_role('admin')
    if err: return err
    data = request.json
    new_pw = data.get('new_password', '').strip()
    if not new_pw:
        return jsonify({'success': False, 'message': 'New password required'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (hash_pw(new_pw), uid))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'success': True, 'message': 'Password reset successfully'})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    err = require_role('admin')
    if err: return err
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as c FROM users WHERE role='student'")
    students = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM users WHERE role='instructor'")
    instructors = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM qr_codes")
    sessions = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM attendance_records")
    records = cursor.fetchone()['c']
    cursor.close(); conn.close()
    return jsonify({'students': students, 'instructors': instructors, 'sessions': sessions, 'records': records})


@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    err = require_role('admin', 'instructor')
    if err: return err
    u = get_current_user()
    data = request.json
    course_name = data.get('course_name', 'Cloud Computing CS405')
    duration = int(data.get('duration', 10))
    session_id = f"SESSION_{uuid.uuid4().hex[:8].upper()}"
    qr_token = uuid.uuid4().hex
    expires_at = datetime.now() + timedelta(minutes=duration)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO qr_codes (session_id, course_name, instructor_id, qr_token, expires_at)
        VALUES (%s,%s,%s,%s,%s)
    """, (session_id, course_name, u['user_id'], qr_token, expires_at))
    conn.commit()
    cursor.close(); conn.close()
    qr_data = f"ATTEND:{session_id}:{qr_token}"
    qr_img = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({
        'success': True,
        'session_id': session_id,
        'qr_token': qr_token,
        'qr_data': qr_data,
        'qr_image': f"data:image/png;base64,{qr_b64}",
        'expires_at': expires_at.strftime('%H:%M:%S'),
        'duration': duration
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    err = require_role('admin', 'instructor')
    if err: return err
    u = get_current_user()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if u['role'] == 'admin':
        cursor.execute("""
            SELECT q.*, COUNT(a.id) as attendance_count, u2.name as instructor_name
            FROM qr_codes q
            LEFT JOIN attendance_records a ON q.session_id = a.session_id
            LEFT JOIN users u2 ON q.instructor_id = u2.user_id
            GROUP BY q.id ORDER BY q.created_at DESC LIMIT 50
        """)
    else:
        cursor.execute("""
            SELECT q.*, COUNT(a.id) as attendance_count, u2.name as instructor_name
            FROM qr_codes q
            LEFT JOIN attendance_records a ON q.session_id = a.session_id
            LEFT JOIN users u2 ON q.instructor_id = u2.user_id
            WHERE q.instructor_id=%s
            GROUP BY q.id ORDER BY q.created_at DESC LIMIT 50
        """, (u['user_id'],))
    sessions = cursor.fetchall()
    for s in sessions:
        s['created_at'] = s['created_at'].strftime('%Y-%m-%d %H:%M')
        s['expires_at'] = s['expires_at'].strftime('%Y-%m-%d %H:%M')
    cursor.close(); conn.close()
    return jsonify({'sessions': sessions})

@app.route('/api/session/<session_id>/attendance', methods=['GET'])
def get_session_attendance(session_id):
    err = require_role('admin', 'instructor')
    if err: return err
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.student_id, u.name, a.marked_at
        FROM attendance_records a
        JOIN users u ON a.student_id = u.user_id
        WHERE a.session_id=%s ORDER BY a.marked_at
    """, (session_id,))
    records = cursor.fetchall()
    for r in records:
        r['marked_at'] = r['marked_at'].strftime('%H:%M:%S')
    cursor.close(); conn.close()
    return jsonify({'records': records, 'count': len(records)})


@app.route('/api/checkin', methods=['POST'])
def checkin():
    err = require_role('student')
    if err: return err
    u = get_current_user()
    data = request.json
    qr_data = data.get('qr_data', '').strip()
    try:
        parts = qr_data.split(':')
        if parts[0] != 'ATTEND' or len(parts) < 3:
            return jsonify({'success': False, 'message': 'Invalid QR Code format'}), 400
        session_id = parts[1]
        qr_token = parts[2]
    except:
        return jsonify({'success': False, 'message': 'Invalid QR Code'}), 400
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM qr_codes WHERE session_id=%s AND qr_token=%s AND is_active=TRUE", (session_id, qr_token))
    qr = cursor.fetchone()
    if not qr:
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': 'Invalid QR Code'}), 400
    if datetime.now() > qr['expires_at']:
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': 'QR Code has expired'}), 400
    cursor.execute("SELECT * FROM attendance_records WHERE student_id=%s AND session_id=%s", (u['user_id'], session_id))
    if cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': 'Attendance already recorded for this session'}), 400
    cursor.execute("INSERT INTO attendance_records (student_id, session_id) VALUES (%s,%s)", (u['user_id'], session_id))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'success': True, 'message': f'Attendance recorded successfully for {qr["course_name"]}'})

@app.route('/api/student/attendance', methods=['GET'])
def student_attendance():
    err = require_role('student')
    if err: return err
    u = get_current_user()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.session_id, q.course_name, a.marked_at, u2.name as instructor_name
        FROM attendance_records a
        JOIN qr_codes q ON a.session_id = q.session_id
        JOIN users u2 ON q.instructor_id = u2.user_id
        WHERE a.student_id=%s ORDER BY a.marked_at DESC
    """, (u['user_id'],))
    records = cursor.fetchall()
    for r in records:
        r['marked_at'] = r['marked_at'].strftime('%Y-%m-%d %H:%M')
    cursor.close(); conn.close()
    return jsonify({'records': records, 'total': len(records)})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    time.sleep(5)
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)