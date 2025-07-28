import asyncio
import platform
import pygame
import sys
import random
import os

# Helper to find resources in PyInstaller bundle or dev
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Constants
FPS = 60
WINDOW_SIZE = (800, 600)
BG_COLOR = (245, 245, 245)
TEXT_COLOR = (30, 30, 30)
BUTTON_COLOR = (76, 175, 80)
BUTTON_HOVER_COLOR = (56, 142, 60)
BUTTON_TEXT_COLOR = (255, 255, 255)
TIMER_COLOR = (33, 150, 243)
ROUND_TOTAL = 4  # We'll show 4 rounds, randomly selected from 5 possible rounds

# Image size constants for each round and phase
# Regular instruction images size (for rounds without special handling)
INSTRUCTION_IMAGE_SIZE = (300, 300)

# Sizes for the black wheel in different contexts
WHEEL_SIZE = {
    "startup": (120, 160),
    "instruction": (120, 160),
    "attempt": (120, 160)
}

# Sizes for the blue arrows in different contexts
BLUE_ARROWS_SIZE = {
    "startup": (500, 500),
    "instruction": (500, 500),
    "attempt": (500, 500)
}

# Sizes for clockwise/counterclockwise green arrows
GREEN_ARROW_SIZE = {
    "instruction": (500, 500),
    "attempt": (500, 500)
}

# Asset filenames (update as needed)
INSTRUCTION_IMAGES = [
    "egely wheel graphic clockwise .png",
    "egely wheel counter clockwise .png",
    "Egely Wheel Graphic both directions.png",
    "Egely wheel no background graphic counter clockwise.png",
    "light_blue_arrows_transparent.png"  # New image for 5th round
]
INSTRUCTIONS = [
    "Spin Clockwise",
    "Spin Counter Clockwise",
    "Spin Clockwise or Counter Clockwise",
    "Spin Fast in Either Direction",
    "Spin Clockwise then Counter Clockwise"  # New instruction for 5th round
]
INSTRUCTION_AUDIO = [
    "spin clockwise.mp3",
    "spin counter clockwise.mp3",
    "spin clockwise or counter clockwise.mp3",
    "Spin fast in either direction.mp3",
    "spin clockwise 1 to roations then anti clockwise 1 to 2 rotations.mp3"  # New audio for 5th round
]
# Additional audio files
ADDITIONAL_AUDIO = [
    "begin.mp3",
    "stop.mp3",
    "Ten seconds to focus intentions.mp3",
    "end_of_game.mp3"  # Add this line
]

# State machine
STATE_STARTUP = "startup"
STATE_INSTRUCTION = "instruction"
STATE_ATTEMPT = "attempt"
STATE_ATTEMPT_END_WAIT = "attempt_end_wait"  # New state for 2s wait after attempt
STATE_END = "end"

# Motivational prompts for attempt phase
MOTIVATIONAL_PROMPTS = [
    "Focus and Influence the Wheel Now",
    "Channel your energy to spin the wheel!",
    "Harness your intention and make it move!",
    "Visualize the wheel turning!",
    "Let your mind guide the motion!",
    "You have the power—spin it!",
    "Direct your will to the wheel!",
    "Feel the energy flow!",
    "Believe and make it happen!",
    "Your focus is your strength!",
    "Imagine the wheel spinning faster!",
    "Let your thoughts move the wheel!",
    "You are in control—show it!",
    "Push the limits of your mind!",
    "Concentrate and influence the spin!",
    "Your intention is powerful!",
    "See the wheel move in your mind!",
    "Unleash your telekinetic potential!",
    "Stay calm, stay focused, spin the wheel!",
    "Trust your inner force!",
    "Let your mind and the wheel become one!"
]

class EgelyApp:
    def __init__(self):
        pygame.init()
        # Get display size and set window to maximized (with title bar)
        display_info = pygame.display.Info()
        screen_width, screen_height = display_info.current_w, display_info.current_h
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.window_size = self.screen.get_size()
        pygame.display.set_caption("Egely Wheel - Spin Control")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.state = STATE_STARTUP
        self.round = 1
        self.instructions = []
        self.current_instruction = ""
        self.current_image = None
        self.timer = 0
        self.audio = {}
        self.images = []
        self.wheel_bg_img = None  # Static background wheel
        self.arrow_cw_img = None  # Rotating clockwise arrow
        self.arrow_ccw_img = None  # Rotating counterclockwise arrow
        self.blue_arrows_img = None  # Light blue arrows for special round
        self.load_assets()
        # Move Start button lower and label it 'Start'
        self.button_rect = pygame.Rect(0, 0, 220, 60)
        self.button_rect.center = (self.window_size[0] // 2, int(self.window_size[1] * 0.85))
        self.close_button_rect = pygame.Rect(0, 0, 220, 60)
        self.close_button_rect.center = (self.window_size[0] // 2, (self.window_size[1] // 2) + 180)
        self.running = True
        self.button_scale = 1.0
        self.close_button_scale = 1.0
        self.button_anim_speed = 0.08
        self.timer_pulse = 1.0
        self.timer_pulse_dir = 1
        self.timer_pulse_speed = 0.01
        # Add rotation state
        self.rotation_angle = 0
        self.rotation_direction = 1
        # Add direction switch timer
        self.direction_switch_timer = 0
        self.ten_sec_audio_played = False
        self.attempt_end_wait_start = None  # Track when wait after attempt ends
        self.rotation_progress = 0  # Track degrees rotated in current direction
        self.end_audio_played = False

    def load_assets(self):
        # Load images
        for img_file in INSTRUCTION_IMAGES:
            img_path = resource_path(img_file)
            if os.path.exists(img_path):
                print(f"Loaded image: {img_file}")
                img = pygame.image.load(img_path)
                img = pygame.transform.smoothscale(img, INSTRUCTION_IMAGE_SIZE)
                self.images.append(img)
            else:
                print(f"Missing image: {img_file}")
                self.images.append(None)

        # Load special images for clockwise round
        wheel_bg_path = resource_path("black_egely_wheel_only.png")
        if os.path.exists(wheel_bg_path):
            print("Loaded special image: black_egely_wheel_only.png")
            self.wheel_bg_img = pygame.image.load(wheel_bg_path)
            self.wheel_bg_img = pygame.transform.smoothscale(self.wheel_bg_img, WHEEL_SIZE["instruction"])
        else:
            print("Missing special image: black_egely_wheel_only.png")

        # Load clockwise arrow
        arrow_cw_path = resource_path("green_arrow_clockwise.png")
        if os.path.exists(arrow_cw_path):
            print("Loaded special image: green_arrow_clockwise.png")
            self.arrow_cw_img = pygame.image.load(arrow_cw_path)
            self.arrow_cw_img = pygame.transform.smoothscale(self.arrow_cw_img, GREEN_ARROW_SIZE["instruction"])
        else:
            print("Missing special image: green_arrow_clockwise.png")

        # Load counterclockwise arrow
        arrow_ccw_path = resource_path("green_arrow_anticlockwise.png")
        if os.path.exists(arrow_ccw_path):
            print("Loaded special image: green_arrow_anticlockwise.png")
            self.arrow_ccw_img = pygame.image.load(arrow_ccw_path)
            self.arrow_ccw_img = pygame.transform.smoothscale(self.arrow_ccw_img, GREEN_ARROW_SIZE["instruction"])
        else:
            print("Missing special image: green_arrow_anticlockwise.png")

        # Load blue arrows for special rounds
        blue_arrows_path = resource_path("light_blue_arrows_transparent.png")
        if os.path.exists(blue_arrows_path):
            print("Loaded special image: light_blue_arrows_transparent.png")
            self.blue_arrows_img = pygame.image.load(blue_arrows_path)
            self.blue_arrows_img = pygame.transform.smoothscale(self.blue_arrows_img, BLUE_ARROWS_SIZE["instruction"])
        else:
            print("Missing special image: light_blue_arrows_transparent.png")

        # Load audio files for instructions
        for idx, audio_file in enumerate(INSTRUCTION_AUDIO):
            audio_path = resource_path(audio_file)
            if os.path.exists(audio_path):
                self.audio[INSTRUCTIONS[idx]] = pygame.mixer.Sound(audio_path)
            else:
                self.audio[INSTRUCTIONS[idx]] = None

        # Load additional audio files
        for audio_file in ADDITIONAL_AUDIO:
            audio_path = resource_path(audio_file)
            if os.path.exists(audio_path):
                self.audio[audio_file] = pygame.mixer.Sound(audio_path)
            else:
                self.audio[audio_file] = None
                print(f"Missing audio: {audio_file}")

    def reset_game(self):
        self.round = 1
        # Create lists of all possible rounds
        all_instructions = list(INSTRUCTIONS)
        all_images = list(INSTRUCTION_IMAGES)
        all_audio = list(INSTRUCTION_AUDIO)
        
        # Randomly select which round to eliminate (0 to 4)
        eliminated_index = random.randint(0, len(all_instructions) - 1)
        eliminated_round = all_instructions[eliminated_index]
        
        # Remove the eliminated round from all lists
        all_instructions.pop(eliminated_index)
        all_images.pop(eliminated_index)
        all_audio.pop(eliminated_index)
        
        print(f"Eliminated round: {eliminated_round}")  # Debug print to see which round was eliminated
        
        # Load the remaining images
        self.images = []
        for img_file in all_images:
            img_path = resource_path(img_file)
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                img = pygame.transform.smoothscale(img, (400, 400))
                self.images.append(img)
            else:
                self.images.append(None)
        
        # Shuffle the remaining 4 rounds
        zipped = list(zip(all_instructions, self.images, all_audio))
        random.shuffle(zipped)
        self.instructions, self.images, _ = zip(*zipped)
        self.instructions = list(self.instructions)
        self.images = list(self.images)
        
        self.state = STATE_STARTUP
        # Select unique motivational prompts for each round
        self.round_prompts = random.sample(MOTIVATIONAL_PROMPTS, ROUND_TOTAL)
        self.end_audio_played = False

    def draw_text_center(self, text, y_ratio, font=None, color=TEXT_COLOR):
        if font is None:
            font = self.font
        surf = font.render(text, True, color)
        # y_ratio is a float between 0 and 1 (fraction of window height)
        y = int(self.window_size[1] * y_ratio)
        rect = surf.get_rect(center=(self.window_size[0] // 2, y))
        self.screen.blit(surf, rect)

    def draw_button(self, text, hover=False, rect=None, scale=1.0):
        if rect is None:
            rect = self.button_rect
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        # Animate scale
        scaled_rect = rect.copy()
        center = rect.center
        scaled_rect.width = int(rect.width * scale)
        scaled_rect.height = int(rect.height * scale)
        scaled_rect.center = center
        pygame.draw.rect(self.screen, color, scaled_rect, border_radius=12)
        # Center text in button
        surf = self.small_font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = surf.get_rect(center=scaled_rect.center)
        self.screen.blit(surf, text_rect)

    def play_audio(self, audio_key):
        sound = self.audio.get(audio_key)
        if sound:
            sound.stop()
            sound.play()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.window_size = self.screen.get_size()
                # Reposition buttons on resize
                self.button_rect.center = (self.window_size[0] // 2, int(self.window_size[1] * 0.85))
                self.close_button_rect.center = (self.window_size[0] // 2, (self.window_size[1] // 2) + 180)
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_STARTUP and event.key == pygame.K_SPACE:
                    self.start_instruction_phase()
                elif self.state == STATE_INSTRUCTION and event.key == pygame.K_SPACE:
                    if self.timer > 10:
                        self.play_audio(self.current_instruction)
                    else:
                        self.play_audio("Ten seconds to focus intentions.mp3")
                elif self.state == STATE_END:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == STATE_STARTUP and self.button_rect.collidepoint(event.pos):
                    self.start_instruction_phase()
                elif self.state == STATE_END:
                    if self.button_rect.collidepoint(event.pos):
                        self.reset_game()
                    elif self.close_button_rect.collidepoint(event.pos):
                        self.running = False

    def start_instruction_phase(self):
        idx = self.round - 1
        self.current_instruction = self.instructions[idx]
        self.current_image = self.images[idx]
        self.timer = 20
        self.state = STATE_INSTRUCTION
        self.play_audio(self.current_instruction)
        self.ten_sec_audio_played = False  # Reset the flag at the start of each instruction phase

    def start_attempt_phase(self):
        self.timer = 12
        self.state = STATE_ATTEMPT
        # Play begin.mp3 at the start of the attempt phase
        self.play_audio("begin.mp3")
        # Set rotation direction and speed based on instruction
        instr = self.current_instruction.strip().lower()
        
        if "clockwise" in instr and "counter" not in instr:
            # This is the Spin Clockwise round
            self.rotation_direction = 1  # Clockwise
            self.direction_switch_timer = 0
            self.rotation_speed = 1  # 60 deg/sec
            self.rotation_progress = 0
        elif instr == "spin counter clockwise":
            # Counter Clockwise round
            self.rotation_direction = -1  # Counter-clockwise
            self.direction_switch_timer = 0
            self.rotation_speed = 1  # 60 deg/sec
            self.rotation_progress = 0
        elif "clockwise or counter clockwise" in instr:
            self.rotation_direction = 1  # Start with clockwise
            self.direction_switch_timer = 4  # 4 seconds per direction
            self.rotation_speed = 1  # 60 deg/sec
            self.rotation_progress = 0
            # Use the blue arrows image for this round
            self.current_image = self.blue_arrows_img
        elif instr == "spin clockwise then counter clockwise":
            self.rotation_direction = 1  # Start with clockwise
            self.rotation_speed = 1  # 60 deg/sec
            self.rotation_progress = 0
            # Use the special blue arrows image
            idx = self.instructions.index(self.current_instruction)
            self.current_image = self.images[idx]
        elif "spin fast in either direction" in instr:
            self.rotation_direction = random.choice([-1, 1])
            self.direction_switch_timer = 0
            self.rotation_speed = 2.5  # 150 deg/sec
            self.rotation_progress = 0
            # Use the blue arrows image for this round
            self.current_image = self.blue_arrows_img
        else:
            self.rotation_direction = random.choice([-1, 1])
            self.direction_switch_timer = 0
            self.rotation_speed = 1  # 60 deg/sec
            self.rotation_progress = 0
            idx = self.instructions.index(self.current_instruction)
            self.current_image = self.images[idx]
        self.rotation_angle = 0

    def update(self):
        # Animate button scale for hover effect
        mouse_pos = pygame.mouse.get_pos()
        # Start/Restart button
        if self.state in [STATE_STARTUP, STATE_END]:
            hover = self.button_rect.collidepoint(mouse_pos)
            target_scale = 1.08 if hover else 1.0
            self.button_scale += (target_scale - self.button_scale) * self.button_anim_speed
            # Close button (only on end screen)
            if self.state == STATE_END:
                close_hover = self.close_button_rect.collidepoint(mouse_pos)
                close_target_scale = 1.08 if close_hover else 1.0
                self.close_button_scale += (close_target_scale - self.close_button_scale) * self.button_anim_speed
        # Timer pulse animation
        if self.state in [STATE_INSTRUCTION, STATE_ATTEMPT]:
            self.timer_pulse += self.timer_pulse_dir * self.timer_pulse_speed
            if self.timer_pulse > 1.08:
                self.timer_pulse = 1.08
                self.timer_pulse_dir = -1
            elif self.timer_pulse < 0.92:
                self.timer_pulse = 0.92
                self.timer_pulse_dir = 1
        else:
            self.timer_pulse = 1.0
            self.timer_pulse_dir = 1
        if self.state in [STATE_INSTRUCTION, STATE_ATTEMPT]:
            if self.timer > 0:
                prev_timer = self.timer
                self.timer -= 1 / FPS
                # Play 'Ten seconds to focus intentions.mp3' at 10s left in instruction phase
                if (
                    self.state == STATE_INSTRUCTION
                    and not self.ten_sec_audio_played
                    and int(self.timer + 1/FPS) == 10  # More precise timing check
                ):
                    print("Playing 10 second warning audio")  # Debug print
                    ten_sec_audio = self.audio.get("Ten seconds to focus intentions.mp3")
                    if ten_sec_audio:
                        ten_sec_audio.stop()  # Stop any previous playback
                        ten_sec_audio.play()
                        print("10 second warning audio played")  # Debug print
                    else:
                        print("10 second warning audio not found")  # Debug print
                    self.ten_sec_audio_played = True
                # Play stop.mp3 and switch to wait state when timer reaches 0 in attempt phase
                if self.state == STATE_ATTEMPT and prev_timer > 0 and self.timer <= 0:
                    print("Playing stop audio")  # Debug print
                    self.play_audio("stop.mp3")
                    self.attempt_end_wait_start = pygame.time.get_ticks()
                    self.state = STATE_ATTEMPT_END_WAIT
            else:
                if self.state == STATE_INSTRUCTION:
                    self.start_attempt_phase()
                    self.ten_sec_audio_played = False  # Reset for next round
        elif self.state == STATE_ATTEMPT_END_WAIT:
            # Wait for 2 seconds before proceeding
            if self.attempt_end_wait_start is not None:
                elapsed = pygame.time.get_ticks() - self.attempt_end_wait_start
                if elapsed >= 2000:
                    if self.round < ROUND_TOTAL:
                        self.round += 1
                        self.state = STATE_INSTRUCTION
                        self.timer = 20
                        idx = self.round - 1
                        self.current_instruction = self.instructions[idx]
                        self.current_image = self.images[idx]
                        self.play_audio(self.current_instruction)
                    else:
                        self.state = STATE_END
                        if not self.end_audio_played:
                            self.play_audio("end_of_game.mp3")
                            self.end_audio_played = True
                    self.attempt_end_wait_start = None
        # Image rotation during ATTEMPT
        if self.state == STATE_ATTEMPT and self.current_image:
            if self.current_instruction.strip().lower() == "spin clockwise then counter clockwise":
                # Rotate one full turn, then switch direction
                step = self.rotation_direction * self.rotation_speed
                self.rotation_angle += step
                self.rotation_angle %= 360
                self.rotation_progress += abs(step)
                if self.rotation_progress >= 360:
                    self.rotation_direction *= -1
                    self.rotation_progress = 0
            else:
                # Alternate direction for 'Spin Clockwise or Counter Clockwise'
                if "Clockwise or Counter Clockwise" in self.current_instruction:
                    self.direction_switch_timer -= 1 / FPS
                    if self.direction_switch_timer <= 0:
                        self.rotation_direction *= -1
                        self.direction_switch_timer = 4
                self.rotation_angle += self.rotation_direction * self.rotation_speed  # degrees per frame
                self.rotation_angle %= 360

    def render(self):
        self.screen.fill(BG_COLOR)
        w, h = self.window_size
        if self.state == STATE_STARTUP:
            self.draw_text_center("Hello Perceptualist, welcome to the Telekinesis challenge we call Spin Control...", 0.2)
            mouse_pos = pygame.mouse.get_pos()
            hover = self.button_rect.collidepoint(mouse_pos)
            # Center image
            # If first round uses wheel and arrows, show both
            if self.instructions and self.instructions[0].strip().lower() in ["spin clockwise then counter clockwise", "spin fast in either direction", "spin clockwise or counter clockwise"]:
                if self.wheel_bg_img:
                    startup_wheel = pygame.transform.smoothscale(self.wheel_bg_img, WHEEL_SIZE["startup"])
                    img_rect = startup_wheel.get_rect(center=(w // 2, int(h * 0.45)))
                    self.screen.blit(startup_wheel, img_rect)
                if self.blue_arrows_img:
                    startup_arrows = pygame.transform.smoothscale(self.blue_arrows_img, BLUE_ARROWS_SIZE["startup"])
                    arrows_rect = startup_arrows.get_rect(center=(w // 2, int(h * 0.45)))
                    self.screen.blit(startup_arrows, arrows_rect)
            elif self.images and self.images[0]:
                img_rect = self.images[0].get_rect(center=(w // 2, int(h * 0.45)))
                self.screen.blit(self.images[0], img_rect)
            # Move button lower
            self.button_rect.center = (w // 2, int(h * 0.85))
            self.draw_button("Start", hover, self.button_rect, self.button_scale)
        elif self.state == STATE_INSTRUCTION:
            self.draw_text_center(f"Round {self.round} of {ROUND_TOTAL}", 0.13, self.small_font)
            self.draw_text_center(self.current_instruction, 0.33)
            # Timer with pulse animation
            timer_font = pygame.font.SysFont("Arial", int(36 * self.timer_pulse))
            self.draw_text_center(f"{int(self.timer):02d}s", 0.45, timer_font, TIMER_COLOR)
            # If this round uses wheel and arrows, show both
            if self.current_instruction.strip().lower() in ["spin clockwise then counter clockwise", "spin fast in either direction", "spin clockwise or counter clockwise"]:
                if self.wheel_bg_img:
                    instruction_wheel = pygame.transform.smoothscale(self.wheel_bg_img, WHEEL_SIZE["instruction"])
                    img_rect = instruction_wheel.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(instruction_wheel, img_rect)
                if self.blue_arrows_img:
                    instruction_arrows = pygame.transform.smoothscale(self.blue_arrows_img, BLUE_ARROWS_SIZE["instruction"])
                    arrows_rect = instruction_arrows.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(instruction_arrows, arrows_rect)
            elif self.current_image:
                img_rect = self.current_image.get_rect(center=(w // 2, int(h * 0.7)))
                self.screen.blit(self.current_image, img_rect)
            self.draw_text_center("Press SPACE to replay instruction", 0.92, self.small_font, (120, 120, 120))
        elif self.state == STATE_ATTEMPT:
            self.draw_text_center(f"Round {self.round} of {ROUND_TOTAL}", 0.13, self.small_font)
            prompt = self.round_prompts[self.round - 1]
            self.draw_text_center(prompt, 0.33)
            mins, secs = divmod(int(self.timer), 60)
            timer_font = pygame.font.SysFont("Arial", int(36 * self.timer_pulse))
            self.draw_text_center(f"{mins:02d}:{secs:02d}", 0.45, timer_font, TIMER_COLOR)

            # Special handling for Spin Clockwise round
            if self.current_instruction.strip().lower() == "spin clockwise":
                # Draw static wheel background
                if self.wheel_bg_img:
                    attempt_wheel = pygame.transform.smoothscale(self.wheel_bg_img, WHEEL_SIZE["attempt"])
                    bg_rect = attempt_wheel.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(attempt_wheel, bg_rect)
                # Draw rotating arrow on top
                if self.arrow_cw_img:
                    attempt_arrow = pygame.transform.smoothscale(self.arrow_cw_img, GREEN_ARROW_SIZE["attempt"])
                    rotated_arrow = pygame.transform.rotate(attempt_arrow, -self.rotation_angle)
                    arrow_rect = rotated_arrow.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(rotated_arrow, arrow_rect)
            # Special handling for Spin Clockwise then Counter Clockwise round and Fast in Either Direction
            elif self.current_instruction.strip().lower() in ["spin clockwise then counter clockwise", "spin fast in either direction", "spin clockwise or counter clockwise"]:
                # Draw static wheel background
                if self.wheel_bg_img:
                    attempt_wheel = pygame.transform.smoothscale(self.wheel_bg_img, WHEEL_SIZE["attempt"])
                    bg_rect = attempt_wheel.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(attempt_wheel, bg_rect)
                # Draw rotating arrow on top
                if self.current_image:
                    scaled_arrow = pygame.transform.smoothscale(self.current_image, BLUE_ARROWS_SIZE["attempt"])
                    rotated_arrow = pygame.transform.rotate(scaled_arrow, -self.rotation_angle)
                    arrow_rect = rotated_arrow.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(rotated_arrow, arrow_rect)
            # Special handling for Spin Counter Clockwise round
            elif self.current_instruction.strip().lower() == "spin counter clockwise":
                # Draw static wheel background
                if self.wheel_bg_img:
                    bg_rect = self.wheel_bg_img.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(self.wheel_bg_img, bg_rect)
                # Draw rotating arrow on top
                if self.arrow_ccw_img:
                    rotated_arrow = pygame.transform.rotate(self.arrow_ccw_img, -self.rotation_angle)
                    arrow_rect = rotated_arrow.get_rect(center=(w // 2, int(h * 0.7)))
                    self.screen.blit(rotated_arrow, arrow_rect)
            elif self.current_image:
                # Regular image handling for other rounds
                rotated_img = pygame.transform.rotate(self.current_image, -self.rotation_angle)
                img_rect = rotated_img.get_rect(center=(w // 2, int(h * 0.7)))
                self.screen.blit(rotated_img, img_rect)
            elif self.current_instruction == "Spin Fast in Either Direction":
                print("DEBUG: self.current_image is None for 'Spin Fast in Either Direction'")
                # Draw a placeholder circle
                placeholder_rect = pygame.Rect(0, 0, 300, 300)  # Increased from 200x200
                placeholder_rect.center = (w // 2, int(h * 0.7))
                pygame.draw.ellipse(self.screen, (200, 200, 200), placeholder_rect)
                self.draw_text_center("[No Image]", 0.7, self.small_font, (180, 0, 0))
        elif self.state == STATE_END:
            self.draw_text_center("Well done, Perceptualist. Challenge Complete.", 0.33)
            mouse_pos = pygame.mouse.get_pos()
            hover = self.button_rect.collidepoint(mouse_pos)
            close_hover = self.close_button_rect.collidepoint(mouse_pos)
            # Move buttons lower
            self.button_rect.center = (w // 2, int(h * 0.7))
            self.close_button_rect.center = (w // 2, int(h * 0.8))
            self.draw_button("Restart", hover, self.button_rect, self.button_scale)
            self.draw_button("Close", close_hover, self.close_button_rect, self.close_button_scale)
        pygame.display.flip()

    def run_once(self):
        self.handle_events()
        self.update()
        self.render()
        self.clock.tick(FPS)

async def main():
    app = EgelyApp()
    app.reset_game()
    while app.running:
        app.run_once()
        await asyncio.sleep(0)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())