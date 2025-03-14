import math
from fractions import Fraction

import pygame


class Block2D:
    def __init__(self, mass, v, x, size=30):
        self.mass = Fraction(mass).limit_denominator(10**9)
        self.v = Fraction(v).limit_denominator(10**9)
        self.x = Fraction(x).limit_denominator(10**9)
        self.size = Fraction(size).limit_denominator(10**9)

    def __repr__(self):
        return f"Block(mass={self.mass}, v={self.v})"

    def simplify(self, max_denominator=10**9):
        """Simplify fractions to improve performance"""
        self.v = self.v.limit_denominator(max_denominator)
        self.x = self.x.limit_denominator(max_denominator)
        return self


class Simulation:
    def __init__(self, width):
        self.width = width

        # Allow for different masses for experimentation
        self.block_0 = Block2D(1, 0, 150)  # Block with mass_0, initially stationary
        self.block_1 = Block2D(10000, -5, 600, 60)  # Block with mass_1, moving left

        # Collision counters
        self.wall_collisions = 0
        self.block_collisions = 0
        self.total_collisions = 0

        # Simulation parameters
        self.time_step = Fraction(1, 100).limit_denominator(10**9)
        self.simulation_speed = 2**8  # Steps per frame

        # Performance optimization parameters
        self.simplify_interval = 100  # How often to simplify fractions
        self.simplify_counter = 0
        self.simplify_denominator = 10**9  # Maximum denominator to allow

        # Calculated values
        self.total_energy = self._total_energy()
        self.total_momentum = self._total_momentum()

        # Store initial values for verification
        self.initial_energy = self.total_energy
        self.initial_momentum = self.total_momentum

        # For pausing simulation
        self.paused = False

    def _total_energy(self):
        """Calculate total kinetic energy"""
        return (
            self.block_0.mass * self.block_0.v**2 / 2
            + self.block_1.mass * self.block_1.v**2 / 2
        ).limit_denominator(10**9)

    def _total_momentum(self):
        """Calculate total momentum"""
        return (
            self.block_0.mass * self.block_0.v + self.block_1.mass * self.block_1.v
        ).limit_denominator(10**9)

    @property
    def mass_ratio(self):
        """Calculate the ratio of masses (m2/m1)"""
        return self.block_1.mass / self.block_0.mass

    @property
    def pi_approximation(self):
        """Calculate π approximation based on collision count and mass ratio"""
        return self.total_collisions / math.sqrt(float(self.mass_ratio))

    def simplify_fractions(self):
        """Periodically simplify fractions to improve performance"""
        self.block_0.simplify(self.simplify_denominator)
        self.block_1.simplify(self.simplify_denominator)
        self.time_step = self.time_step.limit_denominator(self.simplify_denominator)

    def detect_collisions(self):
        """Detect if any collisions are occurring right now"""
        # Check if block_0 is at the wall
        if self.block_0.x <= self.block_0.size / 2 and self.block_0.v < 0:
            return "wall_0"

        # Check if block_1 is at the wall
        if self.block_1.x <= self.block_1.size / 2 and self.block_1.v < 0:
            return "wall_1"

        # Check if blocks are touching and moving toward each other
        min_distance = (self.block_0.size + self.block_1.size) / 2
        actual_distance = self.block_1.x - self.block_0.x

        if actual_distance <= min_distance and self.block_0.v > self.block_1.v:
            return "blocks"

        return None

    def handle_collision(self, collision_type):
        """Handle a collision that is occurring now"""
        if collision_type == "wall_0":
            # Block 0 hits wall - reverse velocity
            self.block_0.v = -self.block_0.v
            # Fix position to be exactly at wall
            self.block_0.x = self.block_0.size / 2
            self.wall_collisions += 1
            self.total_collisions += 1

        elif collision_type == "wall_1":
            # Block 1 hits wall - reverse velocity
            self.block_1.v = -self.block_1.v
            # Fix position to be exactly at wall
            self.block_1.x = self.block_1.size / 2
            self.wall_collisions += 1
            self.total_collisions += 1

        elif collision_type == "blocks":
            # Elastic collision between blocks
            m1, m2 = self.block_0.mass, self.block_1.mass
            v1, v2 = self.block_0.v, self.block_1.v

            # Calculate new velocities and immediately limit denominator
            new_v1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            new_v2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

            self.block_0.v = new_v1.limit_denominator(self.simplify_denominator)
            self.block_1.v = new_v2.limit_denominator(self.simplify_denominator)

            # Ensure blocks are not overlapping
            min_distance = (self.block_0.size + self.block_1.size) / 2
            actual_distance = self.block_1.x - self.block_0.x

            # If there's overlap, adjust positions
            if actual_distance < min_distance:
                overlap = min_distance - actual_distance
                # Move blocks apart proportionally to their masses
                total_mass = m1 + m2

                # Limit denominators immediately for position adjustments
                pos_adj1 = ((overlap * m2) / total_mass).limit_denominator(
                    self.simplify_denominator
                )
                pos_adj2 = ((overlap * m1) / total_mass).limit_denominator(
                    self.simplify_denominator
                )

                self.block_0.x -= pos_adj1
                self.block_1.x += pos_adj2

            self.block_collisions += 1
            self.total_collisions += 1

        # After any collision, update energy and momentum
        self.total_energy = self._total_energy()
        self.total_momentum = self._total_momentum()

    def update(self):
        """Update the simulation one step"""
        if self.paused:
            return

        # First check for and handle any current collisions
        collision_type = self.detect_collisions()
        if collision_type:
            self.handle_collision(collision_type)
            return

        # If no immediate collision, move blocks forward
        self.block_0.x += self.block_0.v * self.time_step
        self.block_1.x += self.block_1.v * self.time_step

        # Check again for collisions after moving
        collision_type = self.detect_collisions()
        if collision_type:
            self.handle_collision(collision_type)

        # Periodically simplify fractions to prevent slowdown
        self.simplify_counter += 1
        if self.simplify_counter >= self.simplify_interval:
            self.simplify_fractions()
            self.simplify_counter = 0

    def reset(self, mass_0=1, mass_1=10000, v_1=-5):
        """Reset the simulation with new parameters"""
        self.block_0 = Block2D(mass_0, 0, 150)
        self.block_1 = Block2D(mass_1, v_1, 600, 60)

        self.wall_collisions = 0
        self.block_collisions = 0
        self.total_collisions = 0
        self.simplify_counter = 0

        self.total_energy = self._total_energy()
        self.total_momentum = self._total_momentum()
        self.initial_energy = self.total_energy
        self.initial_momentum = self.total_momentum

    def adjust_speed(self, increase=True):
        """Increase or decrease simulation speed"""
        if increase:
            self.simulation_speed = min(100000, self.simulation_speed * 2)
        else:
            self.simulation_speed = max(1, self.simulation_speed // 2)

    def adjust_precision(self, increase=True):
        """Adjust the precision of fraction simplification"""
        if increase:
            self.simplify_denominator = min(10**12, self.simplify_denominator * 10)
        else:
            self.simplify_denominator = max(10**3, self.simplify_denominator // 10)
        # Apply immediately
        self.simplify_fractions()


# Increased window size for better readability
HEIGHT = 800
WIDTH = 1200

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pi Calculation by Collisions (Optimized)")
clock = pygame.time.Clock()

# Colors
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
white = (255, 255, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)
cyan = (0, 255, 255)


def render(sim):
    # Draw background
    screen.fill(black)

    # Draw the ground
    ground_y = HEIGHT - 150
    pygame.draw.line(screen, grey, (0, ground_y), (WIDTH, ground_y), 3)

    # Draw the wall
    pygame.draw.line(screen, grey, (0, ground_y), (0, 0), 3)

    # Draw block_0 (red)
    block_0_rect = pygame.Rect(
        float(sim.block_0.x - sim.block_0.size / 2),
        ground_y - float(sim.block_0.size),
        float(sim.block_0.size),
        float(sim.block_0.size),
    )
    pygame.draw.rect(screen, red, block_0_rect)

    # Label for block_0
    small_font = pygame.font.SysFont(None, 20)
    block0_label = small_font.render(f"m1={float(sim.block_0.mass)}", True, white)
    screen.blit(
        block0_label,
        (
            float(sim.block_0.x - sim.block_0.size / 2),
            ground_y - float(sim.block_0.size) - 20,
        ),
    )

    # Draw block_1 (blue)
    block_1_rect = pygame.Rect(
        float(sim.block_1.x - sim.block_1.size / 2),
        ground_y - float(sim.block_1.size),
        float(sim.block_1.size),
        float(sim.block_1.size),
    )
    pygame.draw.rect(screen, blue, block_1_rect)

    # Label for block_1
    block1_label = small_font.render(f"m2={float(sim.block_1.mass)}", True, white)
    screen.blit(
        block1_label,
        (
            float(sim.block_1.x - sim.block_1.size / 2),
            ground_y - float(sim.block_1.size) - 20,
        ),
    )

    # Display collision counts and other info
    font = pygame.font.SysFont(None, 28)  # Larger font
    title_font = pygame.font.SysFont(None, 36)  # Even larger font for titles

    # Calculate pi approximation accounting for both masses
    pi_approx = sim.pi_approximation

    # Calculate energy and momentum conservation errors
    energy_diff = float(abs(sim.total_energy - sim.initial_energy))
    momentum_diff = float(abs(sim.total_momentum - sim.initial_momentum))

    # Draw title
    title = title_font.render("Pi Calculation through Elastic Collisions", True, yellow)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Draw simulation controls
    controls = [
        "Controls:",
        "SPACE: Pause/Resume",
        "R: Reset simulation",
        "1/2: Decrease/Increase m1",
        "3/4: Decrease/Increase m2",
        "+/-: Adjust simulation speed",
        "[/]: Adjust fraction precision",
    ]

    # Draw controls on the right side
    for i, text in enumerate(controls):
        rendered_text = font.render(text, True, green)
        screen.blit(rendered_text, (WIDTH - 300, 70 + i * 30))

    # Draw simulation data on the left side
    data_texts = [
        f"Collisions: {sim.total_collisions}",
        f"Wall: {sim.wall_collisions}, Block: {sim.block_collisions}",
        f"Mass Ratio (m2/m1): {float(sim.mass_ratio):.1f}",
        f"√(m2/m1): {math.sqrt(float(sim.mass_ratio)):.2f}",
        "",
        f"π Approximation: {pi_approx:.8f}",
        f"True π: {math.pi:.8f}",
        f"Error: {100 * abs(pi_approx - math.pi) / math.pi:.8f}%",
        "",
        f"Block 0: m={float(sim.block_0.mass)}, v={float(sim.block_0.v):.2f}",
        f"Block 1: m={float(sim.block_1.mass)}, v={float(sim.block_1.v):.2f}",
        "",
        f"Energy Conservation Error: {energy_diff:.15f}",
        f"Momentum Conservation Error: {momentum_diff:.15f}",
        "",
        f"{'PAUSED' if sim.paused else 'Running'} - Speed: {sim.simulation_speed} steps/frame",
        f"Fraction Precision: {sim.simplify_denominator}",
    ]

    for i, text in enumerate(data_texts):
        rendered_text = font.render(text, True, white)
        screen.blit(rendered_text, (30, 70 + i * 30))

    # Draw a performance indicator (cyan indicates simplification occurring)
    if sim.simplify_counter == 0:
        pygame.draw.circle(screen, cyan, (WIDTH - 20, 20), 10)

    pygame.display.update()


sim = Simulation(WIDTH)

# Track FPS
fps_timer = 0
frames = 0

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sim.paused = not sim.paused
            elif event.key == pygame.K_r:
                # Reset with current mass values
                sim.reset(
                    mass_0=float(sim.block_0.mass), mass_1=float(sim.block_1.mass)
                )
            elif event.key == pygame.K_1 and not sim.paused:
                # Decrease block 0 mass
                new_mass = max(1, float(sim.block_0.mass) / 10)
                sim.reset(mass_0=new_mass, mass_1=float(sim.block_1.mass))
            elif event.key == pygame.K_2 and not sim.paused:
                # Increase block 0 mass
                new_mass = float(sim.block_0.mass) * 10
                sim.reset(mass_0=new_mass, mass_1=float(sim.block_1.mass))
            elif event.key == pygame.K_3 and not sim.paused:
                # Decrease block 1 mass
                new_mass = max(1, float(sim.block_1.mass) / 10)
                sim.reset(mass_0=float(sim.block_0.mass), mass_1=new_mass)
            elif event.key == pygame.K_4 and not sim.paused:
                # Increase block 1 mass
                new_mass = float(sim.block_1.mass) * 10
                sim.reset(mass_0=float(sim.block_0.mass), mass_1=new_mass)
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                # Increase simulation speed
                sim.adjust_speed(increase=True)
            elif event.key == pygame.K_MINUS:
                # Decrease simulation speed
                sim.adjust_speed(increase=False)
            elif event.key == pygame.K_LEFTBRACKET:
                # Decrease fraction precision (faster but less accurate)
                sim.adjust_precision(increase=False)
            elif event.key == pygame.K_RIGHTBRACKET:
                # Increase fraction precision (slower but more accurate)
                sim.adjust_precision(increase=True)

    # Run multiple simulation steps per frame based on simulation speed
    for _ in range(sim.simulation_speed):
        sim.update()

    render(sim)

    # Track and display FPS if enabled
    frames += 1
    fps_timer += clock.get_time()
    if fps_timer >= 1000:  # Every second
        fps_timer = 0
        frames = 0

    clock.tick(60)

pygame.quit()
