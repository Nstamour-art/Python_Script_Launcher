print("This is a long process test file.")
import subprocess

cmd = "ffmpeg -f lavfi -i testsrc=duration=5:size=1280x720:rate=30 -c:v libx264 -pix_fmt yuv420p test.mp4"
subprocess.run(cmd, shell=True)
wait_time = 60
print(f"Waiting for {wait_time} seconds...")
import time

time.sleep(wait_time)
