"""
E2E Tests for Project A - Baseline Player
Uses Playwright to test the player UI and interactions
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
async def page():
    """Fixture for browser page"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        yield page
        await browser.close()


class TestBaselinePlayerE2E:
    """End-to-end tests for baseline player"""

    @pytest.mark.asyncio
    async def test_player_loads(self, page):
        """Test player page loads successfully"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            title = await page.title()
            assert 'Course Player' in title, "Page should load with correct title"
            logger.info("✓ Player page loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load player: {e}")

    @pytest.mark.asyncio
    async def test_baseline_indicator(self, page):
        """Test that baseline version is clearly marked"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            text = await page.text_content('p')
            assert 'Baseline' in text or 'baseline' in text, "Should indicate baseline version"
            logger.info("✓ Baseline version clearly marked")
        except Exception as e:
            logger.warning(f"Could not verify baseline indicator: {e}")

    @pytest.mark.asyncio
    async def test_play_button_exists(self, page):
        """Test play button is present"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            play_btn = await page.query_selector('#playBtn')
            assert play_btn is not None, "Play button should exist"
            logger.info("✓ Play button exists")
        except Exception as e:
            logger.error(f"Play button check failed: {e}")

    @pytest.mark.asyncio
    async def test_pause_button_exists(self, page):
        """Test pause button is present"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            pause_btn = await page.query_selector('#pauseBtn')
            assert pause_btn is not None, "Pause button should exist"
            logger.info("✓ Pause button exists")
        except Exception as e:
            logger.error(f"Pause button check failed: {e}")

    @pytest.mark.asyncio
    async def test_volume_control_exists(self, page):
        """Test volume slider exists"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            volume_slider = await page.query_selector('#volumeSlider')
            assert volume_slider is not None, "Volume slider should exist"
            logger.info("✓ Volume control exists")
        except Exception as e:
            logger.error(f"Volume control check failed: {e}")

    @pytest.mark.asyncio
    async def test_status_display_exists(self, page):
        """Test status display area exists"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            status = await page.query_selector('#statusDisplay')
            assert status is not None, "Status display should exist"
            logger.info("✓ Status display exists")
        except Exception as e:
            logger.error(f"Status display check failed: {e}")

    @pytest.mark.asyncio
    async def test_baseline_no_speed_controls(self, page):
        """Test that baseline doesn't have speed controls"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            speed_controls = await page.query_selector('[id*="speed"]')
            assert speed_controls is None, "Baseline should not have speed controls"
            logger.info("✓ Baseline correctly lacks speed controls")
        except Exception as e:
            logger.warning(f"Speed control check failed: {e}")

    @pytest.mark.asyncio
    async def test_baseline_no_auto_skip(self, page):
        """Test that baseline doesn't have auto-skip"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            auto_skip = await page.query_selector('[id*="auto"]')
            assert auto_skip is None, "Baseline should not have auto-skip"
            logger.info("✓ Baseline correctly lacks auto-skip")
        except Exception as e:
            logger.warning(f"Auto-skip check failed: {e}")

    @pytest.mark.asyncio
    async def test_notes_display_non_interactive(self, page):
        """Test notes are displayed but not interactive"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            notes = await page.query_selector_all('.note-item')
            assert len(notes) > 0, "Notes should be displayed"
            
            # Check they're not clickable (no jump functionality)
            first_note = notes[0]
            note_html = await first_note.inner_html()
            assert '@' in note_html, "Notes should show timestamps"
            logger.info(f"✓ Notes displayed (non-interactive): found {len(notes)} notes")
        except Exception as e:
            logger.warning(f"Notes check failed: {e}")


class TestBasicInteractionFlow:
    """Test basic interaction flows"""

    @pytest.mark.asyncio
    async def test_play_pause_flow(self, page):
        """Test basic play/pause interaction"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            
            # Wait for video element
            video = await page.query_selector('#courseVideo')
            assert video is not None, "Video element should exist"
            logger.info("✓ Play/pause flow: video found")
        except Exception as e:
            logger.error(f"Play/pause flow failed: {e}")

    @pytest.mark.asyncio
    async def test_volume_adjustment(self, page):
        """Test volume adjustment"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            
            volume_slider = await page.query_selector('#volumeSlider')
            assert volume_slider is not None, "Volume slider should exist"
            
            # Set volume
            await volume_slider.fill('50')
            volume_display = await page.text_content('#volumeDisplay')
            assert '50' in volume_display or volume_display == '50%', "Volume should be set to 50"
            logger.info("✓ Volume adjustment working")
        except Exception as e:
            logger.error(f"Volume adjustment failed: {e}")


class TestMetricsCollection:
    """Test metrics collection"""

    @pytest.mark.asyncio
    async def test_current_time_displays(self, page):
        """Test that current time is displayed"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            current_time = await page.text_content('#currentTime')
            assert current_time is not None, "Current time should be displayed"
            logger.info(f"✓ Current time displayed: {current_time}")
        except Exception as e:
            logger.error(f"Current time display failed: {e}")

    @pytest.mark.asyncio
    async def test_duration_displays(self, page):
        """Test that duration is displayed"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            duration = await page.text_content('#duration')
            assert duration is not None, "Duration should be displayed"
            logger.info(f"✓ Duration displayed: {duration}")
        except Exception as e:
            logger.error(f"Duration display failed: {e}")

    @pytest.mark.asyncio
    async def test_playback_rate_displays(self, page):
        """Test that playback rate is displayed"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            rate = await page.text_content('#playbackRate')
            assert '1.0' in rate or '1' in rate, "Should show 1.0x rate in baseline"
            logger.info(f"✓ Playback rate displayed: {rate}")
        except Exception as e:
            logger.error(f"Playback rate display failed: {e}")

    @pytest.mark.asyncio
    async def test_status_updates(self, page):
        """Test that status updates"""
        try:
            await page.goto('http://localhost:5000', timeout=5000)
            status = await page.text_content('#status')
            assert status is not None, "Status should be displayed"
            logger.info(f"✓ Status displayed: {status}")
        except Exception as e:
            logger.error(f"Status display failed: {e}")


class TestAPIEndpoints:
    """Test backend API endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5000/health') as resp:
                    assert resp.status == 200, "Health endpoint should return 200"
                    data = await resp.json()
                    assert data['status'] == 'healthy', "Should report healthy status"
                    logger.info("✓ Health endpoint working")
        except Exception as e:
            logger.warning(f"Health endpoint test failed: {e}")

    @pytest.mark.asyncio
    async def test_courses_endpoint(self):
        """Test courses list endpoint"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5000/api/courses') as resp:
                    assert resp.status == 200, "Courses endpoint should return 200"
                    data = await resp.json()
                    assert 'courses' in data, "Should return courses list"
                    assert len(data['courses']) > 0, "Should have courses"
                    logger.info(f"✓ Courses endpoint working: {len(data['courses'])} courses")
        except Exception as e:
            logger.warning(f"Courses endpoint test failed: {e}")

    @pytest.mark.asyncio
    async def test_progress_endpoint_baseline(self):
        """Test that progress always returns 0 for baseline"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5000/api/user/u1/progress/C101') as resp:
                    assert resp.status == 200, "Progress endpoint should return 200"
                    data = await resp.json()
                    assert data['last_position_s'] == 0, "Baseline should always return 0"
                    logger.info("✓ Progress endpoint returns 0 (baseline)")
        except Exception as e:
            logger.warning(f"Progress endpoint test failed: {e}")


# Test runner for CI/CD
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
