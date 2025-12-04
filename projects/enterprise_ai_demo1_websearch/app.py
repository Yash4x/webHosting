"""
🌐 AI Image Generation Web Interface
===================================

A modern, sleek web interface for AI image generation using Flask.
Features single image generation and visual story creation.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, redirect, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
from functools import wraps

from src.search_service import ImageGenerationService
from src.models import ImageOptions, StoryOptions, ImageResult, StoryResult
from src.logging_config import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://aiuser:aipassword@postgres:5432/aiimages'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Initialize the image generation service
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

service = ImageGenerationService(api_key=api_key)

# Ensure directories exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("static/generated", exist_ok=True)  # For web-accessible images

# Database Models - defined here to avoid circular imports
class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    # Relationships
    generated_images = db.relationship('GeneratedImage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'image_count': self.generated_images.count()
        }


class GeneratedImage(db.Model):
    """Track generated images per user"""
    __tablename__ = 'generated_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    prompt = db.Column(db.Text, nullable=False)
    image_type = db.Column(db.String(20), nullable=False)  # 'single' or 'story'
    file_path = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    image_metadata = db.Column(db.JSON)  # Renamed from 'metadata' (reserved word in SQLAlchemy)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<GeneratedImage {self.id} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert image to dictionary"""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'image_type': self.image_type,
            'file_path': self.file_path,
            'image_url': self.image_url,
            'image_metadata': self.image_metadata,
            'created_at': self.created_at.isoformat()
        }

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== Authentication Routes ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if not email or '@' not in email:
            errors.append('Valid email is required')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check existing user
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            if request.is_json:
                return jsonify({'error': ', '.join(errors)}), 400
            flash(', '.join(errors), 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'}), 201
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            if request.is_json:
                return jsonify({'error': 'Registration failed'}), 500
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Username and password required'}), 400
            flash('Username and password required', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            logger.info(f"User logged in: {username}")
            
            next_page = request.args.get('next')
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': next_page or url_for('dashboard')
                }), 200
            
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their generated images"""
    # Get user's generated images
    images = GeneratedImage.query.filter_by(user_id=current_user.id)\
        .order_by(GeneratedImage.created_at.desc())\
        .limit(50)\
        .all()
    
    # Get statistics
    total_images = current_user.generated_images.count()
    total_stories = current_user.generated_images.filter_by(image_type='story').count()
    total_singles = current_user.generated_images.filter_by(image_type='single').count()
    
    return render_template('dashboard.html',
                         images=images,
                         total_images=total_images,
                         total_stories=total_stories,
                         total_singles=total_singles)


# ==================== Public Routes ====================

@app.route('/')
def index():
    """Homepage with clean, modern design."""
    return render_template('index.html')


@app.route('/generate')
@login_required
def generate_page():
    """Single image generation page."""
    return render_template('generate.html')


@app.route('/story')
@login_required
def story_page():
    """Visual story generation page."""
    return render_template('story.html')


@app.route('/gallery')
@login_required
def gallery_page():
    """Gallery page to view all generated content."""
    return render_template('gallery.html')


@app.route('/api/generate-image', methods=['POST'])
@login_required
def api_generate_image():
    """API endpoint for single image generation."""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        # Create image options
        options = ImageOptions(
            size=data.get('size', '1024x1024'),
            quality=data.get('quality', 'standard'),
            style=data.get('style', 'vivid')
        )
        
        logger.info(f"Generating single image for prompt: {prompt}")
        
        # Track timing
        start_time = datetime.now()
        
        # Generate the image
        result = service.generate_image(
            prompt=prompt,
            options=options,
            auto_save=True,
            save_dir="generated_images"
        )
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Copy to web-accessible location
        web_path = _copy_to_web_accessible(result.file_path, "single_image")
        
        # Save to database
        try:
            generated_img = GeneratedImage(
                user_id=current_user.id,
                prompt=prompt,
                image_type='single',
                file_path=result.file_path,
                image_url=result.image_url,
                image_metadata={
                    'revised_prompt': result.metadata.revised_prompt if result.metadata else None,
                    'size': options.size,
                    'quality': options.quality,
                    'style': options.style,
                    'generation_time': generation_time
                }
            )
            db.session.add(generated_img)
            db.session.commit()
        except Exception as db_error:
            logger.error(f"Failed to save image to database: {str(db_error)}")
            db.session.rollback()
        
        response_data = {
            'success': True,
            'image_url': result.image_url,
            'file_path': result.file_path,
            'web_path': web_path,
            'revised_prompt': result.metadata.revised_prompt if result.metadata else None,
            'generation_time': generation_time,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Single image generated successfully by {current_user.username}: {result.file_path}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating single image: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-story', methods=['POST'])
@login_required
def api_generate_story():
    """API endpoint for story generation."""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        # Create story options
        options = StoryOptions(
            story_prompt=prompt,
            num_scenes=int(data.get('num_scenes', 5)),
            size=data.get('image_size', '1024x1024'),
            quality=data.get('image_quality', 'standard'),
            style=data.get('image_style', 'vivid'),
            enable_narration=bool(data.get('enable_narration', False)),
            voice=data.get('voice', 'alloy'),
            narration_speed=float(data.get('narration_speed', 1.0))
        )
        
        logger.info(f"Generating story for prompt: {prompt}")
        
        # Generate the story
        result = service.generate_story(options)
        
        # Determine story folder from the first scene's file path
        story_folder_name = "story_unknown"
        if result.scenes and result.scenes[0].image_result and result.scenes[0].image_result.file_path:
            # Extract folder name from file path (e.g., "generated_images/story_5/file.png" -> "story_5")
            import os
            folder_path = os.path.dirname(result.scenes[0].image_result.file_path)
            story_folder_name = os.path.basename(folder_path)
        
        # Copy all scene images to web-accessible location
        web_scenes = []
        for scene in result.scenes:
            if scene.image_result and scene.image_result.file_path:
                web_path = _copy_to_web_accessible(
                    scene.image_result.file_path, 
                    story_folder_name
                )
                # Create audio URL if audio file exists
                audio_url = None
                if scene.audio_file_path and os.path.exists(scene.audio_file_path):
                    # Convert absolute path to relative URL
                    audio_relative_path = os.path.relpath(scene.audio_file_path, 'generated_images')
                    audio_url = f"/audio/{audio_relative_path}"
                
                web_scenes.append({
                    'scene_number': scene.scene_number,
                    'description': scene.narrative,  # Use narrative instead of description
                    'web_path': web_path,
                    'file_path': scene.image_result.file_path,
                    'audio_url': audio_url,
                    'has_audio': scene.has_audio,
                    'revised_prompt': scene.image_result.metadata.revised_prompt if scene.image_result.metadata else None,
                    'generation_time': 0  # Story generation timing is tracked at story level
                })
        
        response_data = {
            'success': True,
            'story_folder': story_folder_name,
            'total_scenes': result.num_scenes,
            'successful_scenes': len(result.completed_scenes),
            'success_rate': result.success_rate,
            'scenes': web_scenes,
            'total_generation_time': result.total_generation_time,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Story generated successfully: {story_folder_name}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/gallery')
@login_required
def api_gallery():
    """Get list of generated images and stories for the current user only."""
    try:
        # Query database for current user's images
        images = GeneratedImage.query.filter_by(user_id=current_user.id).order_by(GeneratedImage.created_at.desc()).all()
        
        gallery_items = []
        
        for img in images:
            # Check if file still exists
            if not os.path.exists(img.file_path):
                continue
                
            if img.image_type == 'story':
                # This is a story folder
                story_info = _get_story_info(img.file_path)
                if story_info:
                    story_info['db_id'] = img.id
                    story_info['prompt'] = img.prompt
                    gallery_items.append(story_info)
            else:
                # This is a single image
                image_info = _get_image_info(img.file_path)
                if image_info:
                    image_info['db_id'] = img.id
                    image_info['prompt'] = img.prompt
                    gallery_items.append(image_info)
        
        return jsonify({'items': gallery_items})
        
    except Exception as e:
        logger.error(f"Error getting gallery: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve generated images from web-accessible location."""
    return send_from_directory('static/generated', filename)


@app.route('/generated_images/<path:filename>')
def serve_generated_image(filename):
    """Serve images directly from generated_images directory."""
    return send_from_directory('generated_images', filename)


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files from generated_images directory."""
    return send_from_directory('generated_images', filename)


def _copy_to_web_accessible(source_path: str, folder_name: str) -> str:
    """Copy generated image to web-accessible location."""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source image not found: {source_path}")
    
    # Create unique filename to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder_name}_{timestamp}_{os.path.basename(source_path)}"
    
    # Ensure destination directory exists
    dest_dir = "static/generated"
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy file
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(source_path, dest_path)
    
    # Return web-accessible URL - use relative path that works in browser
    return f"/images/{filename}"


def _get_story_info(story_path: str) -> Optional[Dict]:
    """Get information about a story folder."""
    try:
        story_name = os.path.basename(story_path)
        scenes = []
        audio_files = {}
        
        # First pass: collect all audio files by scene number
        for file in os.listdir(story_path):
            if file.endswith('.mp3') and 'narration' in file:
                # Extract scene number from filename like "scene_1_narration.mp3"
                parts = file.split('_')
                if len(parts) >= 2 and parts[0] == 'scene':
                    try:
                        scene_num = int(parts[1])
                        audio_files[scene_num] = {
                            'filename': file,
                            'path': os.path.join(story_path, file),
                            'url': f"/audio/{story_name}/{file}"
                        }
                    except (ValueError, IndexError):
                        continue
        
        # Second pass: get all image files and sort them by creation time to maintain order
        image_files = []
        for file in os.listdir(story_path):
            if file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                file_path = os.path.join(story_path, file)
                image_files.append({
                    'filename': file,
                    'path': file_path,
                    'created': os.path.getctime(file_path)
                })
        
        # Sort images by creation time to maintain original generation order
        image_files.sort(key=lambda x: x['created'])
        
        # Now assign scene numbers based on the sorted order
        for index, img_info in enumerate(image_files):
            scene_number = index + 1  # Scene numbers start from 1
            file_path = img_info['path']
            
            scene_data = {
                'filename': img_info['filename'],
                'path': file_path,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                'scene_number': scene_number,
                'has_audio': scene_number in audio_files,
                'audio_url': audio_files.get(scene_number, {}).get('url'),
                'audio_filename': audio_files.get(scene_number, {}).get('filename')
            }
            scenes.append(scene_data)
        
        if not scenes:
            return None
        
        # No need to sort again since we already processed in creation order
        
        # Count total audio files
        total_audio_files = len(audio_files)
        
        return {
            'type': 'story',
            'name': story_name,
            'path': story_path,
            'scene_count': len(scenes),
            'scenes': scenes,
            'has_narration': total_audio_files > 0,
            'audio_count': total_audio_files,
            'created_at': min(scene['modified'] for scene in scenes),
            'size': sum(scene['size'] for scene in scenes)
        }
        
    except Exception as e:
        logger.error(f"Error getting story info for {story_path}: {str(e)}")
        return None


def _get_image_info(image_path: str) -> Optional[Dict]:
    """Get information about a single image."""
    try:
        filename = os.path.basename(image_path)
        stat = os.stat(image_path)
        
        return {
            'type': 'image',
            'name': filename,
            'path': image_path,
            'size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting image info for {image_path}: {str(e)}")
        return None


if __name__ == '__main__':
    print("🌐 Starting AI Image Generation Web Interface...")
    print("📖 Access the application at: http://localhost:5000")
    print("🎨 Features: Single Images • Visual Stories • Gallery")
    print("✨ Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)