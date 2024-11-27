import pygame
from moviepy.editor import VideoFileClip
import sys

# Settings
video_path = "your_video.mp4"  # Replace with your video file
initial_speed = 1.0  # Playback speed multiplier

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Video Player")
clock = pygame.time.Clock()

# Load video
clip = VideoFileClip(video_path)
video_fps = clip.fps
video_width, video_height = clip.size
video_surface = pygame.Surface((video_width, video_height))

# Variables
speed = initial_speed
reverse = False
frame_index = 0

# Video frames as surfaces
frames = []
for frame in clip.iter_frames(fps=video_fps, dtype="uint8"):
    frames.append(pygame.image.frombuffer(frame.tobytes(), clip.size, "RGB"))

frame_count = len(frames)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:  # Increase speed
                speed += 0.1
            elif event.key == pygame.K_DOWN:  # Decrease speed
                speed = max(0.1, speed - 0.1)
            elif event.key == pygame.K_r:  # Toggle reverse
                reverse = not reverse

    # Update frame index
    frame_index += -speed if reverse else speed
    frame_index %= frame_count  # Loop video

    # Display the frame
    current_frame = frames[int(frame_index) % frame_count]
    screen.blit(pygame.transform.scale(current_frame, screen.get_size()), (0, 0))
    pygame.display.flip()

    # Cap frame rate to video FPS
    clock.tick(video_fps)

# Cleanup
pygame.quit()
sys.exit()
