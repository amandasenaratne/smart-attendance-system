from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
from datetime import datetime
from pathlib import Path
import io
import cv2
import base64
import numpy as np

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from attendance.attendance_manager import AttendanceManager

app = Flask(__name__)

# Initialize attendance manager
attendance_csv_path = os.path.join(os.path.dirname(__file__), '..', 'attendance', 'attendance_records.csv')
attendance_manager = AttendanceManager(attendance_csv_path)


@app.route('/')
def dashboard():
    """Render the main dashboard."""
    records = attendance_manager.get_all_records()
    stats = attendance_manager.get_summary_statistics()
    
    return render_template('index.html', records=records, stats=stats)


@app.route('/api/records', methods=['GET'])
def get_records():
    """API endpoint to get attendance records with optional filtering."""
    date_filter = request.args.get('date')
    person_filter = request.args.get('person')
    
    if date_filter:
        records = attendance_manager.get_records_by_date(date_filter)
    elif person_filter:
        records = attendance_manager.get_records_by_person(person_filter)
    else:
        records = attendance_manager.get_all_records()
    
    return jsonify(records)


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API endpoint to get attendance statistics."""
    stats = attendance_manager.get_summary_statistics()
    return jsonify(stats)


@app.route('/export', methods=['GET'])
def export_csv():
    """Export attendance records as CSV file."""
    try:
        export_path = os.path.join(
            os.path.dirname(__file__), 
            '..',
            'attendance',
            f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if attendance_manager.export_to_csv(export_path):
            return send_file(
                export_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        else:
            return jsonify({'error': 'Failed to export CSV'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/record', methods=['POST'])
def record_attendance():
    """API endpoint to record attendance manually."""
    data = request.get_json()
    name = data.get('name')
    status = data.get('status', 'Present')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    success = attendance_manager.record_attendance(name, status)
    
    if success:
        return jsonify({'message': 'Attendance recorded successfully'}), 201
    else:
        return jsonify({'error': 'Could not record attendance (duplicate or error)'}), 400


@app.route('/register-face', methods=['POST'])
def register_face():
    """API endpoint to register a new face."""
    try:
        data = request.get_json()
        person_name = data.get('name')
        image_data = data.get('image')
        
        if not person_name or not image_data:
            return jsonify({'error': 'Name and image are required'}), 400
        
        # Create directory for person
        faces_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets', 'faces')
        person_dir = os.path.join(faces_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        # Decode and save image
        try:
            # Remove data:image/jpeg;base64, prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'error': 'Invalid image data'}), 400
            
            # Save image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            img_path = os.path.join(person_dir, f"{person_name}_{timestamp}.jpg")
            cv2.imwrite(img_path, img)
            
            return jsonify({
                'message': f'Face image captured for {person_name}',
                'image_path': img_path
            }), 201
            
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Registration error: {str(e)}'}), 500


@app.route('/registered-people', methods=['GET'])
def get_registered_people():
    """Get list of registered people."""
    try:
        faces_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets', 'faces')
        if not os.path.exists(faces_dir):
            return jsonify({'people': []}), 200
        
        people = [d for d in os.listdir(faces_dir) if os.path.isdir(os.path.join(faces_dir, d))]
        return jsonify({'people': people}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a record by index."""
    try:
        records = attendance_manager.get_all_records()
        
        if record_id < 0 or record_id >= len(records):
            return jsonify({'error': 'Record not found'}), 404
        
        # Read all records except the one to delete
        remaining_records = records[:record_id] + records[record_id + 1:]
        
        # Write back to CSV
        csv_path = attendance_manager.csv_file_path
        with open(csv_path, 'w', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['Name', 'Date', 'Time', 'Status'])
            for record in remaining_records:
                writer.writerow([record['Name'], record['Date'], record['Time'], record['Status']])
        
        return jsonify({'message': 'Record deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Page not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Run the app in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)
