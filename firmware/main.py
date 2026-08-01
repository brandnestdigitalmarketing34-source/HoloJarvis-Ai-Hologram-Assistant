import pygame
import cv2
import sys
import os
import numpy as np

# Core Configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1000
FPS_CAP = 60

def play_intro_video(screen, video_path):
    """
    Plays an MP4 video smoothly using OpenCV for frames and Pygame for rendering.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return

    # Determine video FPS for playback timing
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 30.0
        
    clock = pygame.time.Clock()
    running = True

    while running and cap.isOpened():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Allow skipping intro
                    running = False

        ret, frame = cap.read()
        if not ret:
            break

        # Convert OpenCV's BGR to Pygame's RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit the window dimensions
        frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Prepare for Pygame surface mapping (requires axes swapped)
        frame = np.swapaxes(frame, 0, 1)
        
        # Render the surface directly onto the screen
        surf = pygame.surfarray.make_surface(frame)
        screen.blit(surf, (0, 0))
        
        pygame.display.update()
        clock.tick(fps)
        
    cap.release()

def display_main_interface(screen, image_path):
    """
    Renders the persistent AI Avatar with HUD overlays.
    """
    try:
        # Load and scale AI image
        ai_image = pygame.image.load(image_path).convert_alpha()
        ai_image = pygame.transform.smoothscale(ai_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except Exception as e:
        print(f"Error loading AI image: {e}")
        ai_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        ai_image.fill((10, 10, 20)) # Dark fallback background

    # Setup HUD Fonts
    try:
        font_main = pygame.font.SysFont("Consolas", 28, bold=True)
        font_sub = pygame.font.SysFont("Consolas", 16)
    except:
        font_main = pygame.font.Font(None, 36)
        font_sub = pygame.font.Font(None, 24)

    title_text = "HoloJarvice: Ai Hologram Assistant"
    hud_color = (0, 255, 200) # Cyan/Teal futuristic color
    
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen to ensure no artifacts
        screen.fill((0, 0, 0))

        # 1. Base Image
        screen.blit(ai_image, (0, 0))

        # 2. HUD Aesthetics
        # Draw frame borders
        pygame.draw.rect(screen, hud_color, (20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40), 2)
        pygame.draw.rect(screen, hud_color, (30, 30, WINDOW_WIDTH - 60, WINDOW_HEIGHT - 60), 1)
        
        # Corner accents
        length = 40
        thickness = 4
        # Top-left
        pygame.draw.line(screen, hud_color, (20, 20), (20 + length, 20), thickness)
        pygame.draw.line(screen, hud_color, (20, 20), (20, 20 + length), thickness)
        # Top-right
        pygame.draw.line(screen, hud_color, (WINDOW_WIDTH - 20, 20), (WINDOW_WIDTH - 20 - length, 20), thickness)
        pygame.draw.line(screen, hud_color, (WINDOW_WIDTH - 20, 20), (WINDOW_WIDTH - 20, 20 + length), thickness)
        # Bottom-left
        pygame.draw.line(screen, hud_color, (20, WINDOW_HEIGHT - 20), (20 + length, WINDOW_HEIGHT - 20), thickness)
        pygame.draw.line(screen, hud_color, (20, WINDOW_HEIGHT - 20), (20, WINDOW_HEIGHT - 20 - length), thickness)
        # Bottom-right
        pygame.draw.line(screen, hud_color, (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), (WINDOW_WIDTH - 20 - length, WINDOW_HEIGHT - 20), thickness)
        pygame.draw.line(screen, hud_color, (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20 - length), thickness)

        # 3. HUD Text overlays
        title_render = font_main.render(title_text, True, hud_color)
        title_shadow = font_main.render(title_text, True, (0, 100, 100))
        title_rect = title_render.get_rect(center=(WINDOW_WIDTH // 2, 60))
        
        # Apply shadow offset
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_render, title_rect)

        # Status text
        status_render = font_sub.render("SYSTEM: ONLINE | AWAITING INPUT", True, hud_color)
        status_rect = status_render.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        screen.blit(status_render, status_rect)

        # Refresh
        pygame.display.flip()
        clock.tick(FPS_CAP)

def main():
    """
    Main entry point for HoloJarvice Assistant.
    """
    # Initialize pygame and mixer for potential future audio
    pygame.init()
    pygame.mixer.init()
    
    pygame.display.set_caption("HoloJarvice Assistant")
    # Setting fixed window, but could use pygame.FULLSCREEN | pygame.SCALED flags if needed
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Path Resolution
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    intro_video_path = os.path.join(assets_dir, "intro.mp4")
    ai_image_path = os.path.join(assets_dir, "ai.png")
    
    # 1. Start sequence
    print("Initiating HoloJarvice Boot Sequence...")
    if os.path.exists(intro_video_path):
        play_intro_video(screen, intro_video_path)
    else:
        print(f"Warning: Intro video not found at {intro_video_path}")

    # 2. Main Persistent Loop
    print("Transitioning to Main Interface...")
    if os.path.exists(ai_image_path):
        display_main_interface(screen, ai_image_path)
    else:
        print(f"Error: AI Avatar image not found at {ai_image_path}")

    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
