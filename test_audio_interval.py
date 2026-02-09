import time

# Simulate the audio interval logic for red light
last_audio_time = None

def should_play_audio(current_time):
    if last_audio_time is None or (current_time - last_audio_time) >= 0.3:
        return True
    return False

def play_audio(current_time):
    global last_audio_time
    last_audio_time = current_time
    print(f"Audio played at {current_time}")

# Test 1: First detection
current_time = time.time()
if should_play_audio(current_time):
    play_audio(current_time)

# Test 2: Immediate second detection (should not play)
time.sleep(0.1)
current_time = time.time()
if should_play_audio(current_time):
    play_audio(current_time)
else:
    print(f"Audio not played at {current_time} (too soon)")

# Test 3: After 0.3 seconds (should play)
time.sleep(0.3)
current_time = time.time()
if should_play_audio(current_time):
    play_audio(current_time)

# Test 4: Rapid detections (simulate loop)
print("\nSimulating rapid detections:")
for i in range(10):
    current_time = time.time()
    if should_play_audio(current_time):
        play_audio(current_time)
    else:
        print(f"Audio not played at {current_time} (interval not met)")
    time.sleep(0.1)  # Simulate frame rate

print("Test completed.")
