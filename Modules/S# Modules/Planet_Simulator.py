import pygame
import numpy as np
import math
from scipy.ndimage import gaussian_filter

# Initialize Pygame
pygame.init()

# Get screen dimensions and aspect ratio
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h
aspect_ratio = screen_width / screen_height

# Rendering resolution (keeping total pixels approximately the same)
TOTAL_PIXELS = 160_000  # Adjust as needed for performance
RENDER_HEIGHT = int(math.sqrt(TOTAL_PIXELS / aspect_ratio))
RENDER_WIDTH = int(RENDER_HEIGHT * aspect_ratio)

# Set the display mode to fullscreen
SCREEN = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Planetary Interactive Simulation System")

# Create a render surface with the desired rendering resolution
render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))

# Clock for controlling FPS
CLOCK = pygame.time.Clock()

# Planet parameters
PLANET_RADIUS = RENDER_HEIGHT // 3  # Adjust as needed
CLOUD_RADIUS = PLANET_RADIUS + 10

# Adjusted light source direction
LIGHT_SOURCE = np.array([1, 1, 1], dtype=float)
LIGHT_SOURCE /= np.linalg.norm(LIGHT_SOURCE)  # Normalize light source vector

# Rotation angle
rotation_angle = 0

# Noise parameters
terrain_noise_scale = 8  # Increased for more variation
cloud_noise_scale = 5
city_noise_scale = 10.0
noise_offset = 0

# Color palettes
water_color = np.array([30, 144, 255])  # Dodger Blue
land_color = np.array([34, 139, 34])    # Forest Green
mountain_color = np.array([139, 69, 19]) # Saddle Brown
snow_color = np.array([255, 250, 250])   # Snow

cloud_color = np.array([255, 255, 255])  # White
city_light_color = np.array([255, 215, 0])  # Gold

# Generate 2D noise maps for terrain and city lights
noise_size = 512  # Increased size for better detail
terrain_noise_image = np.random.rand(noise_size, noise_size)
terrain_noise_image = gaussian_filter(terrain_noise_image, sigma=terrain_noise_scale)
terrain_noise_image = (terrain_noise_image - terrain_noise_image.min()) / (terrain_noise_image.max() - terrain_noise_image.min())  # Normalize to [0, 1]

city_noise_image = np.random.rand(noise_size, noise_size)
city_noise_image = gaussian_filter(city_noise_image, sigma=city_noise_scale)

# Generate clouds noise image once
clouds_noise_image_base = np.random.rand(noise_size, noise_size)
clouds_noise_image_base = gaussian_filter(clouds_noise_image_base, sigma=cloud_noise_scale)
clouds_noise_image_base = (clouds_noise_image_base - clouds_noise_image_base.min()) / (clouds_noise_image_base.max() - clouds_noise_image_base.min())

# Planet position (adjust these values to move the planet)
# Values are in pixels within the render_surface
PLANET_POS_X = RENDER_WIDTH // 2    # Centered horizontally
PLANET_POS_Y = RENDER_HEIGHT // 2   # Centered vertically

def draw_planet():
    global rotation_angle, noise_offset

    # Create an array representing the render surface
    screen_array = np.zeros((RENDER_HEIGHT, RENDER_WIDTH, 3), dtype=np.uint8)

    # Coordinate grid centered at the planet's position
    y_indices, x_indices = np.indices((RENDER_HEIGHT, RENDER_WIDTH))
    x = x_indices - PLANET_POS_X
    y = y_indices - PLANET_POS_Y

    # Planet mask
    planet_mask = x**2 + y**2 <= PLANET_RADIUS**2

    # Normalize coordinates
    nx = x / PLANET_RADIUS
    ny = y / PLANET_RADIUS
    with np.errstate(invalid='ignore', divide='ignore'):
        nz = np.sqrt(1 - nx**2 - ny**2)
    nz = np.nan_to_num(nz)

    # Stack normals
    normals = np.stack((nx, ny, nz), axis=-1)

    # Rotate normals around the Y-axis by -90 degrees to change the viewpoint
    cos_tilt = math.cos(-np.pi / 2)
    sin_tilt = math.sin(-np.pi / 2)
    tilt_matrix = np.array([
        [cos_tilt, 0, sin_tilt],
        [0,        1,      0  ],
        [-sin_tilt,0, cos_tilt]
    ])
    normals = normals @ tilt_matrix.T

    # Rotation matrix around the Z-axis (polar axis)
    cos_angle = math.cos(rotation_angle)
    sin_angle = math.sin(rotation_angle)
    rotation_matrix = np.array([
        [cos_angle, -sin_angle, 0],
        [sin_angle,  cos_angle, 0],
        [0,          0,         1]
    ])

    # Rotate normals around the Z-axis
    rotated_normals = normals @ rotation_matrix.T

    # Compute brightness
    brightness = np.einsum('ijk,k->ij', rotated_normals, LIGHT_SOURCE)
    brightness = np.clip(brightness, 0, 1)

    # Compute theta and phi from rotated normals
    with np.errstate(invalid='ignore'):
        theta = np.arccos(rotated_normals[:, :, 2])  # Range [0, π]
        phi = np.arctan2(rotated_normals[:, :, 1], rotated_normals[:, :, 0])  # Range [-π, π]
    theta = np.nan_to_num(theta)
    phi = np.nan_to_num(phi)

    # Normalize theta and phi to [0, 1]
    theta_normalized = theta / np.pi
    phi_normalized = (phi + np.pi) / (2 * np.pi)

    # Map to noise texture
    noise_x = (phi_normalized * (noise_size - 1)).astype(int)
    noise_y = (theta_normalized * (noise_size - 1)).astype(int)

    # Ensure indices are within bounds
    noise_x = np.clip(noise_x, 0, noise_size - 1)
    noise_y = np.clip(noise_y, 0, noise_size - 1)

    # Get terrain noise values
    terrain_noise = terrain_noise_image[noise_y, noise_x]

    # Determine terrain type based on elevation
    water_threshold = 0.4
    mountain_threshold = 0.7
    snow_threshold = 0.85

    terrain_color = np.zeros((RENDER_HEIGHT, RENDER_WIDTH, 3))

    # Water
    water_mask = terrain_noise <= water_threshold
    terrain_color[water_mask] = water_color

    # Land
    land_mask = (terrain_noise > water_threshold) & (terrain_noise <= mountain_threshold)
    terrain_color[land_mask] = land_color

    # Mountains
    mountain_mask = (terrain_noise > mountain_threshold) & (terrain_noise <= snow_threshold)
    terrain_color[mountain_mask] = mountain_color

    # Snow
    snow_mask = terrain_noise > snow_threshold
    terrain_color[snow_mask] = snow_color

    # Apply lighting
    terrain_color = np.clip(terrain_color * brightness[..., None], 0, 255)

    # Add city lights on the dark side
    dark_side = brightness < 0.2
    city_noise = city_noise_image[noise_y, noise_x]
    city_lights_mask = (city_noise > 0.8) & planet_mask & dark_side
    terrain_color[city_lights_mask] = city_light_color

    # Apply planet mask
    screen_array[planet_mask] = terrain_color[planet_mask].astype(np.uint8)

    # Clouds
    # Shift clouds noise image to simulate movement
    clouds_noise_shifted = np.roll(clouds_noise_image_base, int(noise_offset), axis=1)

    # Get clouds noise values
    clouds_noise = clouds_noise_shifted[noise_y, noise_x]

    # Adjust cloud threshold to reduce clouds
    cloud_threshold = 0.7  # Increase this value to reduce clouds
    clouds_mask = (clouds_noise > cloud_threshold) & (x**2 + y**2 <= CLOUD_RADIUS**2)

    # Calculate cloud brightness
    cloud_brightness = brightness * (0.7 + 0.3 * clouds_noise)

    # Apply clouds to the screen array
    screen_array[clouds_mask] = np.clip(cloud_color * cloud_brightness[clouds_mask, None], 0, 255).astype(np.uint8)

    # Convert the array to a surface
    # Swap axes to match Pygame's (width, height) format
    surface_from_array = pygame.surfarray.make_surface(screen_array.swapaxes(0, 1))

    # Blit the surface onto the render_surface
    render_surface.blit(surface_from_array, (0, 0))

    # Update rotation angle and noise offset
    rotation_angle += 0.01  # Adjust rotation speed as needed
    noise_offset += 0.5     # Adjust cloud movement speed as needed

def main():
    running = True
    while running:
        CLOCK.tick(30)  # Limit to 30 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Allow exiting fullscreen with ESC key
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_planet()

        # Rotate the render_surface by 90 degrees
        rotated_render_surface = pygame.transform.rotate(render_surface, 90)

        # After rotation, the dimensions are swapped
        rotated_width, rotated_height = rotated_render_surface.get_size()

        # Calculate scale factors to maintain aspect ratio
        scale_x = screen_width / rotated_width
        scale_y = screen_height / rotated_height
        scale_factor = min(scale_x, scale_y)

        # Calculate new dimensions
        scaled_width = int(rotated_width * scale_factor)
        scaled_height = int(rotated_height * scale_factor)

        # Scale the rotated render surface to the new dimensions
        scaled_surface = pygame.transform.scale(rotated_render_surface, (scaled_width, scaled_height))

        # Calculate position to center the image
        x_offset = (screen_width - scaled_width) // 2
        y_offset = (screen_height - scaled_height) // 2

        # Fill the screen with black before blitting (in case of borders)
        SCREEN.fill((0, 0, 0))

        # Blit the scaled surface onto the SCREEN
        SCREEN.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
