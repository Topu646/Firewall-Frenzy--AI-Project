import pygame
import sys
import random

# Initialize Pygame
pygame.init()


# Initialize buttons

# Add a variable to store the start time
game_start_time = 0
# Initialize constants
HIGHLIGHT_DURATION = 3000  # Duration in milliseconds to highlight goal, player, and AI
power_up_message = None
power_up_message_time = 0
POWER_UP_DISPLAY_DURATION = 3000  # Duration in milliseconds to display power-up message

trap_revealed = False


# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 12
CELL_SIZE = 45
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 300
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE


FPS = 60
DELAY = 100  # Delay in milliseconds between turns
MAX_DEPTH = 8  # Depth for the minimax algorithm
NUM_OBSTACLES = 35  # Number of obstacles for both player and AI


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)
DARK_GRAY = (105, 105, 105)
LIGHT_GRAY = (211, 211, 211)

# Constants for traps
NUM_TRAPS = 10
FREEZE_DURATION = 2  # Number of moves the player or AI is frozen

# Variables for traps
freeze_traps = []
random_move_traps = []
player_freeze_moves = 0
ai_freeze_moves = 0
trap_message = None
trap_message_time = 0
TRAP_DISPLAY_DURATION = 2000  # Duration in milliseconds to display trap message


# Add these variables for button positions and sizes
button_width = 150
button_height = 50
button_padding = 10
button_y_position = WINDOW_HEIGHT + button_height

buttons = [
    {"text": "New Game", "rect": pygame.Rect(button_padding, button_y_position, button_width, button_height)},
    {"text": "Restart", "rect": pygame.Rect(2 * button_padding + button_width, button_y_position, button_width, button_height)},
    {"text": "Exit", "rect": pygame.Rect(3 * button_padding + 2 * button_width, button_y_position, button_width, button_height)}
]

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH  , WINDOW_HEIGHT + 100))
pygame.display.set_caption('Firewall Frenzy')

# Font for displaying text
font = pygame.font.Font(None, 36)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Initialize positions and scores
player_score = 0
ai_score = 0

UI_BACKGROUND_COLOR = (41, 61, 61)  # Dark gray background for the UI

# Load images
player_image = pygame.image.load('img/player.png').convert_alpha()
player_image = pygame.transform.scale(player_image, (CELL_SIZE, CELL_SIZE))
ai_image = pygame.image.load('img/hacker.png').convert_alpha()
ai_image = pygame.transform.scale(ai_image, (CELL_SIZE, CELL_SIZE))
goal_image = pygame.image.load('img/computer.png').convert_alpha()
goal_image = pygame.transform.scale(goal_image, (CELL_SIZE, CELL_SIZE))

# Load images for obstacles
player_obstacle_image = pygame.image.load('img/wallblue.png').convert_alpha()
player_obstacle_image = pygame.transform.scale(player_obstacle_image, (CELL_SIZE, CELL_SIZE))
ai_obstacle_image = pygame.image.load('img/wallred.png').convert_alpha()
ai_obstacle_image = pygame.transform.scale(ai_obstacle_image, (CELL_SIZE, CELL_SIZE))

NUM_POWERUPS = 10
SHIELD_DURATION = 250  # Duration for the shield power-up
TRAP_REVEAL_DURATION = 1000  # Duration for the trap reveal power-up
PENETRATE_DURATION = 250  # Duration for the penetrate power-up

# Variables for power-ups
power_ups = []
player_shield = 0
ai_shield = 0
player_trap_reveal = 0
ai_trap_reveal = 0
player_penetrate = 0
ai_penetrate = 0

# Load trap images
trap_image = pygame.image.load('img/spring.png').convert_alpha()
trap_image = pygame.transform.scale(trap_image, (CELL_SIZE, CELL_SIZE))

freeze_image = pygame.image.load('img/freezing.png').convert_alpha()
freeze_image = pygame.transform.scale(freeze_image, (CELL_SIZE, CELL_SIZE))


# Load power-up images
shield_image = pygame.image.load('img/sheild.png').convert_alpha()
shield_image = pygame.transform.scale(shield_image, (CELL_SIZE, CELL_SIZE))
trap_reveal_image = pygame.image.load('img/eye.png').convert_alpha()
trap_reveal_image = pygame.transform.scale(trap_reveal_image, (CELL_SIZE, CELL_SIZE))
penetrate_image = pygame.image.load('img/wall_penetrate.png').convert_alpha()
penetrate_image = pygame.transform.scale(penetrate_image, (CELL_SIZE, CELL_SIZE))


font2 = pygame.font.Font(None, 25)
small_font = pygame.font.Font(None, 20)  # Smaller font for descriptions

def draw_button_window():
    for button in buttons:
        pygame.draw.rect(screen, (41, 61, 61), button["rect"])
        pygame.draw.rect(screen, BLACK, button["rect"], 2)  # Border color

        text_surface = font.render(button["text"], True, WHITE)
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)

# Add event handling for button clicks
def handle_button_clicks():
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0]:  # Left mouse button clicked
        for button in buttons:
            if button["rect"].collidepoint(mouse_pos):
                if button["text"] == "New Game":
                    start_new_game()
                elif button["text"] == "Restart":
                    restart_game()
                elif button["text"] == "Exit":
                    pygame.quit()
                    sys.exit()

# Function to start a new game (reset everything)
def start_new_game():
    global player_position, ai_position, traps, power_ups, player_score, ai_score, player_shield, ai_shield, player_reveal, ai_reveal, player_penetrate, ai_penetrate
    initialize_positions()
    player_score = 0
    ai_score = 0
    player_shield = 0
    ai_shield = 0
    player_reveal = 0
    ai_reveal = 0
    player_penetrate = 0
    ai_penetrate = 0

# Function to restart the game (keep scores)
def restart_game():
    global player_position, ai_position, traps, power_ups, player_shield, ai_shield, player_reveal, ai_reveal, player_penetrate, ai_penetrate
    initialize_positions()
    player_shield = 0
    ai_shield = 0
    player_reveal = 0
    ai_reveal = 0
    player_penetrate = 0
    ai_penetrate = 0

def generate_power_ups(occupied_positions):
    global power_ups
    power_ups = []
    while len(power_ups) < NUM_POWERUPS:
        power_up_type = random.choice(["shield", "trap_reveal", "penetrate"])
        power_up = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), power_up_type]
        if not is_occupied(power_up[:2], occupied_positions):
            power_ups.append(power_up)
            occupied_positions.add(tuple(power_up[:2]))
    return power_ups


def handle_enter_key():
    initialize_positions()


# Initialize positions and traps
def initialize_positions():
    global player_pos, ai_pos, goal_pos, player_turn, game_over, winner, last_move_time
    global player_obstacles, ai_obstacles, ai_path, predicted_ai_path
    global freeze_traps, random_move_traps, player_freeze_moves, ai_freeze_moves
    global power_ups, player_shield, ai_shield, player_trap_reveal, ai_trap_reveal
    global player_penetrate, ai_penetrate,game_start_time

    occupied_positions = set()

    player_pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
    occupied_positions.add(tuple(player_pos))

    ai_pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
    occupied_positions.add(tuple(ai_pos))

    # Ensure the goal position is at least 10 cells away from both player and AI
    while True:
        goal_pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        if (abs(goal_pos[0] - player_pos[0]) + abs(goal_pos[1] - player_pos[1]) >= 10 and
            abs(goal_pos[0] - ai_pos[0]) + abs(goal_pos[1] - ai_pos[1]) >= 10):
            break
    occupied_positions.add(tuple(goal_pos))

    player_turn = True
    game_over = False
    winner = None
    last_move_time = pygame.time.get_ticks()

    # Generate obstacles
    player_obstacles = generate_obstacles(occupied_positions)
    ai_obstacles = generate_obstacles(occupied_positions)

    # Generate traps
    freeze_traps = generate_traps(occupied_positions)
    random_move_traps = generate_traps(occupied_positions)

    # Generate power-ups
    power_ups = generate_power_ups(occupied_positions)

    player_freeze_moves = 0
    ai_freeze_moves = 0
    player_shield = 0
    ai_shield = 0
    player_trap_reveal = 0
    ai_trap_reveal = 0
    player_penetrate = 0
    ai_penetrate = 0

    # Initialize AI path
    ai_path = [ai_pos[:]]
    predicted_ai_path = [ai_pos[:]]

    # Set the game start time
    game_start_time = pygame.time.get_ticks()

def is_occupied(position, occupied_positions):
    return tuple(position) in occupied_positions


def handle_power_ups(pos, player_type):
    global player_shield, ai_shield, player_trap_reveal, ai_trap_reveal, player_penetrate, ai_penetrate
    global power_up_message, power_up_message_time, trap_revealed

    for power_up in power_ups:
        if pos == power_up[:2]:
            power_up_type = power_up[2]
            power_ups.remove(power_up)
            if power_up_type == "shield":
                if player_type == "Player":
                    player_shield = SHIELD_DURATION
                else:
                    ai_shield = SHIELD_DURATION
                power_up_message = f"{player_type} collected a Shield!"
            elif power_up_type == "trap_reveal":
                if player_type == "Player":
                    player_trap_reveal = TRAP_REVEAL_DURATION
                else:
                    ai_trap_reveal = TRAP_REVEAL_DURATION
                trap_revealed = True
                power_up_message = f"{player_type} collected Trap Reveal!"
            elif power_up_type == "penetrate":
                if player_type == "Player":
                    player_penetrate = PENETRATE_DURATION
                else:
                    ai_penetrate = PENETRATE_DURATION
                power_up_message = f"{player_type} collected Penetrate!"
            power_up_message_time = pygame.time.get_ticks()


def generate_traps(occupied_positions):
    traps = []
    while len(traps) < NUM_TRAPS:
        trap = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        if not is_occupied(trap, occupied_positions):
            traps.append(trap)
            occupied_positions.add(tuple(trap))
    return traps


def generate_obstacles(occupied_positions):
    obstacles = []
    while len(obstacles) < NUM_OBSTACLES:
        obstacle = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        if not is_occupied(obstacle, occupied_positions):
            obstacles.append(obstacle)
            occupied_positions.add(tuple(obstacle))
    return obstacles


initialize_positions()


def display_power_up_message():
    global power_up_message, power_up_message_time
    if power_up_message and pygame.time.get_ticks() - power_up_message_time < POWER_UP_DISPLAY_DURATION:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - power_up_message_time
        alpha = 255  # Starting opacity level

        # Calculate opacity based on elapsed time for fade-in and fade-out
        if elapsed_time < 500:
            alpha = int(255 * elapsed_time / 500)  # Fade in
        elif elapsed_time > POWER_UP_DISPLAY_DURATION - 1000:
            alpha = int(255 * (POWER_UP_DISPLAY_DURATION - elapsed_time) / 1000)  # Fade out

        # Ensure alpha stays within valid range (0 to 255)
        alpha = max(0, min(255, alpha))

        # Render the message with the calculated alpha value
        message_surface = font.render(power_up_message, True, BLACK, WHITE)
        message_surface.set_alpha(255)

        # Calculate dimensions for the message box
        message_rect = message_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT + 30))

        # Create a background rectangle for the power-up message with border
        background_rect = pygame.Surface((message_rect.width + 20, message_rect.height + 20))
        background_rect.set_alpha(alpha)
        background_rect.fill(WHITE)  # Dark background color

        # Calculate position for the background rectangle and border
        background_rect_rect = background_rect.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT + 30))
        border_rect = background_rect_rect.inflate(2, 2)
        pygame.draw.rect(background_rect, BLACK, border_rect, 2)  # Black border

        # Blit the background and the text
        screen.blit(background_rect, background_rect_rect)
        screen.blit(message_surface, message_rect)

    else:
        power_up_message = None

def draw_power_ups():
    for power_up in power_ups:
        power_up_type = power_up[2]
        if power_up_type == "shield":
            screen.blit(shield_image, (power_up[0] * CELL_SIZE, power_up[1] * CELL_SIZE))
        elif power_up_type == "trap_reveal":
            screen.blit(trap_reveal_image, (power_up[0] * CELL_SIZE, power_up[1] * CELL_SIZE))
        elif power_up_type == "penetrate":
            screen.blit(penetrate_image, (power_up[0] * CELL_SIZE, power_up[1] * CELL_SIZE))

def draw_grid():
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Draw traps if revealed
    if trap_revealed:
        for trap in freeze_traps + random_move_traps:
            trap_rect = pygame.Rect(trap[0] * CELL_SIZE, trap[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            #pygame.draw.rect(screen, RED, trap_rect)


def draw_player(image, position):
    screen.blit(image, (position[0] * CELL_SIZE, position[1] * CELL_SIZE))


def draw_goal(image, position):
    screen.blit(image, (position[0] * CELL_SIZE, position[1] * CELL_SIZE))


def draw_obstacles(obstacles, image):
    for obstacle in obstacles:
        screen.blit(image, (obstacle[0] * CELL_SIZE, obstacle[1] * CELL_SIZE))

def draw_traps(traps, image):
    for trap in traps:
        screen.blit(image, (trap[0] * CELL_SIZE, trap[1] * CELL_SIZE))

def calculate_glow_alpha(elapsed_time):
    cycle_time = 1000  # Time in milliseconds for a full glow cycle (fade in and out)
    half_cycle = cycle_time / 2
    time_in_cycle = elapsed_time % cycle_time

    if time_in_cycle <= half_cycle:
        alpha = (time_in_cycle / half_cycle) * 255
    else:
        alpha = ((cycle_time - time_in_cycle) / half_cycle) * 255

    return int(alpha)

def draw_highlighted(image, position, alpha):
    # Draw the glowing highlight
    glow_surface = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
    glow_color = (255, 255, 0, alpha)  # Yellow color with alpha transparency
    pygame.draw.circle(glow_surface, glow_color, (CELL_SIZE * 1.5, CELL_SIZE * 1.5), CELL_SIZE * 1.5)
    screen.blit(glow_surface, (position[0] * CELL_SIZE - CELL_SIZE, position[1] * CELL_SIZE - CELL_SIZE))

    # Draw the original image
    screen.blit(image, (position[0] * CELL_SIZE, position[1] * CELL_SIZE))


def handle_keys():
    global player_turn, last_move_time, player_freeze_moves, player_penetrate
    keys = pygame.key.get_pressed()
    moved = False

    if player_freeze_moves == 0:
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            new_pos = [player_pos[0] - 1, player_pos[1]]
            if player_penetrate > 0 or new_pos not in player_obstacles:
                player_pos[0] -= 1
                moved = True
        if keys[pygame.K_RIGHT] and player_pos[0] < GRID_WIDTH - 1:
            new_pos = [player_pos[0] + 1, player_pos[1]]
            if player_penetrate > 0 or new_pos not in player_obstacles:
                player_pos[0] += 1
                moved = True
        if keys[pygame.K_UP] and player_pos[1] > 0:
            new_pos = [player_pos[0], player_pos[1] - 1]
            if player_penetrate > 0 or new_pos not in player_obstacles:
                player_pos[1] -= 1
                moved = True
        if keys[pygame.K_DOWN] and player_pos[1] < GRID_HEIGHT - 1:
            new_pos = [player_pos[0], player_pos[1] + 1]
            if player_penetrate > 0 or new_pos not in player_obstacles:
                player_pos[1] += 1
                moved = True

        if moved:
            if player_penetrate > 0:
                player_penetrate -= 1
            player_turn = False
            last_move_time = pygame.time.get_ticks()
            check_traps(player_pos, "Player")


def update_trap_reveal():
    global player_trap_reveal, ai_trap_reveal, trap_revealed

    if player_trap_reveal > 0:
        player_trap_reveal -= 1
    if ai_trap_reveal > 0:
        ai_trap_reveal -= 1

    if player_trap_reveal == 0 and ai_trap_reveal == 0:
        trap_revealed = False


def random_move(pos, player_type):
    global trap_message, trap_message_time

    max_distance = abs(pos[0] - goal_pos[0]) + abs(pos[1] - goal_pos[1])
    new_pos = pos[:]

    while True:
        new_pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])
        if new_distance > max_distance and new_pos != pos and new_pos not in player_obstacles and new_pos not in ai_obstacles:
            break

    trap_message = f"{player_type} fell into a Random Move Trap!"
    trap_message_time = pygame.time.get_ticks()

    return new_pos

def check_traps(pos, player_type):
    global player_freeze_moves, ai_freeze_moves, freeze_traps, random_move_traps
    global trap_message, trap_message_time

    if player_type == "Player" and player_shield > 0:
        return
    if player_type == "AI" and ai_shield > 0:
        return

    if pos in freeze_traps:
        freeze_traps.remove(pos)
        trap_message = f"{player_type} fell into a Freezing Trap!"
        trap_message_time = pygame.time.get_ticks()
        if player_type == "Player":
            player_freeze_moves = FREEZE_DURATION
        else:
            ai_freeze_moves = FREEZE_DURATION

    if pos in random_move_traps:
        random_move_traps.remove(pos)
        if player_type == "Player":
            player_pos[:] = random_move(player_pos, "Player")
        else:
            ai_pos[:] = random_move(ai_pos, "AI")

MAX_HISTORY = 5  # Number of past positions to remember
ai_history = []


def fuzzify_distance_to_goal(distance):
    if distance <= 13:
        return {"Near": 1, "Medium": 0, "Far": 0}
    elif 13 < distance <= 17:
        return {"Near": (17 - distance) / 14, "Medium": (distance - 13) / 14, "Far": 0}
    else:
        return {"Near": 0, "Medium": (20 - distance) / 13, "Far": (distance - 17) / 13}


def fuzzify_distance_to_power_up(distance):
    if distance <= 1:
        return {"Close": 1, "Medium": 0, "Far": 0}
    elif 1 < distance <= 4:
        return {"Close": (4 - distance) / 2, "Medium": (distance - 1) / 2, "Far": 0}
    else:
        return {"Close": 0, "Medium": (7 - distance) / 2, "Far": (distance - 5) / 2}


def fuzzy_rules(goal_distance, power_up_distance):
    rules = {
        "MoveToGoal": min(goal_distance["Near"], power_up_distance["Far"]),
        "MoveToPowerUp": min(goal_distance["Far"], power_up_distance["Close"])
    }
    return rules


def fuzzify_positions(ai_pos, goal_pos, power_up_pos):
    distance_to_goal = abs(ai_pos[0] - goal_pos[0]) + abs(ai_pos[1] - goal_pos[1])
    distance_to_power_up = abs(ai_pos[0] - power_up_pos[0]) + abs(ai_pos[1] - power_up_pos[1])

    fuzzy_goal = fuzzify_distance_to_goal(distance_to_goal)
    fuzzy_power_up = fuzzify_distance_to_power_up(distance_to_power_up)

    return fuzzy_goal, fuzzy_power_up


def apply_fuzzy_logic(ai_pos, goal_pos, power_ups):
    best_action = None
    max_activation = 0

    for power_up_pos in power_ups:
        fuzzy_goal, fuzzy_power_up = fuzzify_positions(ai_pos, goal_pos, power_up_pos)
        rule_activations = fuzzy_rules(fuzzy_goal, fuzzy_power_up)

        if rule_activations["MoveToPowerUp"] > max_activation:
            max_activation = rule_activations["MoveToPowerUp"]
            best_action = "MoveToPowerUp"

    return best_action

from heapq import heappush, heappop

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal, obstacles, traps):
    open_list = []
    heappush(open_list, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[tuple(start)] = None
    cost_so_far[tuple(start)] = 0

    while open_list:
        current = heappop(open_list)[1]

        if current == goal:
            break

        for direction in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            neighbor = [current[0] + direction[0], current[1] + direction[1]]
            neighbor_tuple = tuple(neighbor)
            if (0 <= neighbor[0] < GRID_WIDTH and
                0 <= neighbor[1] < GRID_HEIGHT and
                neighbor not in obstacles and
                neighbor not in traps):

                new_cost = cost_so_far[tuple(current)] + 1
                if neighbor_tuple not in cost_so_far or new_cost < cost_so_far[neighbor_tuple]:
                    cost_so_far[neighbor_tuple] = new_cost
                    priority = new_cost + heuristic(goal, neighbor)
                    heappush(open_list, (priority, neighbor))
                    came_from[neighbor_tuple] = current

    if tuple(goal) not in came_from:
        return []  # No path found

    # Reconstruct path
    path = []
    current = goal
    while current:
        path.append(current)
        current = came_from[tuple(current)]
    path.reverse()
    return path


def ai_move():
    global ai_pos, player_turn, last_move_time, ai_path, predicted_ai_path, ai_history, ai_penetrate, ai_freeze_moves, power_ups,action

    if ai_freeze_moves > 0:
        ai_freeze_moves -= 1
        player_turn = True
        last_move_time = pygame.time.get_ticks()
        return

    goal_posistion = goal_pos  # Assuming the goal position is the player's position

    traps = freeze_traps + random_move_traps if trap_revealed else []
    ai_path = a_star_search(ai_pos, goal_posistion, ai_obstacles, traps)
    if ai_path and len(ai_path) > 1:
        ai_pos = ai_path[1]  # Move to the next position in the path
        ai_path = ai_path[1:]  # Update the path to remove the current position
    else:
        best_score = float('-inf')
        best_move = None
        best_path = []
        penalty = 5  # Penalty for revisiting a node

        # Apply fuzzy logic to decide between moving to goal or power-up
        action = apply_fuzzy_logic(ai_pos, goal_posistion, [pu[:2] for pu in power_ups])

        if action == "MoveToPowerUp":
            # Find the closest power-up
            best_power_up = min(power_ups, key=lambda pu: abs(ai_pos[0] - pu[0]) + abs(ai_pos[1] - pu[1]))
            if ai_pos[0] < best_power_up[0]:
                ai_pos[0] += 1
            elif ai_pos[0] > best_power_up[0]:
                ai_pos[0] -= 1
            elif ai_pos[1] < best_power_up[1]:
                ai_pos[1] += 1
            elif ai_pos[1] > best_power_up[1]:
                ai_pos[1] -= 1
        else:
            for move in get_possible_moves(ai_pos, ai_obstacles if ai_penetrate == 0 else []):
                ai_pos_new = [ai_pos[0] + move[0], ai_pos[1] + move[1]]
                score, path = minimax(ai_pos_new, player_pos, MAX_DEPTH, False, float('-inf'), float('inf'), [ai_pos])

                # Apply a penalty if the move goes back to a recent position
                if ai_pos_new in ai_history:
                    score -= penalty

                if score > best_score:
                    best_score = score
                    best_move = move
                    best_path = path

        if best_move:
            ai_pos[0] += best_move[0]
            ai_pos[1] += best_move[1]
            ai_path.append(ai_pos[:])  # Append the new position to the path
            predicted_ai_path = best_path
    ai_history.append(ai_pos[:])
    if len(ai_history) > MAX_HISTORY:
        ai_history.pop(0)

    if ai_penetrate > 0:
        ai_penetrate -= 1

    check_traps(ai_pos, "AI")

    player_turn = True
    last_move_time = pygame.time.get_ticks()

def display_trap_message():
    global trap_message, trap_message_time
    if trap_message and pygame.time.get_ticks() - trap_message_time < TRAP_DISPLAY_DURATION:
        if "Player" in trap_message:
            text_color = (255, 153, 102)
        else:
            text_color = (128, 128, 255)

        text = font.render(trap_message, True, text_color)

        # Create a background rectangle for the trap message
        background_rect = pygame.Surface((text.get_width() + 20, text.get_height() + 20))
        background_rect.set_alpha(200)  # Set transparency level (0-255)
        background_rect.fill((41, 61, 61))  # Background color

        # Calculate the position for the message box above the scoreboard
        message_x = (WINDOW_WIDTH - background_rect.get_width()) // 2  # Centered horizontally
        message_y = WINDOW_HEIGHT + 10  # 10 pixels below the scoreboard

        # Calculate the position for animation
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - trap_message_time
        if elapsed_time < 500:
            alpha = int(255 * elapsed_time / 500)  # Fade in animation
        elif elapsed_time > TRAP_DISPLAY_DURATION - 500:
            alpha = int(255 * (TRAP_DISPLAY_DURATION - elapsed_time) / 500)  # Fade out animation
        else:
            alpha = 255

        background_rect.set_alpha(alpha)
        background_rect_rect = background_rect.get_rect(topleft=(message_x, message_y))

        # Draw a border around the background rectangle
        border_rect = background_rect_rect.inflate(2, 2)
        pygame.draw.rect(background_rect, BLACK, border_rect, 2)  # 2-pixel wide border

        # Blit the background and the text
        screen.blit(background_rect, background_rect_rect)
        screen.blit(text, (background_rect_rect.x + 10, background_rect_rect.y + 10))

    else:
        trap_message = None

def get_possible_moves(pos, obstacles, penetrate_duration=0):
    moves = []
    if pos[0] > 0 and ([pos[0] - 1, pos[1]] not in obstacles or penetrate_duration > 0):
        moves.append([-1, 0])
    if pos[0] < GRID_WIDTH - 1 and ([pos[0] + 1, pos[1]] not in obstacles or penetrate_duration > 0):
        moves.append([1, 0])
    if pos[1] > 0 and ([pos[0], pos[1] - 1] not in obstacles or penetrate_duration > 0):
        moves.append([0, -1])
    if pos[1] < GRID_HEIGHT - 1 and ([pos[0], pos[1] + 1] not in obstacles or penetrate_duration > 0):
        moves.append([0, 1])
    return moves


def minimax(ai_pos, player_pos, depth, is_maximizing, alpha, beta, path=[]):
    if depth == 0 or ai_pos == goal_pos or player_pos == goal_pos:
        return evaluate(ai_pos, player_pos), path

    if is_maximizing:
        max_eval = float('-inf')
        best_path = path
        for move in get_possible_moves(ai_pos, ai_obstacles):
            new_ai_pos = [ai_pos[0] + move[0], ai_pos[1] + move[1]]
            eval, new_path = minimax(new_ai_pos, player_pos, depth - 1, False, alpha, beta, path + [new_ai_pos])
            if eval > max_eval:
                max_eval = eval
                best_path = new_path
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_path
    else:
        min_eval = float('inf')
        best_path = path
        for move in get_possible_moves(player_pos, player_obstacles):
            new_player_pos = [player_pos[0] + move[0], player_pos[1] + move[1]]
            eval, new_path = minimax(ai_pos, new_player_pos, depth - 1, True, alpha, beta, path)
            if eval < min_eval:
                min_eval = eval
                best_path = new_path
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_path



def evaluate(ai_pos, player_pos):
    ai_distance = abs(ai_pos[0] - goal_pos[0]) + abs(ai_pos[1] - goal_pos[1])
    player_distance = abs(player_pos[0] - goal_pos[0]) + abs(player_pos[1] - goal_pos[1])
    return player_distance - ai_distance


def check_winner():
    global game_over, winner, player_score, ai_score
    if player_pos == goal_pos:
        game_over = True
        winner = "Player"
        player_score += 1
    elif ai_pos == goal_pos:
        game_over = True
        winner = "AI"
        ai_score += 1


def display_winner():
    global winner
    if winner:
        if winner == "Player":
            text_color = RED
        else:
            text_color = BLUE

        text = font.render(f"{winner} wins!", True, text_color)

        # Create a background rectangle for the winner message
        background_rect = pygame.Surface((text.get_width() + 20, text.get_height() + 20))
        background_rect.set_alpha(200)  # Set transparency level (0-255)
        background_rect.fill(BLACK)  # Background color

        # Calculate the position for animation
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_move_time
        if elapsed_time < 500:
            alpha = int(255 * elapsed_time / 500)  # Fade in animation
        else:
            alpha = 255

        background_rect.set_alpha(alpha)
        background_rect_rect = background_rect.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # Draw a border around the background rectangle
        border_rect = background_rect_rect.inflate(2, 2)
        pygame.draw.rect(screen, BLACK, border_rect, 2)  # 2-pixel wide border

        # Blit the background and the text
        screen.blit(background_rect, background_rect_rect)
        screen.blit(text, (background_rect_rect.x + 10, background_rect_rect.y + 10))

        # Clear winner after displaying for a certain time
        if elapsed_time > 3000:
            winner = None


def draw_play_again_button():
    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 40, 150, 50)
    pygame.draw.rect(screen, BLACK, button_rect)
    text = font.render("Play Again", True, WHITE)
    screen.blit(text, (button_rect.x + (button_rect.width - text.get_width()) // 2,
                       button_rect.y + (button_rect.height - text.get_height()) // 2))
    return button_rect


def handle_play_again_click(mouse_pos):
    button_rect = draw_play_again_button()
    if button_rect.collidepoint(mouse_pos):
        initialize_positions()

def draw_scoreboard():
    # Create the text surfaces for the scoreboard
    player_text = font.render(f"Player: {player_score}", True, (255, 71, 26))
    ai_text = font.render(f"AI: {ai_score}", True, (128, 128, 255))

    # Get the rectangles for positioning
    player_rect = player_text.get_rect(center=(WINDOW_WIDTH // 4, WINDOW_HEIGHT + 25))
    ai_rect = ai_text.get_rect(center=(3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT + 25))

    # Create a background rectangle with padding
    background_rect = pygame.Surface((WINDOW_WIDTH, 50))
    background_rect.set_alpha(200)  # Set transparency level (0-255)
    background_rect.fill((31, 31, 46))  # Background color
    background_rect_rect = background_rect.get_rect(topleft=(0, WINDOW_HEIGHT))

    # Draw a border around the background rectangle
    border_rect = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, 50)
    pygame.draw.rect(screen, BLACK, border_rect, 2)  # 2-pixel wide border

    # Blit the background and the text
    screen.blit(background_rect, background_rect_rect)
    screen.blit(player_text, player_rect)
    screen.blit(ai_text, ai_rect)

def draw_ui():
    # Define the position and size of the UI background
    ui_x = GRID_WIDTH * CELL_SIZE + 1  # Starting x position of the UI
    ui_y = 0  # Starting y position of the UI
    ui_width = 300  # Width of the UI
    ui_height = WINDOW_HEIGHT   # Height of the UI

    # Draw the UI background
    pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (ui_x, ui_y, ui_width, ui_height))

    ui_x += 10  # Adjust for padding inside the UI background
    ui_y += 10  # Adjust for padding inside the UI background
    spacing = 52  # Space between each item

    # List of traps and power-ups with their images, names, and descriptions
    items = [
        ("img/player.png", "Player", "You control this character"),
        ("img/hacker.png", "Hacker(AI)", "Your opponent"),
        ("img/computer.png", "Goal", "Reach this to win"),
        ("img/wallred.png", "Wall Block (For AI)", "Obstacles placed by the player"),
        ("img/wallblue.png", "Wall Block (For player)", "Obstacles placed by the AI"),
        ("img/spring.png", "Random Move Trap", "Forces random movement for 1 turn"),
        ("img/freezing.png", "Freeze Trap", "Freezes for 2 turns"),
        ("img/sheild.png", "Shield", "Protects from traps for 10 seconds"),
        ("img/eye.png", "Trap Reveal", "Reveals traps for 10 seconds"),
        ("img/wall_penetrate.png", "Penetrate", "Move through obstacles for 10 seconds")
    ]

    for img_path, name, description in items:
        # Load image
        image = pygame.image.load(img_path)
        image = pygame.transform.scale(image, (30, 30))

        # Render text
        name_text = font2.render(name, True, WHITE)  # White color
        desc_text = small_font.render(description, True, (255, 255, 255))  # White color

        # Blit image and text
        screen.blit(image, (ui_x, ui_y))
        screen.blit(name_text, (ui_x + 40, ui_y))
        screen.blit(desc_text, (ui_x + 40, ui_y + 25))

        # Move to the next item position
        ui_y += spacing
# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            handle_play_again_click(event.pos)
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                handle_enter_key()

    current_time = pygame.time.get_ticks()

    if not game_over:
        if player_turn and current_time - last_move_time > DELAY:
            if player_freeze_moves == 0:
                handle_keys()
                handle_power_ups(player_pos, "Player")
            else:
                player_freeze_moves -= 1
                player_turn = False
                last_move_time = pygame.time.get_ticks()
        elif not player_turn and current_time - last_move_time > DELAY:
            ai_move()
            handle_power_ups(ai_pos, "AI")  # Call handle_power_ups for AI position here
            player_turn = True  # Assuming after AI moves, it's player's turn
            last_move_time = pygame.time.get_ticks()
        check_winner()
        update_trap_reveal()

    # Calculate elapsed time since game start
    elapsed_time = pygame.time.get_ticks() - game_start_time

    if elapsed_time < HIGHLIGHT_DURATION:
        alpha = calculate_glow_alpha(elapsed_time)
    else:
        alpha = 255
    screen.fill(GRAY)
    display_trap_message()  # Display any active trap messages
    display_power_up_message()
    draw_grid()
    handle_button_clicks()
    #draw_goal(goal_image, goal_pos)
    draw_obstacles(player_obstacles, player_obstacle_image)  # Use image for player obstacles
    draw_obstacles(ai_obstacles, ai_obstacle_image)  # Use image for AI obstacles
    #draw_predicted_path(predicted_ai_path, GREEN)  # Draw predicted AI path in green
    #draw_ai_path(ai_path, BLUE)  # Draw AI path in blue

    if player_trap_reveal > 0 or ai_trap_reveal > 0:
        draw_traps(freeze_traps, freeze_image)
        draw_traps(random_move_traps, trap_image)

    #draw_player(player_image, player_pos)
    #draw_player(ai_image, ai_pos)

    draw_scoreboard()
    draw_power_ups()
    draw_ui()
    draw_button_window()
    if elapsed_time < HIGHLIGHT_DURATION:
        draw_highlighted(goal_image, goal_pos, alpha)
        draw_highlighted(player_image, player_pos,alpha)
        draw_highlighted(ai_image, ai_pos,alpha)
    else:
        draw_goal(goal_image, goal_pos)
        draw_player(player_image, player_pos)
        draw_player(ai_image, ai_pos)


    display_trap_message()  # Display any active trap messages
    if game_over:
        display_winner()
        draw_play_again_button()

    pygame.display.flip()
    clock.tick(FPS)

    if player_shield > 0:
        player_shield -= 1
    if ai_shield > 0:
        ai_shield -= 1
    if player_trap_reveal > 0:
        player_trap_reveal -= 1
    if ai_trap_reveal > 0:
        ai_trap_reveal -= 1
    if player_penetrate > 0:
        player_penetrate -= 1
    if ai_penetrate > 0:
        ai_penetrate -= 1