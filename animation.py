import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import matplotlib.patches as mpatches
import matplotlib

# Individual Class
class Individual:
    def __init__(self, role, speed, perception, energy, position=None):
        self.role = role  # "hunter", "gatherer", etc.
        self.speed = speed
        self.perception = perception
        self.energy = energy
        self.position = position if position else (random.randint(0, 100), random.randint(0, 100))
        self.resources_collected = 0

    def move(self):
        self.position = (
            max(0, min(100, self.position[0] + random.randint(-self.speed, self.speed))),
            max(0, min(100, self.position[1] + random.randint(-self.speed, self.speed))),
        )
        self.energy -= 1  # Moving costs energy

    def collect_resource(self, resource_position):
        if self.distance_to(resource_position) < self.perception:
            self.resources_collected += 1
            self.energy += 10  # Regain some energy by collecting resources

    def distance_to(self, target_position):
        return ((self.position[0] - target_position[0]) ** 2 + (self.position[1] - target_position[1]) ** 2) ** 0.5


# Keyboard-controlled Player Class
class ControlledIndividual(Individual):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = [0, 0]  # [dx, dy]

    def move_controlled(self):
        self.position = (
            max(0, min(100, self.position[0] + self.direction[0] * self.speed)),
            max(0, min(100, self.position[1] + self.direction[1] * self.speed)),
        )
        self.energy -= 1  # Moving costs energy


# Environment Class
class Environment:
    def __init__(self, resource_count):
        self.resources = [
            (random.randint(0, 100), random.randint(0, 100)) for _ in range(resource_count)
        ]

    def regenerate_resources(self, count):
        self.resources.extend(
            (random.randint(0, 100), random.randint(0, 100)) for _ in range(count)
        )

    def remove_resource(self, position):
        self.resources = [res for res in self.resources if res != position]


# Game Class
class SurvivalGame:
    def __init__(self, player_count, resource_count, max_days):
        self.players = [
            Individual("gatherer" if i % 2 == 0 else "hunter", random.randint(1, 5), random.randint(5, 10), 100)
            for i in range(player_count - 1)
        ]
        self.controlled_player = ControlledIndividual("controlled", 5, 10, 100)
        self.environment = Environment(resource_count)
        self.day = 0
        self.max_days = max_days

    def step(self):
        if self.day >= self.max_days or not self.players and self.controlled_player.energy <= 0:
            return False

        self.day += 1
        # Move AI players
        for player in self.players:
            player.move()
            for resource in self.environment.resources:
                if player.distance_to(resource) < player.perception:
                    player.collect_resource(resource)
                    self.environment.remove_resource(resource)
                    break

        # Move controlled player
        self.controlled_player.move_controlled()
        for resource in self.environment.resources:
            if self.controlled_player.distance_to(resource) < self.controlled_player.perception:
                self.controlled_player.collect_resource(resource)
                self.environment.remove_resource(resource)
                break

        # Check if players run out of energy
        self.players = [player for player in self.players if player.energy > 0]

        # Regenerate some resources daily
        self.environment.regenerate_resources(random.randint(1, 5))
        return True


# Visualization using FuncAnimation
def update(frame):
    if not game.step():
        ani.event_source.stop()
        return

    plt.cla()
    player_positions = [player.position for player in game.players]
    controlled_position = game.controlled_player.position
    resource_positions = game.environment.resources

    if player_positions:
        player_x, player_y = zip(*player_positions)
        plt.scatter(player_x, player_y, color="blue", label="Players", alpha=0.7)

    if resource_positions:
        resource_x, resource_y = zip(*resource_positions)
        plt.scatter(resource_x, resource_y, color="green", label="Resources", alpha=0.7)

    plt.scatter(*controlled_position, color="red", label="Controlled Player", alpha=0.7)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.title(f"Day {game.day}")
    plt.legend()


def on_key(event):
    # Map keys to movement direction
    if event.key == "up":
        game.controlled_player.direction = [0, 1]
    elif event.key == "down":
        game.controlled_player.direction = [0, -1]
    elif event.key == "left":
        game.controlled_player.direction = [-1, 0]
    elif event.key == "right":
        game.controlled_player.direction = [1, 0]
    else:
        game.controlled_player.direction = [0, 0]


# Run the Survival Game
game = SurvivalGame(player_count=10, resource_count=20, max_days=50)
fig, ax = plt.subplots(figsize=(8, 8))
fig.canvas.mpl_connect("key_press_event", on_key)
ani = FuncAnimation(fig, update, frames=range(50), repeat=False, interval=500)
plt.show()
