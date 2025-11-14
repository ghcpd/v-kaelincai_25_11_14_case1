"""
Baseline Course Player Backend Server (Project A)
Serves static HTML/JS content and mock video fragments without enhancement features
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory
from pathlib import Path
import logging

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/server_pre.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Store for user progress (baseline: no actual persistence features)
user_progress = {}
courses_db = {
    'C101': {'id': 'C101', 'title': 'Introduction to Python', 'duration': 3600},
    'C102': {'id': 'C102', 'title': 'Advanced Python', 'duration': 3600},
    'C103': {'id': 'C103', 'title': 'Web Development Basics', 'duration': 3600},
    'C104': {'id': 'C104', 'title': 'Data Science 101', 'duration': 3600},
    'C105': {'id': 'C105', 'title': 'Cloud Computing', 'duration': 3600},
}

@app.route('/')
def index():
    """Serve the baseline player HTML"""
    logger.info('Serving baseline player index')
    return send_from_directory('../src', 'index.html')

@app.route('/js/<path:path>')
def send_js(path):
    """Serve JavaScript files"""
    return send_from_directory('../src', path)

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get list of available courses"""
    logger.info('Fetching courses list')
    return jsonify({'courses': list(courses_db.values())})

@app.route('/api/course/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get course details"""
    if course_id not in courses_db:
        logger.warning(f'Course not found: {course_id}')
        return jsonify({'error': 'Course not found'}), 404
    
    logger.info(f'Fetching course details: {course_id}')
    return jsonify(courses_db[course_id])

@app.route('/api/user/<user_id>/progress/<course_id>', methods=['GET'])
def get_progress(user_id, course_id):
    """
    Get user's progress for a course
    Baseline: Always returns position 0 (no resume functionality)
    """
    logger.info(f'Getting progress for user {user_id}, course {course_id}')
    
    # Baseline behavior: no saved progress
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'last_position_s': 0,
        'playback_rate': 1.0,
        'quality': '720p',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/<user_id>/progress/<course_id>', methods=['POST'])
def save_progress(user_id, course_id):
    """
    Save user's progress (baseline: accepts but doesn't use)
    """
    data = request.json
    logger.info(f'Received progress save for user {user_id}, course {course_id}: {data}')
    
    # Baseline: Accept but don't store for actual use
    return jsonify({
        'status': 'accepted',
        'message': 'Progress data logged but not persisted (baseline)',
        'user_id': user_id,
        'course_id': course_id
    })

@app.route('/mock-video/sample.mp4', methods=['GET'])
def serve_mock_video():
    """Serve a simple mock video or placeholder"""
    logger.info('Serving mock video')
    
    # Create a minimal MP4 placeholder if not exists
    mock_video_path = Path('../mocks/sample.mp4')
    if not mock_video_path.exists():
        create_mock_video(mock_video_path)
    
    return send_file(str(mock_video_path), mimetype='video/mp4')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'baseline-player',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get server metrics"""
    return jsonify({
        'service': 'baseline-player',
        'active_users': len(user_progress),
        'timestamp': datetime.now().isoformat()
    })

def create_mock_video(path):
    """Create a simple mock video placeholder (minimal MP4)"""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Minimal MP4 file structure (valid but very small)
    # This is a valid MP4 header for a video with 0 frames
    mp4_header = bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
        0x69, 0x73, 0x6f, 0x6d, 0x00, 0x00, 0x02, 0x00,
        0x69, 0x73, 0x6f, 0x6d, 0x69, 0x73, 0x6f, 0x32,
        0x61, 0x76, 0x63, 0x31, 0x6d, 0x70, 0x34, 0x31
    ])
    
    with open(path, 'wb') as f:
        f.write(mp4_header)
    
    logger.info(f'Created mock video: {path}')

if __name__ == '__main__':
    logger.info('Starting baseline player server...')
    os.chdir(os.path.dirname(__file__))
    app.run(host='127.0.0.1', port=5000, debug=False)
