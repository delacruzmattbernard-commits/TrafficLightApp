import os
import sys
import time

# Add the current directory to sys.path to import AudioManager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_utils import AudioManager

def test_audio_manager():
    print("Testing AudioManager...")

    # Test 1: Initialize AudioManager
    try:
        audio_manager = AudioManager()
        print("✓ AudioManager initialized successfully.")
    except Exception as e:
        print(f"✗ Failed to initialize AudioManager: {e}")
        return

    # Test 2: Check if sound configs are loaded
    expected_sounds = ['red', 'yellow', 'green']
    for color in expected_sounds:
        if color in audio_manager.sound_configs and audio_manager.sound_configs[color]:
            print(f"✓ Sound config for {color} loaded successfully.")
        else:
            print(f"✗ Sound config for {color} not loaded.")

    # Test 3: Test audio enabled by default
    if audio_manager.is_enabled():
        print("✓ Audio is enabled by default.")
    else:
        print("✗ Audio is not enabled by default.")

    # Test 4: Test toggle audio
    original_state = audio_manager.is_enabled()
    new_state = audio_manager.toggle_audio()
    if new_state != original_state:
        print("✓ Audio toggle works.")
    else:
        print("✗ Audio toggle failed.")

    # Toggle back
    audio_manager.toggle_audio()

    # Test 5: Test play_sound (simulate, since actual play might not be audible in test)
    # Note: Actual sound play can't be verified in a headless test, but we can check if the method runs without error
    for color in expected_sounds:
        try:
            audio_manager.play_sound(color)
            print(f"✓ play_sound('{color}') executed without error.")
        except Exception as e:
            print(f"✗ play_sound('{color}') failed: {e}")

    # Test 6: Test play_sound when audio disabled
    audio_manager.toggle_audio()  # Disable
    try:
        audio_manager.play_sound('red')
        print("✓ play_sound works when audio disabled (should not play).")
    except Exception as e:
        print(f"✗ play_sound failed when disabled: {e}")
    audio_manager.toggle_audio()  # Re-enable

    # Test 7: Test invalid color
    try:
        audio_manager.play_sound('invalid')
        print("✓ play_sound handles invalid color gracefully.")
    except Exception as e:
        print(f"✗ play_sound failed for invalid color: {e}")

    print("AudioManager testing completed.")

if __name__ == '__main__':
    test_audio_manager()
