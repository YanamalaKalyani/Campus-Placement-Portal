from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime
from functools import wraps
from flask import send_from_directory

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'campus_placement_secret_key_2024')
CORS(app, supports_credentials=True)

DEFAULT_ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@campus.edu')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'campus_placement'),
    'port': 3307,
    'pool_name': 'mypool',
    'pool_size': 5
}

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'resumes')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create connection pool
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
except Exception as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None

def get_db_connection():
    if connection_pool:
        return connection_pool.get_connection()
    return None

# Ensure we always have a default admin user
def ensure_default_admin():
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s AND role = 'admin'", (DEFAULT_ADMIN_EMAIL,))
        if not cursor.fetchone():
            hashed_password = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
            cursor.execute(
                "INSERT INTO users (email, password, role, name, created_at) VALUES (%s, %s, 'admin', %s, %s)",
                (DEFAULT_ADMIN_EMAIL, hashed_password, 'Super Admin', datetime.now())
            )
            admin_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO admins (user_id, name, email, created_at) VALUES (%s, %s, %s, %s)",
                (admin_id, 'Super Admin', DEFAULT_ADMIN_EMAIL, datetime.now())
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error ensuring default admin: {e}")
    finally:
        cursor.close()
        conn.close()

ensure_default_admin()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Serve frontend
# ====================== SERVE FRONTEND ======================
app = Flask(__name__, 
            static_folder='../frontend', 
            static_url_path='')

# Serve main page
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Serve all static files (css, js, images, etc.)
@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except FileNotFoundError:
        # If file not found, return index.html (for SPA-like behavior)
        return send_from_directory(app.static_folder, 'index.html')
# ============================================================
# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    name = data.get('name')

    if not all([email, password, role, name]):
        return jsonify({'error': 'Email, password, role and name are required'}), 400

    if role == 'admin':
        return jsonify({'error': 'Admin registration is disabled. Use default admin credentials.'}), 403

    if role not in ('student', 'company'):
        return jsonify({'error': 'Invalid role'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400

        if role == 'student':
            enrollment_number = data.get('enrollment_number')
            if not enrollment_number:
                return jsonify({'error': 'Enrollment number is required for student registration'}), 400

            cursor.execute("SELECT id FROM students WHERE enrollment_number = %s", (enrollment_number,))
            if cursor.fetchone():
                return jsonify({'error': 'Enrollment number already registered'}), 400

        # Create user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (email, password, role, name, created_at) VALUES (%s, %s, %s, %s, %s)",
            (email, hashed_password, role, name, datetime.now())
        )
        user_id = cursor.lastrowid

        # Create role-specific record
        if role == 'student':
            enrollment_number = data.get('enrollment_number')
            branch = data.get('branch', 'Not specified')
            cgpa = float(data.get('cgpa', 0.0)) if data.get('cgpa') is not None else 0.0
            phone = data.get('phone', '')

            cursor.execute(
                "INSERT INTO students (user_id, name, email, enrollment_number, branch, cgpa, phone, skills, placement_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, name, email, enrollment_number, branch, cgpa, phone, '', 'unplaced')
            )

        elif role == 'company':
            website = data.get('website', '')
            cursor.execute(
                "INSERT INTO companies (user_id, name, email, description, website) VALUES (%s, %s, %s, %s, %s)",
                (user_id, name, email, '', website)
            )

        conn.commit()
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role')
    password = data.get('password')

    if not all([role, password]):
        return jsonify({'error': 'Role and password are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if role == 'admin':
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Admin email is required'}), 400
            if email != DEFAULT_ADMIN_EMAIL:
                return jsonify({'error': 'Invalid admin credentials'}), 401

            cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
            user = cursor.fetchone()
            if not user or not check_password_hash(user['password'], password):
                return jsonify({'error': 'Invalid admin credentials'}), 401

        elif role == 'student':
            enrollment_number = data.get('enrollment_number')
            if not enrollment_number:
                return jsonify({'error': 'Enrollment number is required'}), 400

            cursor.execute(
                "SELECT u.*, s.id AS student_id, s.branch, s.cgpa, s.enrollment_number FROM users u JOIN students s ON u.id = s.user_id WHERE s.enrollment_number = %s AND u.role = 'student'",
                (enrollment_number,)
            )
            user = cursor.fetchone()
            if not user or not check_password_hash(user['password'], password):
                return jsonify({'error': 'Invalid student credentials'}), 401

        elif role == 'company':
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Company email is required'}), 400

            cursor.execute(
                "SELECT u.*, c.id AS company_id FROM users u JOIN companies c ON u.id = c.user_id WHERE u.email = %s AND u.role = 'company'",
                (email,)
            )
            user = cursor.fetchone()
            if not user or not check_password_hash(user['password'], password):
                return jsonify({'error': 'Invalid company credentials'}), 401

        else:
            return jsonify({'error': 'Invalid role'}), 400

        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session['name'] = user['name']

        extra_data = {}
        if role == 'student':
            extra_data = {
                'student_id': user.get('student_id'),
                'branch': user.get('branch'),
                'cgpa': user.get('cgpa'),
                'enrollment_number': user.get('enrollment_number')
            }
        elif role == 'company':
            extra_data = {'company_id': user.get('company_id')}

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                **extra_data
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/session', methods=['GET'])
def get_session():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'email': session['email'],
                'name': session['name'],
                'role': session['role']
            }
        }), 200
    return jsonify({'authenticated': False}), 200

# Admin Routes
@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get counts
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        companies_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM students")
        students_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM students WHERE placement_status = 'placed'")
        placed_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT AVG(package_offered) as avg_package FROM students WHERE placement_status = 'placed' AND package_offered > 0")
        avg_package = cursor.fetchone()['avg_package'] or 0
        
        # Branch-wise placement (Automated from Students table)
        cursor.execute("""
            SELECT UPPER(TRIM(branch)) as branch, 
                   COUNT(*) as total,
                   CAST(SUM(CASE WHEN placement_status = 'placed' THEN 1 ELSE 0 END) AS SIGNED) as placed
            FROM students 
            WHERE branch IS NOT NULL AND branch != ''
            GROUP BY UPPER(TRIM(branch))
        """)
        branch_stats = cursor.fetchall()

        # Optional manual override tables (Handle if missing)
        placement_settings = {
            'total_students': int(students_count),
            'placed_students': int(placed_count),
            'avg_package': float(avg_package),
            'highest_package': 0,
            'lowest_package': 0
        }
        branches = []
        yearly = []

        try:
            cursor.execute("SELECT * FROM placement_settings ORDER BY id DESC LIMIT 1")
            res = cursor.fetchone()
            if res:
                placement_settings = res
                # Safe cast Decimal to float
                for k in ['avg_package', 'highest_package', 'lowest_package']:
                    if k in placement_settings: 
                        placement_settings[k] = float(placement_settings[k])
                
            cursor.execute("SELECT * FROM placement_branches ORDER BY id ASC")
            branches = cursor.fetchall()

            cursor.execute("SELECT * FROM placement_yearly_package ORDER BY year ASC")
            yearly = cursor.fetchall()
        except Exception:
            # Table doesn't exist? Just use our automated defaults
            pass

        # Salary Analysis (LPA Buckets) for Dashboard overview
        cursor.execute("""
            SELECT 
                CAST(SUM(CASE WHEN package_offered > 0 AND package_offered < 5 THEN 1 ELSE 0 END) AS SIGNED) as bucket_0_5,
                CAST(SUM(CASE WHEN package_offered >= 5 AND package_offered < 10 THEN 1 ELSE 0 END) AS SIGNED) as bucket_5_10,
                CAST(SUM(CASE WHEN package_offered >= 10 AND package_offered < 15 THEN 1 ELSE 0 END) AS SIGNED) as bucket_10_15,
                CAST(SUM(CASE WHEN package_offered >= 15 THEN 1 ELSE 0 END) AS SIGNED) as bucket_15_plus,
                COALESCE(AVG(package_offered), 0) as avg_package,
                COALESCE(MAX(package_offered), 0) as max_package
            FROM students
            WHERE placement_status = 'placed' AND package_offered > 0
        """)
        salary_analysis = cursor.fetchone()
        if salary_analysis:
            salary_analysis['avg_package'] = float(salary_analysis['avg_package'])
            salary_analysis['max_package'] = float(salary_analysis['max_package'])

        return jsonify({
            'registered_companies': int(companies_count),
            'registered_students': int(students_count),
            'placed_students': int(placed_count),
            'avg_package': float(avg_package),
            'branch_stats': branch_stats,
            'placement_settings': placement_settings,
            'placement_branches': branches,
            'placement_yearly': yearly,
            'salary_analysis': salary_analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def admin_analytics():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Overview Stats
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        total_companies = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM students WHERE placement_status = 'placed'")
        total_placed = cursor.fetchone()['count']
        
        # Branch-wise Distribution (Automated & Normalized)
        cursor.execute("""
            SELECT UPPER(TRIM(branch)) as branch, 
                   COUNT(*) as total,
                   CAST(SUM(CASE WHEN placement_status = 'placed' THEN 1 ELSE 0 END) AS SIGNED) as placed
            FROM students 
            WHERE branch IS NOT NULL AND branch != ''
            GROUP BY UPPER(TRIM(branch))
        """)
        branch_distribution = cursor.fetchall()

        # Application Status Trends
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM applications 
            GROUP BY status
        """)
        app_status_counts = cursor.fetchall()

        # Salary Analysis (LPA Buckets)
        cursor.execute("""
            SELECT 
                CAST(SUM(CASE WHEN package_offered > 0 AND package_offered < 5 THEN 1 ELSE 0 END) AS SIGNED) as bucket_0_5,
                CAST(SUM(CASE WHEN package_offered >= 5 AND package_offered < 10 THEN 1 ELSE 0 END) AS SIGNED) as bucket_5_10,
                CAST(SUM(CASE WHEN package_offered >= 10 AND package_offered < 15 THEN 1 ELSE 0 END) AS SIGNED) as bucket_10_15,
                CAST(SUM(CASE WHEN package_offered >= 15 THEN 1 ELSE 0 END) AS SIGNED) as bucket_15_plus,
                COALESCE(AVG(package_offered), 0) as avg_package,
                COALESCE(MAX(package_offered), 0) as max_package
            FROM students
            WHERE placement_status = 'placed' AND package_offered > 0
        """)
        salary_analysis = cursor.fetchone()
        if salary_analysis:
            salary_analysis['avg_package'] = float(salary_analysis['avg_package'])
            salary_analysis['max_package'] = float(salary_analysis['max_package'])

        # Top Recruiters
        cursor.execute("""
            SELECT c.name, CAST(COUNT(a.id) AS SIGNED) as hires
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            WHERE a.status = 'accepted'
            GROUP BY c.id, c.name
            ORDER BY hires DESC
            LIMIT 5
        """)
        top_recruiters = cursor.fetchall()

        return jsonify({
            'overview': {
                'total_companies': total_companies,
                'total_students': total_students,
                'total_placed': total_placed,
                'placement_rate': round((total_placed / total_students * 100), 2) if total_students > 0 else 0
            },
            'branch_distribution': branch_distribution,
            'application_status': app_status_counts,
            'salary_analysis': salary_analysis,
            'top_recruiters': top_recruiters
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/placement-settings', methods=['GET', 'PUT'])
@admin_required
def admin_placement_settings():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM placement_settings ORDER BY id DESC LIMIT 1")
            setting = cursor.fetchone()
            if not setting:
                setting = {
                    'total_students': 0,
                    'placed_students': 0,
                    'avg_package': 0,
                    'highest_package': 0,
                    'lowest_package': 0
                }
            return jsonify({'placement_settings': setting}), 200

        data = request.json
        total_students = int(data.get('total_students', 0))
        placed_students = int(data.get('placed_students', 0))
        avg_package = float(data.get('avg_package', 0))
        highest_package = float(data.get('highest_package', 0))
        lowest_package = float(data.get('lowest_package', 0))

        cursor.execute("INSERT INTO placement_settings (total_students, placed_students, avg_package, highest_package, lowest_package, updated_at) VALUES (%s,%s,%s,%s,%s,%s)",
                       (total_students, placed_students, avg_package, highest_package, lowest_package, datetime.now()))
        conn.commit()

        return jsonify({'message': 'Placement settings updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/placement-branches', methods=['POST', 'DELETE'])
@admin_required
def admin_placement_branches():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'DELETE':
            branch_id = request.args.get('id')
            if not branch_id:
                return jsonify({'error': 'Branch ID is required'}), 400
            cursor.execute("DELETE FROM placement_branches WHERE id = %s", (branch_id,))
            conn.commit()
            return jsonify({'message': 'Branch deleted successfully'}), 200

        data = request.json
        branch = data.get('branch')
        total = int(data.get('total', 0))
        placed = int(data.get('placed', 0))

        cursor.execute("INSERT INTO placement_branches (branch, total, placed, created_at) VALUES (%s,%s,%s,%s)",
                       (branch, total, placed, datetime.now()))
        conn.commit()
        return jsonify({'message': 'Branch added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/placement-yearly', methods=['POST', 'DELETE'])
@admin_required
def admin_placement_yearly():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'DELETE':
            year_id = request.args.get('id')
            if not year_id:
                return jsonify({'error': 'Yearly row ID is required'}), 400
            cursor.execute("DELETE FROM placement_yearly_package WHERE id = %s", (year_id,))
            conn.commit()
            return jsonify({'message': 'Yearly package deleted successfully'}), 200

        data = request.json
        year = int(data.get('year', 0))
        avg_package = float(data.get('avg_package', 0))

        cursor.execute("INSERT INTO placement_yearly_package (year, avg_package, created_at) VALUES (%s,%s,%s)",
                       (year, avg_package, datetime.now()))
        conn.commit()
        return jsonify({'message': 'Yearly package added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/student/<int:student_id>', methods=['GET', 'PUT'])
@admin_required
def admin_student_detail(student_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            return jsonify({'student': student}), 200

        data = request.json
        cursor.execute("UPDATE students SET name=%s, email=%s, branch=%s, cgpa=%s, phone=%s, skills=%s, placement_status=%s, package_offered=%s, enrollment_number=%s, semester=%s, tenth=%s, twelfth=%s, backlogs=%s, certifications=%s, internship=%s, projects=%s WHERE id=%s", (
            data.get('name'), data.get('email'), data.get('branch'), data.get('cgpa'), data.get('phone'), data.get('skills'), data.get('placement_status'), data.get('package_offered'), data.get('enrollment_number'), data.get('semester'), data.get('tenth'), data.get('twelfth'), data.get('backlogs'), data.get('certifications'), data.get('internship'), data.get('projects'), student_id
        ))
        conn.commit()
        return jsonify({'message': 'Student updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/company/<int:company_id>', methods=['GET', 'PUT'])
@admin_required
def admin_company_detail(company_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
            company = cursor.fetchone()
            if not company:
                return jsonify({'error': 'Company not found'}), 404
            return jsonify({'company': company}), 200

        data = request.json
        cursor.execute("UPDATE companies SET name=%s, email=%s, website=%s, description=%s, contact=%s, domain=%s, package_lpa=%s, min_cgpa=%s, max_backlogs=%s, position=%s, required_skills=%s, rounds=%s WHERE id=%s", (
            data.get('name'), data.get('email'), data.get('website'), data.get('description'), data.get('contact'), data.get('domain'), data.get('package_lpa'), data.get('min_cgpa'), data.get('max_backlogs'), data.get('position'), data.get('required_skills'), data.get('rounds'), company_id
        ))
        conn.commit()
        return jsonify({'message': 'Company updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/companies', methods=['GET'])
@admin_required
def get_companies():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM companies ORDER BY created_at DESC")
        companies = cursor.fetchall()
        return jsonify({'companies': companies}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/clear-registrations', methods=['POST'])
@admin_required
def clear_registrations():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM applications")
        cursor.execute("DELETE FROM placement_drives")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM companies")
        cursor.execute("DELETE FROM users WHERE role IN ('student', 'company')")
        conn.commit()
        return jsonify({'message': 'Student and company data cleared'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/students', methods=['GET'])
@login_required
def company_students():
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, enrollment_number, branch, semester, tenth, twelfth, cgpa, backlogs, phone, skills, certifications, internship, projects, placement_status, resume_path FROM students WHERE is_sample = 0 ORDER BY created_at DESC")
        students = cursor.fetchall()
        return jsonify({'students': students}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/students', methods=['GET'])
@admin_required
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
        students = cursor.fetchall()
        return jsonify({'students': students}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/placements', methods=['GET'])
@admin_required
def get_placements():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT a.*, s.name as student_name, s.branch, c.name as company_name, pd.title as drive_title
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            WHERE a.status = 'accepted'
            ORDER BY a.updated_at DESC
        """)
        placements = cursor.fetchall()
        return jsonify({'placements': placements}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/drives', methods=['GET', 'POST'])
@admin_required
def admin_drives():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT pd.*, c.name as company_name 
                FROM placement_drives pd
                JOIN companies c ON pd.company_id = c.id
                ORDER BY pd.created_at DESC
            """)
            drives = cursor.fetchall()
            return jsonify({'drives': drives}), 200
        else:
            data = request.json
            cursor.execute("""
                INSERT INTO placement_drives (company_id, title, description, package, eligibility_criteria, drive_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['company_id'], data['title'], data['description'],
                data['package'], data.get('eligibility_criteria', ''),
                data.get('drive_date'), 'active'
            ))
            conn.commit()
            return jsonify({'message': 'Drive created successfully', 'drive_id': cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/notifications', methods=['GET', 'POST'])
@admin_required
def admin_notifications():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC")
            notifications = cursor.fetchall()
            return jsonify({'notifications': notifications}), 200
        else:
            data = request.json
            cursor.execute("""
                INSERT INTO notifications (title, message, target_role, created_at)
                VALUES (%s, %s, %s, %s)
            """, (data['title'], data['message'], data.get('target_role', 'all'), datetime.now()))
            conn.commit()
            return jsonify({'message': 'Notification sent successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Student Routes
@app.route('/api/student/dashboard', methods=['GET'])
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        
        # Get student info
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get application count
        cursor.execute("SELECT COUNT(*) as count FROM applications WHERE student_id = %s", (student['id'],))
        app_count = cursor.fetchone()['count']
        
        # Get automated placement statistics (Consistent with Admin Dashboard)
        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM students WHERE placement_status = 'placed'")
        placed_students = cursor.fetchone()['count']
        
        cursor.execute("SELECT AVG(package_offered) as avg_package FROM students WHERE placement_status = 'placed' AND package_offered > 0")
        avg_package = cursor.fetchone()['avg_package'] or 0
        
        # Branch-wise placement (Automated and Normalized)
        cursor.execute("""
            SELECT UPPER(TRIM(branch)) as branch, 
                   COUNT(*) as total,
                   CAST(SUM(CASE WHEN placement_status = 'placed' THEN 1 ELSE 0 END) AS SIGNED) as placed
            FROM students 
            WHERE branch IS NOT NULL AND branch != ''
            GROUP BY UPPER(TRIM(branch))
        """)
        branch_stats = cursor.fetchall()
            
        return jsonify({
            'student': student,
            'applications_count': int(app_count),
            'stats': {
                'total_students': int(total_students),
                'placed_students': int(placed_students),
                'avg_package': float(avg_package),
                'placement_ratio': round((placed_students / total_students * 100), 1) if total_students > 0 else 0
            },
            'branch_stats': branch_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/profile', methods=['GET', 'PUT'])
@login_required
def student_profile():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        
        if request.method == 'GET':
            cursor.execute(
                "SELECT id, name, email, enrollment_number, branch, semester, tenth, twelfth, cgpa, backlogs, phone, skills, certifications, internship, projects, placement_status, resume_path FROM students WHERE user_id = %s",
                (user_id,)
            )
            student = cursor.fetchone()
            return jsonify({'student': student}), 200
        else:
            data = request.json
            cursor.execute("""
                UPDATE students 
                SET name = %s, branch = %s, semester = %s, tenth = %s, twelfth = %s, cgpa = %s, backlogs = %s, phone = %s,
                    skills = %s, certifications = %s, internship = %s, projects = %s
                WHERE user_id = %s
            """, (
                data.get('name'), data.get('branch'), data.get('semester'), data.get('tenth'), data.get('twelfth'), data.get('cgpa'),
                data.get('backlogs'), data.get('phone'), data.get('skills'), data.get('certifications'), data.get('internship'), data.get('projects'),
                user_id
            ))
            conn.commit()
            return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
        
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        from werkzeug.utils import secure_filename
        
        user_id = session['user_id']
        filename = secure_filename(f"resume_{user_id}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE students SET resume_path = %s WHERE user_id = %s", (filename, user_id))
            conn.commit()
            return jsonify({'message': 'Resume uploaded successfully', 'filename': filename}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
            
    return jsonify({'error': 'Invalid file type. Allowed: PDF, DOC, DOCX'}), 400

@app.route('/uploads/resumes/<filename>')
def serve_resume(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/student/placement-stats', methods=['GET'])
@login_required
def student_placement_stats():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM placement_settings ORDER BY id DESC LIMIT 1")
        settings = cursor.fetchone() or {
            'total_students': 0,
            'placed_students': 0,
            'avg_package': 0,
            'highest_package': 0,
            'lowest_package': 0
        }

        cursor.execute("SELECT * FROM placement_branches ORDER BY id ASC")
        branches = cursor.fetchall()

        cursor.execute("SELECT * FROM placement_yearly_package ORDER BY year ASC")
        yearly = cursor.fetchall()

        return jsonify({
            'placement_settings': settings,
            'placement_branches': branches,
            'placement_yearly': yearly
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/student/companies', methods=['GET'])
@login_required
def student_companies():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT c.id as company_id, c.name as company_name, c.description as company_description,
                   c.min_cgpa, c.rounds, c.domain, c.required_skills, c.position as company_position,
                   c.package_lpa as company_package,
                   pd.id as drive_id, pd.title as drive_title, pd.package as drive_package, 
                   pd.drive_date, pd.status as drive_status
            FROM companies c
            LEFT JOIN placement_drives pd ON c.id = pd.company_id AND pd.status = 'active'
            ORDER BY c.created_at DESC
        """)
        drives = cursor.fetchall()
        
        # Get student info for eligibility check on front-end
        user_id = session['user_id']
        cursor.execute("SELECT cgpa FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        return jsonify({
            'drives': drives,
            'student_cgpa': student['cgpa'] if student else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/applications', methods=['GET', 'POST'])
@login_required
def student_applications():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT a.*, pd.title as drive_title, pd.package, c.name as company_name
                FROM applications a
                JOIN placement_drives pd ON a.drive_id = pd.id
                JOIN companies c ON pd.company_id = c.id
                WHERE a.student_id = %s
                ORDER BY a.created_at DESC
            """, (student['id'],))
            applications = cursor.fetchall()
            return jsonify({'applications': applications}), 200
        else:
            data = request.json
            drive_id = data.get('drive_id')
            company_id = data.get('company_id')
            
            if not drive_id and not company_id:
                return jsonify({'error': 'Drive or Company ID required'}), 400
                
            # If application is through company ID, resolve/create a drive
            if not drive_id:
                cursor.execute("SELECT id FROM placement_drives WHERE company_id = %s AND status = 'active' LIMIT 1", (company_id,))
                drive = cursor.fetchone()
                if drive:
                    drive_id = drive['id']
                else:
                    # Auto-create a general drive for this company if profile is sufficient
                    cursor.execute("SELECT name, position, package_lpa FROM companies WHERE id = %s", (company_id,))
                    c_info = cursor.fetchone()
                    if not c_info:
                        return jsonify({'error': 'Invalid company'}), 404
                    
                    drive_title = f"General Hiring - {c_info['name']}"
                    drive_package = c_info['package_lpa'] or 0
                    
                    cursor.execute("""
                        INSERT INTO placement_drives (company_id, title, package, status, drive_date)
                        VALUES (%s, %s, %s, 'active', %s)
                    """, (company_id, drive_title, drive_package, datetime.now()))
                    drive_id = cursor.lastrowid
            
            # Check if already applied
            cursor.execute(
                "SELECT id FROM applications WHERE student_id = %s AND drive_id = %s",
                (student['id'], drive_id)
            )
            if cursor.fetchone():
                return jsonify({'error': 'Already applied to this drive'}), 400
            
            cursor.execute("""
                INSERT INTO applications (student_id, drive_id, status, created_at)
                VALUES (%s, %s, 'pending', %s)
            """, (student['id'], drive_id, datetime.now()))
            conn.commit()
            return jsonify({'message': 'Application submitted successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/notifications', methods=['GET'])
@login_required
def student_notifications():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        cursor.execute("""
            SELECT n.*, IF(ns.id IS NOT NULL, 1, 0) as is_read 
            FROM notifications n
            LEFT JOIN notification_status ns ON n.id = ns.notification_id AND ns.user_id = %s
            WHERE (n.target_role IN ('all', 'student') AND n.user_id IS NULL) 
               OR (n.target_role = 'student' AND n.user_id = %s)
            ORDER BY n.created_at DESC
        """, (user_id, user_id))
        notifications = cursor.fetchall()
        return jsonify({'notifications': notifications}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/notifications/read', methods=['POST'])
@login_required
def mark_notification_read():
    if session.get('role') != 'student':
        return jsonify({'error': 'Student access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        data = request.json or {}
        notification_id = data.get('notification_id')
        
        if notification_id:
            # Mark single notification as read
            cursor.execute("SELECT id FROM notification_status WHERE user_id = %s AND notification_id = %s", (user_id, notification_id))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO notification_status (user_id, notification_id, is_read, read_at) VALUES (%s, %s, 1, %s)",
                    (user_id, notification_id, datetime.now())
                )
        else:
            # Mark all as read
            cursor.execute("""
                INSERT INTO notification_status (user_id, notification_id, is_read, read_at)
                SELECT %s, n.id, 1, %s
                FROM notifications n
                LEFT JOIN notification_status ns ON n.id = ns.notification_id AND ns.user_id = %s
                WHERE ((n.target_role IN ('all', 'student') AND n.user_id IS NULL) 
                   OR (n.target_role = 'student' AND n.user_id = %s))
                   AND ns.id IS NULL
            """, (user_id, datetime.now(), user_id, user_id))
            
        conn.commit()
        return jsonify({'message': 'Notifications marked as read'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Company Routes
@app.route('/api/company/dashboard', methods=['GET'])
@login_required
def company_dashboard():
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        
        cursor.execute("SELECT * FROM companies WHERE user_id = %s", (user_id,))
        company = cursor.fetchone()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get drives count
        cursor.execute("SELECT COUNT(*) as count FROM placement_drives WHERE company_id = %s", (company['id'],))
        drives_count = cursor.fetchone()['count']
        
        # Get applications count
        cursor.execute("""
            SELECT COUNT(*) as count FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            WHERE pd.company_id = %s
        """, (company['id'],))
        applications_count = cursor.fetchone()['count']
        
        # Get selected students count
        cursor.execute("""
            SELECT COUNT(*) as count FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            WHERE pd.company_id = %s AND a.status = 'accepted'
        """, (company['id'],))
        selected_count = cursor.fetchone()['count']
        
        return jsonify({
            'company': company,
            'drives_count': drives_count,
            'applications_count': applications_count,
            'selected_count': selected_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/applications', methods=['GET'])
@login_required
def company_applications():
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        cursor.execute("SELECT id FROM companies WHERE user_id = %s", (user_id,))
        company = cursor.fetchone()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        cursor.execute("""
            SELECT a.*, s.name as student_name, s.email as student_email, 
                   s.branch, s.cgpa, s.skills, pd.title as drive_title
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN placement_drives pd ON a.drive_id = pd.id
            WHERE pd.company_id = %s
            ORDER BY a.created_at DESC
        """, (company['id'],))
        applications = cursor.fetchall()
        return jsonify({'applications': applications}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/applications/<int:app_id>', methods=['PUT'])
@login_required
def update_application(app_id):
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        data = request.json
        status = data.get('status')
        package = data.get('package', 0)
        
        # Get current application details for notification
        cursor.execute("""
            SELECT a.student_id, a.drive_id, pd.title as drive_title, c.name as company_name, s.user_id as student_user_id
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            JOIN students s ON a.student_id = s.id
            WHERE a.id = %s
        """, (app_id,))
        app_details = cursor.fetchone()
        
        if not app_details:
            return jsonify({'error': 'Application not found'}), 404
        
        cursor.execute("""
            UPDATE applications SET status = %s, updated_at = %s WHERE id = %s
        """, (status, datetime.now(), app_id))
        
        if status == 'accepted':
            # Update student placement status
            cursor.execute("""
                UPDATE students SET placement_status = 'placed', package_offered = %s WHERE id = %s
            """, (package, app_details['student_id']))
        
        # Create notification for the student
        status_messages = {
            'pending': 'Your application is under review',
            'shortlisted': 'Congratulations! You have been shortlisted',
            'accepted': f'Congratulations! You have been selected for the position with package ₹{package:,} LPA',
            'rejected': 'We regret to inform you that your application was not successful'
        }
        
        title = f'Application Update - {app_details["company_name"]}'
        message = f'Your application for "{app_details["drive_title"]}" at {app_details["company_name"]} has been updated.\n\n{status_messages.get(status, "Status updated")}'
        
        cursor.execute("""
            INSERT INTO notifications (title, message, target_role, user_id, created_at)
            VALUES (%s, %s, 'student', %s, %s)
        """, (title, message, app_details['student_user_id'], datetime.now()))
        
        conn.commit()
        return jsonify({'message': 'Application updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/profile', methods=['GET', 'PUT'])
@login_required
def company_profile():
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        
        if request.method == 'GET':
            cursor.execute(
                "SELECT id, name, email, website, description, contact, domain, package_lpa, min_cgpa, max_backlogs, position, required_skills, rounds FROM companies WHERE user_id = %s",
                (user_id,)
            )
            company = cursor.fetchone()
            return jsonify({'company': company}), 200
        else:
            data = request.json
            cursor.execute("""
                UPDATE companies SET name = %s, website = %s, description = %s, contact = %s,
                    domain = %s, package_lpa = %s, min_cgpa = %s, max_backlogs = %s,
                    position = %s, required_skills = %s, rounds = %s
                WHERE user_id = %s
            """, (
                data.get('name'), data.get('website'), data.get('description'), data.get('contact'),
                data.get('domain'), data.get('package_lpa'), data.get('min_cgpa'), data.get('max_backlogs'),
                data.get('position'), data.get('required_skills'), data.get('rounds'),
                user_id
            ))
            conn.commit()
            return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/drives', methods=['GET', 'POST'])
@login_required
def company_drives():
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        user_id = session['user_id']
        cursor.execute("SELECT id FROM companies WHERE user_id = %s", (user_id,))
        company = cursor.fetchone()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT * FROM placement_drives WHERE company_id = %s ORDER BY created_at DESC
            """, (company['id'],))
            drives = cursor.fetchall()
            return jsonify({'drives': drives}), 200
        else:
            data = request.json
            cursor.execute("""
                INSERT INTO placement_drives (company_id, title, description, package, eligibility_criteria, drive_date, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                company['id'], data['title'], data.get('description', ''),
                data['package'], data.get('eligibility_criteria', ''),
                data.get('drive_date'), 'active', datetime.now()
            ))
            conn.commit()
            return jsonify({'message': 'Drive created successfully', 'drive_id': cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/company/student/<int:student_id>', methods=['GET'])
@login_required
def company_student_detail(student_id):
    if session.get('role') != 'company':
        return jsonify({'error': 'Company access required'}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, name, email, enrollment_number, branch, semester, tenth, twelfth, cgpa, backlogs, phone, skills, certifications, internship, projects, placement_status, resume_path FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        return jsonify({'student': student}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ====================== SERVE FRONTEND ======================
# This must be at the BOTTOM of the file (before if __name__ == "__main__")

from flask import send_from_directory

# Configure Flask to serve frontend files
app.static_folder = '../frontend'

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except FileNotFoundError:
        return send_from_directory(app.static_folder, 'index.html')
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
