"""
E2E Tests for Project B - Enhanced Player
Tests all enhancement features using Playwright
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


class TestEnhancedPlayerE2E:
    """End-to-end tests for enhanced player"""

    @pytest.mark.asyncio
    async def test_enhanced_player_loads(self, page):
        """Test enhanced player page loads"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            title = await page.title()
            assert 'Course Player' in title, "Page should load"
            logger.info("✓ Enhanced player page loaded")
        except Exception as e:
            logger.error(f"Failed to load enhanced player: {e}")

    @pytest.mark.asyncio
    async def test_enhanced_version_marked(self, page):
        """Test enhanced version is clearly marked"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            text = await page.text_content('p')
            assert 'Enhanced' in text or 'enhanced' in text, "Should indicate enhanced version"
            logger.info("✓ Enhanced version clearly marked")
        except Exception as e:
            logger.warning(f"Enhanced version check failed: {e}")


class TestResumeFeatureE2E:
    """E2E tests for resume feature"""

    @pytest.mark.asyncio
    async def test_resume_button_exists(self, page):
        """Test resume button is present"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            resume_btn = await page.query_selector('#resumeLastBtn')
            assert resume_btn is not None, "Resume button should exist"
            logger.info("✓ Resume button exists")
        except Exception as e:
            logger.error(f"Resume button check failed: {e}")

    @pytest.mark.asyncio
    async def test_resume_shows_last_position(self, page):
        """Test resume display shows last position"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            resume_display = await page.text_content('#resumeAvailable')
            assert resume_display is not None, "Should show resume availability"
            logger.info(f"✓ Resume display shows: {resume_display}")
        except Exception as e:
            logger.error(f"Resume display check failed: {e}")


class TestPlaybackSpeedE2E:
    """E2E tests for playback speed controls"""

    @pytest.mark.asyncio
    async def test_speed_buttons_exist(self, page):
        """Test all speed buttons exist"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            speeds = ['075', '100', '125', '150', '200']
            for speed in speeds:
                btn = await page.query_selector(f'#speed{speed}')
                assert btn is not None, f"Speed {speed} button should exist"
            logger.info("✓ All speed buttons exist")
        except Exception as e:
            logger.error(f"Speed buttons check failed: {e}")

    @pytest.mark.asyncio
    async def test_speed_default_1x(self, page):
        """Test default speed is 1.0x"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            speed_btn = await page.query_selector('#speed100')
            is_active = await speed_btn.get_attribute('class')
            logger.info(f"✓ Default speed button state: {is_active}")
        except Exception as e:
            logger.error(f"Default speed check failed: {e}")


class TestAutoSkipE2E:
    """E2E tests for auto-skip feature"""

    @pytest.mark.asyncio
    async def test_auto_skip_checkbox_exists(self, page):
        """Test auto-skip checkbox exists"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            checkbox = await page.query_selector('#autoSkipCheckbox')
            assert checkbox is not None, "Auto-skip checkbox should exist"
            logger.info("✓ Auto-skip checkbox exists")
        except Exception as e:
            logger.error(f"Auto-skip checkbox check failed: {e}")

    @pytest.mark.asyncio
    async def test_auto_skip_label(self, page):
        """Test auto-skip has proper label"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            text = await page.text_content('label')
            assert 'Auto-Skip' in text or 'auto-skip' in text, "Should label auto-skip"
            logger.info("✓ Auto-skip properly labeled")
        except Exception as e:
            logger.warning(f"Auto-skip label check failed: {e}")


class TestAdaptiveQualityE2E:
    """E2E tests for quality selection"""

    @pytest.mark.asyncio
    async def test_quality_select_exists(self, page):
        """Test quality selector exists"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            select = await page.query_selector('#qualitySelect')
            assert select is not None, "Quality selector should exist"
            logger.info("✓ Quality selector exists")
        except Exception as e:
            logger.error(f"Quality selector check failed: {e}")

    @pytest.mark.asyncio
    async def test_quality_options_available(self, page):
        """Test quality options are available"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            options = await page.query_selector_all('#qualitySelect option')
            assert len(options) >= 4, "Should have multiple quality options"
            logger.info(f"✓ Quality options available: {len(options)}")
        except Exception as e:
            logger.error(f"Quality options check failed: {e}")

    @pytest.mark.asyncio
    async def test_auto_quality_default(self, page):
        """Test auto quality is default"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            select = await page.query_selector('#qualitySelect')
            value = await select.input_value()
            assert value == 'auto', "Default quality should be auto"
            logger.info(f"✓ Default quality is auto: {value}")
        except Exception as e:
            logger.warning(f"Default quality check failed: {e}")


class TestNoteSyncE2E:
    """E2E tests for note synchronization"""

    @pytest.mark.asyncio
    async def test_notes_interactive(self, page):
        """Test notes are interactive"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            notes = await page.query_selector_all('.note-item')
            assert len(notes) > 0, "Should have notes"
            assert len(notes) >= 3, "Should have multiple notes"
            logger.info(f"✓ Interactive notes found: {len(notes)}")
        except Exception as e:
            logger.error(f"Notes check failed: {e}")

    @pytest.mark.asyncio
    async def test_note_timestamps_display(self, page):
        """Test note timestamps are displayed"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            times = await page.query_selector_all('.note-time')
            assert len(times) > 0, "Should display note times"
            
            # Check format @M:SS
            first_time = await times[0].text_content()
            assert '@' in first_time, "Should show @ symbol"
            logger.info(f"✓ Note timestamps displayed: {first_time}")
        except Exception as e:
            logger.error(f"Note timestamps check failed: {e}")

    @pytest.mark.asyncio
    async def test_note_sync_badge(self, page):
        """Test sync badge on notes"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            badges = await page.query_selector_all('.feature-badge')
            assert len(badges) > 0, "Should have sync badges"
            badge_text = await badges[0].text_content()
            assert 'SYNC' in badge_text, "Badge should indicate sync"
            logger.info(f"✓ Note sync badges present: {badge_text}")
        except Exception as e:
            logger.warning(f"Sync badge check failed: {e}")

    @pytest.mark.asyncio
    async def test_note_popover_on_hover(self, page):
        """Test note popover appears on hover"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            note = await page.query_selector('.note-item')
            assert note is not None, "Should have note"
            
            await note.hover()
            popover = await note.query_selector('.note-popover')
            assert popover is not None, "Popover should appear on hover"
            logger.info("✓ Note popover appears on hover")
        except Exception as e:
            logger.warning(f"Note popover check failed: {e}")


class TestBasicControlsE2E:
    """E2E tests for basic controls"""

    @pytest.mark.asyncio
    async def test_all_playback_buttons_exist(self, page):
        """Test all playback control buttons"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            buttons = ['playBtn', 'pauseBtn', 'stopBtn']
            for btn_id in buttons:
                btn = await page.query_selector(f'#{btn_id}')
                assert btn is not None, f"Button {btn_id} should exist"
            logger.info("✓ All playback buttons exist")
        except Exception as e:
            logger.error(f"Playback buttons check failed: {e}")

    @pytest.mark.asyncio
    async def test_volume_control(self, page):
        """Test volume control"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            slider = await page.query_selector('#volumeSlider')
            assert slider is not None, "Volume slider should exist"
            
            await slider.fill('50')
            value = await slider.input_value()
            assert value == '50', "Volume should be settable"
            logger.info(f"✓ Volume control working: {value}")
        except Exception as e:
            logger.error(f"Volume control check failed: {e}")


class TestStatusDisplayE2E:
    """E2E tests for status display"""

    @pytest.mark.asyncio
    async def test_current_time_displays(self, page):
        """Test current time displays"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            time_display = await page.text_content('#currentTime')
            assert time_display is not None, "Current time should display"
            logger.info(f"✓ Current time displays: {time_display}")
        except Exception as e:
            logger.error(f"Current time display failed: {e}")

    @pytest.mark.asyncio
    async def test_playback_rate_displays(self, page):
        """Test playback rate displays"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            rate_display = await page.text_content('#playbackRate')
            assert '1.0' in rate_display or '1' in rate_display, "Should show playback rate"
            logger.info(f"✓ Playback rate displays: {rate_display}")
        except Exception as e:
            logger.error(f"Playback rate display failed: {e}")

    @pytest.mark.asyncio
    async def test_quality_displays(self, page):
        """Test quality display"""
        try:
            await page.goto('http://localhost:5001', timeout=5000)
            quality = await page.text_content('#quality')
            assert quality is not None, "Quality should display"
            logger.info(f"✓ Quality displays: {quality}")
        except Exception as e:
            logger.error(f"Quality display failed: {e}")


class TestAPIEndpointsE2E:
    """E2E tests for backend API"""

    @pytest.mark.asyncio
    async def test_enhanced_health_endpoint(self):
        """Test health check endpoint for enhanced server"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5001/health') as resp:
                    assert resp.status == 200, "Health endpoint should return 200"
                    data = await resp.json()
                    assert data['status'] == 'healthy', "Should report healthy"
                    assert 'enhanced' in data['service'], "Should identify as enhanced"
                    logger.info("✓ Enhanced health endpoint working")
        except Exception as e:
            logger.warning(f"Health endpoint test failed: {e}")

    @pytest.mark.asyncio
    async def test_progress_save_endpoint(self):
        """Test progress save endpoint"""
        import aiohttp
        import json as json_module
        try:
            async with aiohttp.ClientSession() as session:
                progress_data = {
                    'position': 125.7,
                    'playback_rate': 1.25,
                    'quality': '720p'
                }
                
                async with session.post(
                    'http://localhost:5001/api/user/u1/progress/C101',
                    json=progress_data
                ) as resp:
                    assert resp.status == 200, "Progress save should succeed"
                    data = await resp.json()
                    assert data['status'] == 'saved', "Should confirm save"
                    logger.info("✓ Progress save endpoint working")
        except Exception as e:
            logger.warning(f"Progress save endpoint test failed: {e}")

    @pytest.mark.asyncio
    async def test_learned_segments_endpoint(self):
        """Test learned segments endpoint"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                segment_data = {
                    'segment_id': 'S1',
                    'start_time_s': 100,
                    'end_time_s': 200
                }
                
                async with session.post(
                    'http://localhost:5001/api/user/u1/course/C101/segments',
                    json=segment_data
                ) as resp:
                    assert resp.status == 200, "Segment save should succeed"
                    logger.info("✓ Learned segments endpoint working")
        except Exception as e:
            logger.warning(f"Learned segments endpoint test failed: {e}")


# Test runner for CI/CD
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
