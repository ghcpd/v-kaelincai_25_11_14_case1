/**
 * Baseline Course Player - No enhancements
 * This version demonstrates the basic player without:
 * - Resume from last position
 * - Playback speed controls
 * - Auto-skip learned segments
 * - Adaptive buffering
 * - Note synchronization
 */

class BaselinePlayer {
    constructor() {
        this.videoElement = document.getElementById('courseVideo');
        this.statusDisplay = document.getElementById('statusDisplay');
        this.playBtn = document.getElementById('playBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.volumeSlider = document.getElementById('volumeSlider');
        
        this.currentCourse = null;
        this.userId = null;
        this.metrics = {
            startTime: null,
            timeToFirstFrame: null,
            stalls: 0,
            stallDurations: [],
            networkStatus: 'good'
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.logAction('Initialized baseline player');
    }

    setupEventListeners() {
        this.playBtn.addEventListener('click', () => this.play());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.volumeSlider.addEventListener('change', (e) => this.setVolume(e.target.value));
        
        this.videoElement.addEventListener('play', () => this.onPlay());
        this.videoElement.addEventListener('pause', () => this.onPause());
        this.videoElement.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.videoElement.addEventListener('loadstart', () => this.onLoadStart());
        this.videoElement.addEventListener('canplay', () => this.onCanPlay());
        this.videoElement.addEventListener('seeking', () => this.onSeeking());
        this.videoElement.addEventListener('seeked', () => this.onSeeked());
        this.videoElement.addEventListener('ended', () => this.onEnded());
    }

    openCourse(courseId, userId) {
        this.currentCourse = courseId;
        this.userId = userId;
        this.metrics.startTime = Date.now();
        this.logAction(`Opened course ${courseId} for user ${userId}`);
        
        // Baseline: No resume functionality
        // Start from beginning
        this.videoElement.currentTime = 0;
        return {
            status: 'ready',
            course_id: courseId,
            user_id: userId,
            current_time_s: 0,
            playback_rate: 1.0,
            quality: 'auto'
        };
    }

    play() {
        this.videoElement.play();
    }

    pause() {
        this.videoElement.pause();
    }

    stop() {
        this.videoElement.pause();
        this.videoElement.currentTime = 0;
        this.updateStatus();
        this.logAction('Stopped playback');
    }

    setVolume(value) {
        const volume = value / 100;
        this.videoElement.volume = volume;
        document.getElementById('volumeDisplay').textContent = value + '%';
        this.logAction(`Set volume to ${value}%`);
    }

    seekTo(time) {
        this.videoElement.currentTime = time;
        this.logAction(`Seeked to ${time.toFixed(2)}s`);
    }

    onPlay() {
        this.updateStatus('Playing');
        this.logAction('Play started');
    }

    onPause() {
        this.updateStatus('Paused');
        this.logAction('Paused');
    }

    onLoadStart() {
        this.updateStatus('Loading');
        this.logAction('Loading started');
    }

    onCanPlay() {
        if (!this.metrics.timeToFirstFrame) {
            this.metrics.timeToFirstFrame = Date.now() - this.metrics.startTime;
            console.log(`Time to first frame: ${this.metrics.timeToFirstFrame}ms`);
        }
        this.updateStatus('Ready');
        this.logAction('Video ready to play');
    }

    onSeeking() {
        this.updateStatus('Seeking');
    }

    onSeeked() {
        this.updateStatus('Seeked');
        this.logAction('Seek completed');
    }

    onTimeUpdate() {
        const progress = (this.videoElement.currentTime / this.videoElement.duration) * 100;
        document.getElementById('progressFill').style.width = progress + '%';
        document.getElementById('currentTime').textContent = this.videoElement.currentTime.toFixed(2);
        document.getElementById('duration').textContent = this.videoElement.duration.toFixed(2);
    }

    onEnded() {
        this.updateStatus('Ended');
        this.logAction('Video playback ended');
    }

    updateStatus(status = null) {
        const video = this.videoElement;
        if (status) {
            document.getElementById('status').textContent = status;
        }
        document.getElementById('currentTime').textContent = video.currentTime.toFixed(2);
        document.getElementById('duration').textContent = video.duration.toFixed(2);
        document.getElementById('playbackRate').textContent = video.playbackRate.toFixed(2) + 'x';
        document.getElementById('volumeDisplay').textContent = Math.round(video.volume * 100) + '%';
    }

    logAction(message) {
        const timestamp = new Date().toLocaleTimeString();
        document.getElementById('lastAction').textContent = `[${timestamp}] ${message}`;
        console.log(`[${timestamp}] ${message}`);
    }

    getPlayerState() {
        return {
            status: this.videoElement.paused ? 'paused' : 'playing',
            current_time_s: this.videoElement.currentTime,
            duration_s: this.videoElement.duration,
            playback_rate: this.videoElement.playbackRate,
            volume: this.videoElement.volume,
            quality: 'auto',
            course_id: this.currentCourse,
            user_id: this.userId
        };
    }

    getMetrics() {
        return {
            time_to_first_frame_ms: this.metrics.timeToFirstFrame,
            stalls_count: this.metrics.stalls,
            stall_durations_ms: this.metrics.stallDurations,
            network_status: this.metrics.networkStatus
        };
    }
}

// Initialize player when DOM is ready
let player;
document.addEventListener('DOMContentLoaded', () => {
    player = new BaselinePlayer();
    
    // For testing purposes, expose globals
    window.playerInstance = player;
    window.getPlayerState = () => player.getPlayerState();
    window.getMetrics = () => player.getMetrics();
});
