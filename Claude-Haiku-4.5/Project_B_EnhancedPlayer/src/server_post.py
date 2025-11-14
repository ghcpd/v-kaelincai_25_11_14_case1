"""
Enhanced Course Player Backend Server (Project B)
Serves enhanced player with progress persistence, learned segments, and notes
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
        logging.FileHandler('../logs/server_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Store for user progress and learned segments
user_progress = {}
user_learned_segments = {}
user_notes = {}

courses_db = {
    'C101': {'id': 'C101', 'title': 'Introduction to Python', 'duration': 3600},
    'C102': {'id': 'C102', 'title': 'Advanced Python', 'duration': 3600},
    'C103': {'id': 'C103', 'title': 'Web Development Basics', 'duration': 3600},
    'C104': {'id': 'C104', 'title': 'Data Science 101', 'duration': 3600},
    'C105': {'id': 'C105', 'title': 'Cloud Computing', 'duration': 3600},
}

@app.route('/')
def index():
    """Serve the enhanced player HTML"""
    logger.info('Serving enhanced player index')
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
    ENHANCED: Returns last saved position and settings
    """
    logger.info(f'Getting progress for user {user_id}, course {course_id}')
    
    key = f'{user_id}_{course_id}'
    if key in user_progress:
        progress = user_progress[key]
        logger.info(f'Returning saved progress: {progress}')
        return jsonify(progress)
    
    # No saved progress
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'last_position_s': 0,
        'playback_rate': 1.0,
        'quality': 'auto',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/<user_id>/progress/<course_id>', methods=['POST'])
def save_progress(user_id, course_id):
    """
    Save user's progress (ENHANCED: Actually persists)
    """
    data = request.json
    logger.info(f'Saving progress for user {user_id}, course {course_id}: {data}')
    
    key = f'{user_id}_{course_id}'
    user_progress[key] = {
        'user_id': user_id,
        'course_id': course_id,
        'last_position_s': data.get('position', 0),
        'playback_rate': data.get('playback_rate', 1.0),
        'quality': data.get('quality', 'auto'),
        'timestamp': datetime.now().isoformat()
    }

    return jsonify({
        'status': 'saved',
        'message': 'Progress persisted',
        'user_id': user_id,
        'course_id': course_id,
        'position': data.get('position', 0)
    })

@app.route('/api/user/<user_id>/course/<course_id>/segments', methods=['GET'])
def get_learned_segments(user_id, course_id):
    """Get learned segments for a course"""
    logger.info(f'Getting learned segments for user {user_id}, course {course_id}')
    
    key = f'{user_id}_{course_id}'
    segments = user_learned_segments.get(key, [])
    
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'learned_segments': segments
    })

@app.route('/api/user/<user_id>/course/<course_id>/segments', methods=['POST'])
def mark_segment_learned(user_id, course_id):
    """Mark a segment as learned"""
    data = request.json
    logger.info(f'Marking segment as learned for user {user_id}, course {course_id}: {data}')
    
    key = f'{user_id}_{course_id}'
    if key not in user_learned_segments:
        user_learned_segments[key] = []
    
    segment = {
        'segment_id': data.get('segment_id'),
        'start_time_s': data.get('start_time_s'),
        'end_time_s': data.get('end_time_s'),
        'marked_at': datetime.now().isoformat()
    }
    
    user_learned_segments[key].append(segment)
    
    return jsonify({
        'status': 'marked',
        'segment': segment
    })

@app.route('/api/user/<user_id>/course/<course_id>/notes', methods=['GET'])
def get_notes(user_id, course_id):
    """Get user's notes for a course"""
    logger.info(f'Getting notes for user {user_id}, course {course_id}')
    
    key = f'{user_id}_{course_id}'
    notes = user_notes.get(key, [])
    
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'notes': notes
    })

@app.route('/api/user/<user_id>/course/<course_id>/notes', methods=['POST'])
def save_note(user_id, course_id):
    """Save a note with timestamp"""
    data = request.json
    logger.info(f'Saving note for user {user_id}, course {course_id}: {data}')
    
    key = f'{user_id}_{course_id}'
    if key not in user_notes:
        user_notes[key] = []
    
    note = {
        'note_id': data.get('note_id', f'N{len(user_notes[key])+1}'),
        'timestamp_s': data.get('timestamp_s'),
        'text': data.get('text'),
        'created_at': datetime.now().isoformat()
    }
    
    user_notes[key].append(note)
    
    return jsonify({
        'status': 'saved',
        'note': note
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
        'service': 'enhanced-player',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get server metrics"""
    return jsonify({
        'service': 'enhanced-player',
        'active_users': len(set(k.split('_')[0] for k in user_progress.keys())),
        'saved_progress_entries': len(user_progress),
        'learned_segments': len(user_learned_segments),
        'notes': len(user_notes),
        'timestamp': datetime.now().isoformat()
    })

def create_mock_video(path):
    """Create a simple mock video placeholder (minimal MP4)"""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Minimal MP4 file structure (valid but very small)
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
    logger.info('Starting enhanced player server...')
    os.chdir(os.path.dirname(__file__))
    app.run(host='127.0.0.1', port=5001, debug=False)
