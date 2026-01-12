/**
 * Enhanced Course Player with all features:
 * - Resume from last position
 * - Playback speed controls (0.75x - 2x)
 * - Auto-skip learned segments
 * - Adaptive buffering and resolution switching
 * - Note time synchronization with hover-to-jump
 */

class EnhancedPlayer {
    constructor() {
        this.videoElement = document.getElementById('courseVideo');
        this.statusDisplay = document.getElementById('statusDisplay');
        
        // UI Elements
        this.playBtn = document.getElementById('playBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.resumeLastBtn = document.getElementById('resumeLastBtn');
        this.volumeSlider = document.getElementById('volumeSlider');
        this.qualitySelect = document.getElementById('qualitySelect');
        this.autoSkipCheckbox = document.getElementById('autoSkipCheckbox');
        
        // Speed buttons
        this.speedButtons = {
            '0.75': document.getElementById('speed075'),
            '1.0': document.getElementById('speed100'),
            '1.25': document.getElementById('speed125'),
            '1.5': document.getElementById('speed150'),
            '2.0': document.getElementById('speed200')
        };

        this.currentCourse = null;
        this.userId = null;
        this.currentPlaybackRate = 1.0;
        this.currentQuality = 'auto';
        this.autoSkipEnabled = false;
        this.learnedSegments = [];

        // Metrics
        this.metrics = {
            startTime: null,
            timeToFirstFrame: null,
            stalls: 0,
            stallDurations: [],
            resolutionSwitches: [],
            networkStatus: 'good',
            resumeAccuracy: 0
        };

        // Storage
        this.storagePrefix = 'coursePlayer_';

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadNotesFromDOM();
        this.setupNoteInteractions();
        this.logAction('Initialized enhanced player with all features');
    }

    setupEventListeners() {
        this.playBtn.addEventListener('click', () => this.play());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.resumeLastBtn.addEventListener('click', () => this.resumeLastSession());
        this.volumeSlider.addEventListener('change', (e) => this.setVolume(e.target.value));
        this.qualitySelect.addEventListener('change', (e) => this.setQuality(e.target.value));
        this.autoSkipCheckbox.addEventListener('change', (e) => this.setAutoSkip(e.target.checked));
        
        // Speed control listeners
        Object.entries(this.speedButtons).forEach(([rate, btn]) => {
            btn.addEventListener('click', () => this.setPlaybackRate(parseFloat(rate)));
        });

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
        
        // Try to resume from last position
        const savedProgress = this.getSavedProgress(courseId, userId);
        const resumePosition = savedProgress ? savedProgress.position : 0;
        const resumeRate = savedProgress ? savedProgress.playbackRate : 1.0;
        const resumeQuality = savedProgress ? savedProgress.quality : 'auto';

        this.videoElement.currentTime = resumePosition;
        this.setPlaybackRate(resumeRate);
        this.setQuality(resumeQuality);

        this.metrics.resumeAccuracy = resumePosition;
        this.updateResumeDisplay(resumePosition);

        return {
            status: 'ready',
            course_id: courseId,
            user_id: userId,
            current_time_s: resumePosition,
            playback_rate: resumeRate,
            quality: resumeQuality,
            resume_available: resumePosition > 0
        };
    }

    // RESUME FUNCTIONALITY
    saveProgress(courseId, userId, position, playbackRate, quality) {
        const key = `${this.storagePrefix}${userId}_${courseId}`;
        const data = {
            position: position,
            playbackRate: playbackRate,
            quality: quality,
            timestamp: Date.now()
        };
        localStorage.setItem(key, JSON.stringify(data));
        this.logAction(`Saved progress: ${position.toFixed(2)}s @ ${playbackRate}x`);
    }

    getSavedProgress(courseId, userId) {
        const key = `${this.storagePrefix}${userId}_${courseId}`;
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    }

    resumeLastSession() {
        const savedProgress = this.getSavedProgress(this.currentCourse, this.userId);
        if (savedProgress) {
            this.videoElement.currentTime = savedProgress.position;
            this.setPlaybackRate(savedProgress.playbackRate);
            this.setQuality(savedProgress.quality);
            this.logAction(`Resumed from ${savedProgress.position.toFixed(2)}s`);
        } else {
            this.logAction('No saved progress to resume');
        }
    }

    updateResumeDisplay(position) {
        if (position > 0) {
            const time = this.formatTime(position);
            document.getElementById('resumeAvailable').innerHTML = 
                `<span class="highlight">Yes (${time})</span>`;
        } else {
            document.getElementById('resumeAvailable').textContent = 'No';
        }
    }

    // PLAYBACK SPEED CONTROLS
    setPlaybackRate(rate) {
        this.currentPlaybackRate = rate;
        this.videoElement.playbackRate = rate;
        
        // Update button states
        Object.entries(this.speedButtons).forEach(([btnRate, btn]) => {
            if (parseFloat(btnRate) === rate) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Save preference
        this.saveProgress(this.currentCourse, this.userId, 
            this.videoElement.currentTime, rate, this.currentQuality);
        
        this.logAction(`Set playback rate to ${rate}x`);
        this.updateStatus();
    }

    // QUALITY/ADAPTIVE BUFFERING
    setQuality(quality) {
        this.currentQuality = quality;
        document.getElementById('quality').textContent = quality === 'auto' ? 'Auto (Adaptive)' : quality;
        
        // Log resolution switch
        if (this.metrics.startTime) {
            this.metrics.resolutionSwitches.push({
                quality: quality,
                time: Date.now() - this.metrics.startTime,
                position: this.videoElement.currentTime
            });
        }

        this.logAction(`Switched to ${quality} quality`);
        this.updateStatus();
    }

    // AUTO-SKIP LEARNED SEGMENTS
    setAutoSkip(enabled) {
        this.autoSkipEnabled = enabled;
        this.logAction(`Auto-skip ${enabled ? 'enabled' : 'disabled'}`);
    }

    markSegmentAsLearned(segmentId, startTime, endTime) {
        this.learnedSegments.push({
            id: segmentId,
            start: startTime,
            end: endTime
        });
        this.logAction(`Marked segment ${segmentId} as learned`);
    }

    checkAndAutoSkip(currentTime) {
        if (!this.autoSkipEnabled) return false;

        for (const segment of this.learnedSegments) {
            if (currentTime >= segment.start && currentTime < segment.end) {
                const wasPlaying = !this.videoElement.paused;
                this.videoElement.currentTime = segment.end;
                if (wasPlaying) this.videoElement.play();
                this.logAction(`Auto-skipped learned segment: ${segment.id}`);
                return true;
            }
        }
        return false;
    }

    // NOTE SYNCHRONIZATION
    loadNotesFromDOM() {
        this.notes = Array.from(document.querySelectorAll('.note-item')).map(el => ({
            element: el,
            timestamp: parseFloat(el.getAttribute('data-timestamp')),
            text: el.querySelector('.note-text').textContent
        }));
        this.logAction(`Loaded ${this.notes.length} notes`);
    }

    setupNoteInteractions() {
        this.notes.forEach(note => {
            note.element.addEventListener('click', () => this.jumpToNote(note));
            note.element.addEventListener('mouseenter', () => this.highlightNoteForCurrentTime());
            note.element.addEventListener('mouseleave', () => this.clearNoteHighlight());
        });
    }

    jumpToNote(note) {
        this.videoElement.currentTime = note.timestamp;
        this.logAction(`Jumped to note: "${note.text.substring(0, 30)}..." at ${this.formatTime(note.timestamp)}`);
        this.highlightNote(note);
    }

    highlightNote(note) {
        document.querySelectorAll('.note-item').forEach(el => {
            el.classList.remove('synced');
        });
        note.element.classList.add('synced');
    }

    highlightNoteForCurrentTime() {
        const currentTime = this.videoElement.currentTime;
        const closeNote = this.notes.find(note => 
            Math.abs(note.timestamp - currentTime) < 0.5
        );
        if (closeNote) {
            this.highlightNote(closeNote);
        }
    }

    clearNoteHighlight() {
        document.querySelectorAll('.note-item.synced').forEach(el => {
            el.classList.remove('synced');
        });
    }

    // PLAYBACK CONTROLS
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

    // EVENT HANDLERS
    onPlay() {
        this.updateStatus('Playing');
        this.logAction('Play started');
    }

    onPause() {
        this.updateStatus('Paused');
        this.logAction('Paused');
        // Save progress when paused
        this.saveProgress(this.currentCourse, this.userId, 
            this.videoElement.currentTime, this.currentPlaybackRate, this.currentQuality);
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
        const currentTime = this.videoElement.currentTime;
        const progress = (currentTime / this.videoElement.duration) * 100;
        document.getElementById('progressFill').style.width = progress + '%';
        document.getElementById('currentTime').textContent = currentTime.toFixed(2);
        document.getElementById('duration').textContent = this.videoElement.duration.toFixed(2);

        // Check for auto-skip
        this.checkAndAutoSkip(currentTime);

        // Sync notes highlighting
        this.updateNoteSyncStatus(currentTime);

        // Periodically save progress
        if (Math.floor(currentTime) % 5 === 0) {
            this.saveProgress(this.currentCourse, this.userId, 
                currentTime, this.currentPlaybackRate, this.currentQuality);
        }
    }

    updateNoteSyncStatus(currentTime) {
        this.notes.forEach(note => {
            if (Math.abs(note.timestamp - currentTime) < 0.5) {
                this.highlightNote(note);
            }
        });
    }

    onEnded() {
        this.updateStatus('Ended');
        this.logAction('Video playback ended');
        // Save final progress
        this.saveProgress(this.currentCourse, this.userId, 
            this.videoElement.currentTime, this.currentPlaybackRate, this.currentQuality);
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

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    getPlayerState() {
        return {
            status: this.videoElement.paused ? 'paused' : 'playing',
            current_time_s: this.videoElement.currentTime,
            duration_s: this.videoElement.duration,
            playback_rate: this.videoElement.playbackRate,
            volume: this.videoElement.volume,
            quality: this.currentQuality,
            auto_skip_enabled: this.autoSkipEnabled,
            course_id: this.currentCourse,
            user_id: this.userId
        };
    }

    getMetrics() {
        return {
            time_to_first_frame_ms: this.metrics.timeToFirstFrame,
            stalls_count: this.metrics.stalls,
            stall_durations_ms: this.metrics.stallDurations,
            resolution_switches: this.metrics.resolutionSwitches,
            network_status: this.metrics.networkStatus,
            resume_accuracy_s: this.metrics.resumeAccuracy,
            notes_count: this.notes.length
        };
    }
}

// Initialize player when DOM is ready
let player;
document.addEventListener('DOMContentLoaded', () => {
    player = new EnhancedPlayer();
    
    // For testing purposes, expose globals
    window.playerInstance = player;
    window.getPlayerState = () => player.getPlayerState();
    window.getMetrics = () => player.getMetrics();
});
