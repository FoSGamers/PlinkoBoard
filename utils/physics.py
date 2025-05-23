import random

class PlinkoPhysics:
    """
    Simulates realistic Plinko chip physics:
    - Each peg hit causes a strong deflection (left/right) and an upward bounce.
    - The chip's fall time is randomized (3-10 seconds) based on bounces and peg hits.
    - Spin and angle bias add human-like unpredictability.
    - Chip is always clamped within board bounds and nudged toward center if near edge.
    """
    def __init__(self, pegs, peg_positions, board_height, board_width=None):
        self.pegs = pegs
        self.peg_positions = peg_positions
        self.board_height = board_height
        self.board_width = board_width or 720  # Default width if not provided
        self.reset()

    def reset(self):
        self.vy = 0
        self.target_steps = random.randint(180, 600)  # 3-10 seconds at 60 FPS
        # Gravity is set so that sum(gravity * n for n in 1..target_steps) ~= board_height
        # Use formula for sum of arithmetic series: S = n/2 * (first + last)
        # Approximate: gravity * (target_steps^2 / 2) = board_height
        gravity = (2 * self.board_height) / (self.target_steps ** 2)
        self.gravity = min(max(gravity, 0.15), 1.5)  # Cap gravity between 0.15 and 1.5
        self.bounce_energy = random.uniform(0.5, 1.2)  # Higher up-bounce energy
        self.spin = random.uniform(-2, 2)
        self.angle_bias = random.uniform(-3, 3)
        self.last_hit_row = -1

    def next_bounce(self, chip_x, chip_y, chip_d, step, max_steps):
        # Returns (new_x, new_y, hit_peg, vy)
        hit_peg = False
        up_bounce = 0
        for idx, (px, py, pr) in enumerate(self.peg_positions):
            dist = ((chip_x + chip_d/2 - px)**2 + (chip_y + chip_d/2 - py)**2)**0.5
            if dist < pr + chip_d/2:
                # Only bounce if not the same row as last hit (prevents multi-bounce on same peg)
                row = int(py // (self.board_height / 12))
                if row != self.last_hit_row:
                    direction = random.choice([-1, 1])
                    bias = self.angle_bias + self.spin * random.uniform(-0.5, 0.5)
                    dx = direction * random.uniform(18, 32) + bias
                    chip_x += dx
                    # Clamp chip_x within board bounds after bounce
                    chip_x = max(0, min(chip_x, self.board_width - chip_d))
                    # Nudge toward center if near edge
                    if chip_x < chip_d:
                        chip_x += chip_d * 0.5
                    elif chip_x > self.board_width - 2 * chip_d:
                        chip_x -= chip_d * 0.5
                    # Strong up bounce, energy decays with each hit
                    up_bounce = -random.uniform(18, 40) * self.bounce_energy
                    self.vy = up_bounce
                    self.last_hit_row = row
                    hit_peg = True
                    break
        # Gravity always pulls down
        self.vy += self.gravity
        chip_y += self.vy
        # Clamp chip_x within board bounds after gravity
        chip_x = max(0, min(chip_x, self.board_width - chip_d))
        # Nudge toward center if near edge
        if chip_x < chip_d:
            chip_x += chip_d * 0.5
        elif chip_x > self.board_width - 2 * chip_d:
            chip_x -= chip_d * 0.5
        # Slow down as chip nears the bottom (simulate air resistance)
        if step > max_steps * 0.7:
            self.vy *= 0.98
        return chip_x, chip_y, hit_peg, self.vy 