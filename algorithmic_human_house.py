import pygame
import sys
import math
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
from enum import Enum
import colorsys

# Initialize pygame
pygame.init()

class BodyPart(Enum):
    HEAD = "head"
    TORSO = "torso"
    ARM_LEFT = "arm_left"
    ARM_RIGHT = "arm_right"
    LEG_LEFT = "leg_left"
    LEG_RIGHT = "leg_right"

class HousePart(Enum):
    FOUNDATION = "foundation"
    WALLS = "walls"
    ROOF = "roof"
    DOOR = "door"
    WINDOWS = "windows"
    CHIMNEY = "chimney"

@dataclass
class HumanConfig:
    height: float = 1.0
    proportions: dict = None
    posture: float = 0.5  # 0 = slumped, 1 = upright
    movement: float = 0.0  # 0 = standing, 1 = walking
    style: str = "realistic"
    
    def __post_init__(self):
        if self.proportions is None:
            self.proportions = {
                'head_size': 0.15,
                'torso_length': 0.3,
                'arm_length': 0.4,
                'leg_length': 0.45,
                'shoulder_width': 0.2,
                'hip_width': 0.15
            }

@dataclass
class HouseConfig:
    width: float = 1.0
    height: float = 1.0
    roof_type: str = "gable"  # gable, flat, hip, mansard
    stories: int = 2
    symmetry: float = 0.8  # 0 = asymmetric, 1 = perfectly symmetric
    style: str = "modern"
    
    def __post_init__(self):
        self.window_count = random.randint(2, 6)
        self.door_width = 0.15 * self.width

class AlgorithmicArtist:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Algorithmic Human & House Generator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Color palettes
        self.human_palette = {
            'skin': [(255, 224, 189), (210, 180, 140), (180, 150, 120)],
            'clothing': [(70, 130, 180), (220, 20, 60), (34, 139, 34)],
            'hair': [(139, 69, 19), (0, 0, 0), (210, 180, 140)]
        }
        
        self.house_palette = {
            'walls': [(240, 230, 210), (200, 200, 200), (180, 200, 220)],
            'roof': [(139, 0, 0), (105, 105, 105), (160, 120, 80)],
            'door': [(101, 67, 33), (139, 69, 19), (0, 0, 0)],
            'windows': [(173, 216, 230), (240, 248, 255)]
        }
        
        self.current_human = None
        self.current_house = None
        self.relationship = "standing"  # standing, entering, leaning, watching
        
    def generate_l_system(self, axiom, rules, iterations):
        """Generate L-system string for organic shapes"""
        result = axiom
        for _ in range(iterations):
            new_result = ""
            for char in result:
                new_result += rules.get(char, char)
            result = new_result
        return result
    
    def draw_l_system(self, start_pos, angle, length, l_string, angle_change):
        """Draw L-system on screen"""
        stack = []
        current_pos = start_pos
        current_angle = angle
        
        for char in l_string:
            if char == 'F':
                new_pos = (
                    current_pos[0] + length * math.cos(math.radians(current_angle)),
                    current_pos[1] + length * math.sin(math.radians(current_angle))
                )
                pygame.draw.line(self.screen, (0, 0, 0), current_pos, new_pos, 2)
                current_pos = new_pos
            elif char == '+':
                current_angle += angle_change
            elif char == '-':
                current_angle -= angle_change
            elif char == '[':
                stack.append((current_pos, current_angle))
            elif char == ']':
                current_pos, current_angle = stack.pop()
    
    def create_bezier_curve(self, points, num_segments=100):
        """Create smooth Bézier curve"""
        curve_points = []
        for i in range(num_segments + 1):
            t = i / num_segments
            # De Casteljau's algorithm
            temp_points = list(points)
            while len(temp_points) > 1:
                new_points = []
                for j in range(len(temp_points) - 1):
                    x = (1 - t) * temp_points[j][0] + t * temp_points[j + 1][0]
                    y = (1 - t) * temp_points[j][1] + t * temp_points[j + 1][1]
                    new_points.append((x, y))
                temp_points = new_points
            curve_points.append(temp_points[0])
        return curve_points
    
    def draw_bezier_shape(self, control_points, color, closed=True):
        """Draw a shape using Bézier curves"""
        if len(control_points) < 3:
            return
            
        curve_points = self.create_bezier_curve(control_points)
        
        if closed:
            curve_points.append(curve_points[0])
            
        if len(curve_points) > 1:
            pygame.draw.lines(self.screen, color, False, curve_points, 2)
            
    def generate_human(self, config: HumanConfig):
        """Generate algorithmic human figure"""
        human_data = {}
        
        # Base position
        base_x = self.width // 4
        base_y = self.height * 0.7
        
        # Apply posture
        posture_offset = (1 - config.posture) * 30
        
        # Head - using Bézier curves for organic shape
        head_radius = config.height * config.proportions['head_size'] * 100
        head_center = (base_x, base_y - config.height * 100 + head_radius)
        
        # Create oval head with Bézier
        head_points = []
        for angle in np.linspace(0, 2 * math.pi, 8):
            # Make head slightly oval (wider than tall)
            rx = head_radius * 0.8
            ry = head_radius * 1.1
            x = head_center[0] + rx * math.cos(angle)
            y = head_center[1] + ry * math.sin(angle)
            head_points.append((x, y))
        
        human_data[BodyPart.HEAD] = {
            'center': head_center,
            'points': head_points,
            'radius': head_radius
        }
        
        # Torso - using modified sine wave for natural curvature
        torso_length = config.height * config.proportions['torso_length'] * 100
        shoulder_y = head_center[1] + head_radius * 1.2
        hip_y = shoulder_y + torso_length
        
        # Create torso with natural curve
        torso_points = []
        shoulder_width = config.proportions['shoulder_width'] * 100
        hip_width = config.proportions['hip_width'] * 100
        
        # Left side of torso (sinusoidal curve)
        for i in range(11):
            t = i / 10
            x_offset = shoulder_width * (1 - t) + hip_width * t
            # Natural body curve using sine
            curve = math.sin(t * math.pi) * 5 * (1 - config.posture)
            x = base_x - x_offset + posture_offset + curve
            y = shoulder_y + torso_length * t
            torso_points.append((x, y))
        
        # Right side of torso
        for i in range(10, -1, -1):
            t = i / 10
            x_offset = shoulder_width * (1 - t) + hip_width * t
            curve = math.sin(t * math.pi) * 5 * (1 - config.posture)
            x = base_x + x_offset + posture_offset + curve
            y = shoulder_y + torso_length * t
            torso_points.append((x, y))
        
        torso_points.append(torso_points[0])  # Close the shape
        
        human_data[BodyPart.TORSO] = {
            'points': torso_points,
            'shoulder_y': shoulder_y,
            'hip_y': hip_y
        }
        
        # Arms - with natural hanging/walking motion
        arm_length = config.height * config.proportions['arm_length'] * 100
        
        # Calculate arm positions based on movement
        arm_swing = math.sin(config.movement * math.pi * 2) * 30 if config.movement > 0 else 0
        
        # Left arm
        arm_start_left = (base_x - shoulder_width + posture_offset, shoulder_y + torso_length * 0.2)
        arm_angle_left = math.radians(190 + arm_swing)  # Natural hanging angle with swing
        
        arm_end_left = (
            arm_start_left[0] + arm_length * math.cos(arm_angle_left),
            arm_start_left[1] + arm_length * math.sin(arm_angle_left)
        )
        
        # Add elbow for more natural look
        elbow_left = (
            arm_start_left[0] + arm_length * 0.5 * math.cos(arm_angle_left),
            arm_start_left[1] + arm_length * 0.5 * math.sin(arm_angle_left)
        )
        
        human_data[BodyPart.ARM_LEFT] = {
            'points': [arm_start_left, elbow_left, arm_end_left],
            'length': arm_length
        }
        
        # Right arm
        arm_start_right = (base_x + shoulder_width + posture_offset, shoulder_y + torso_length * 0.2)
        arm_angle_right = math.radians(170 - arm_swing)
        
        arm_end_right = (
            arm_start_right[0] + arm_length * math.cos(arm_angle_right),
            arm_start_right[1] + arm_length * math.sin(arm_angle_right)
        )
        
        elbow_right = (
            arm_start_right[0] + arm_length * 0.5 * math.cos(arm_angle_right),
            arm_start_right[1] + arm_length * 0.5 * math.sin(arm_angle_right)
        )
        
        human_data[BodyPart.ARM_RIGHT] = {
            'points': [arm_start_right, elbow_right, arm_end_right],
            'length': arm_length
        }
        
        # Legs - with walking motion
        leg_length = config.height * config.proportions['leg_length'] * 100
        
        # Leg separation based on movement
        leg_spread = 20 + abs(arm_swing) * 0.5
        
        # Left leg
        leg_start_left = (base_x - hip_width * 0.7 + posture_offset, hip_y)
        leg_angle_left = math.radians(270 + leg_spread - arm_swing * 0.7)
        
        leg_end_left = (
            leg_start_left[0] + leg_length * math.cos(leg_angle_left),
            leg_start_left[1] + leg_length * math.sin(leg_angle_left)
        )
        
        # Add knee
        knee_left = (
            leg_start_left[0] + leg_length * 0.4 * math.cos(leg_angle_left),
            leg_start_left[1] + leg_length * 0.4 * math.sin(leg_angle_left)
        )
        
        human_data[BodyPart.LEG_LEFT] = {
            'points': [leg_start_left, knee_left, leg_end_left],
            'length': leg_length
        }
        
        # Right leg
        leg_start_right = (base_x + hip_width * 0.7 + posture_offset, hip_y)
        leg_angle_right = math.radians(270 - leg_spread + arm_swing * 0.7)
        
        leg_end_right = (
            leg_start_right[0] + leg_length * math.cos(leg_angle_right),
            leg_start_right[1] + leg_length * math.sin(leg_angle_right)
        )
        
        knee_right = (
            leg_start_right[0] + leg_length * 0.4 * math.cos(leg_angle_right),
            leg_start_right[1] + leg_length * 0.4 * math.sin(leg_angle_right)
        )
        
        human_data[BodyPart.LEG_RIGHT] = {
            'points': [leg_start_right, knee_right, leg_end_right],
            'length': leg_length
        }
        
        self.current_human = human_data
        return human_data
    
    def generate_house(self, config: HouseConfig):
        """Generate algorithmic house"""
        house_data = {}
        
        # Base position (right side of screen)
        base_x = self.width * 3 // 4
        base_y = self.height * 0.7
        
        # Foundation
        foundation_width = config.width * 200
        foundation_height = 20
        
        foundation_rect = pygame.Rect(
            base_x - foundation_width // 2,
            base_y - foundation_height,
            foundation_width,
            foundation_height
        )
        
        house_data[HousePart.FOUNDATION] = {
            'rect': foundation_rect,
            'points': [
                (foundation_rect.left, foundation_rect.top),
                (foundation_rect.right, foundation_rect.top),
                (foundation_rect.right, foundation_rect.bottom),
                (foundation_rect.left, foundation_rect.bottom)
            ]
        }
        
        # Walls - add slight irregularity for organic feel
        wall_height = config.height * 200
        wall_top = foundation_rect.top - wall_height
        
        # Introduce asymmetry based on symmetry parameter
        asymmetry_left = (1 - config.symmetry) * random.uniform(-20, 20)
        asymmetry_right = (1 - config.symmetry) * random.uniform(-20, 20)
        
        wall_points = [
            (foundation_rect.left + asymmetry_left, wall_top),
            (foundation_rect.right + asymmetry_right, wall_top),
            (foundation_rect.right, foundation_rect.top),
            (foundation_rect.left, foundation_rect.top)
        ]
        
        house_data[HousePart.WALLS] = {
            'points': wall_points,
            'height': wall_height
        }
        
        # Roof based on type
        roof_height = wall_height * 0.3
        
        if config.roof_type == "gable":
            # Gable roof
            roof_points = [
                (wall_points[0][0] - 10, wall_points[0][1]),  # Left eave
                (wall_points[1][0] + 10, wall_points[1][1]),  # Right eave
                ((wall_points[0][0] + wall_points[1][0]) / 2, wall_points[0][1] - roof_height)  # Peak
            ]
        elif config.roof_type == "flat":
            # Flat roof
            roof_points = [
                (wall_points[0][0] - 10, wall_points[0][1]),
                (wall_points[1][0] + 10, wall_points[0][1]),
                (wall_points[1][0] + 10, wall_points[0][1] - 10),
                (wall_points[0][0] - 10, wall_points[0][1] - 10)
            ]
        elif config.roof_type == "hip":
            # Hip roof
            roof_points = [
                (wall_points[0][0], wall_points[0][1]),
                (wall_points[1][0], wall_points[1][1]),
                ((wall_points[0][0] + wall_points[1][0]) / 2, wall_points[0][1] - roof_height * 0.7),
                (wall_points[0][0], wall_points[0][1] - roof_height * 0.3)
            ]
        else:  # mansard
            # Mansard roof
            roof_points = [
                (wall_points[0][0], wall_points[0][1]),
                (wall_points[1][0], wall_points[1][1]),
                (wall_points[1][0], wall_points[0][1] - roof_height * 0.5),
                ((wall_points[0][0] + wall_points[1][0]) / 2, wall_points[0][1] - roof_height),
                (wall_points[0][0], wall_points[0][1] - roof_height * 0.5)
            ]
        
        house_data[HousePart.ROOF] = {
            'points': roof_points,
            'type': config.roof_type
        }
        
        # Door
        door_width = config.door_width
        door_height = wall_height * 0.3
        
        door_left = base_x - door_width // 2
        door_bottom = foundation_rect.top
        
        door_points = [
            (door_left, door_bottom),
            (door_left + door_width, door_bottom),
            (door_left + door_width, door_bottom - door_height),
            (door_left, door_bottom - door_height)
        ]
        
        house_data[HousePart.DOOR] = {
            'points': door_points,
            'center': (door_left + door_width // 2, door_bottom - door_height // 2)
        }
        
        # Windows - generate algorithmically
        window_width = door_width * 0.6
        window_height = door_height * 0.7
        
        windows = []
        
        # Calculate window positions using grid
        cols = min(3, config.window_count)
        rows = math.ceil(config.window_count / cols)
        
        # Available wall space for windows
        wall_space_left = wall_points[0][0] + 20
        wall_space_right = wall_points[1][0] - 20
        wall_space_width = wall_space_right - wall_space_left
        
        # Grid spacing
        col_spacing = wall_space_width / (cols + 1)
        row_spacing = wall_height * 0.6 / (rows + 1)
        
        for row in range(rows):
            for col in range(cols):
                if len(windows) >= config.window_count:
                    break
                    
                # Add some random offset for organic placement
                offset_x = (1 - config.symmetry) * random.uniform(-10, 10)
                offset_y = (1 - config.symmetry) * random.uniform(-5, 5)
                
                center_x = wall_space_left + (col + 1) * col_spacing + offset_x
                center_y = wall_top + wall_height * 0.2 + (row + 1) * row_spacing + offset_y
                
                window_points = [
                    (center_x - window_width // 2, center_y - window_height // 2),
                    (center_x + window_width // 2, center_y - window_height // 2),
                    (center_x + window_width // 2, center_y + window_height // 2),
                    (center_x - window_width // 2, center_y + window_height // 2)
                ]
                
                windows.append(window_points)
        
        house_data[HousePart.WINDOWS] = {
            'windows': windows,
            'count': len(windows)
        }
        
        # Chimney (sometimes)
        if random.random() > 0.3 and config.roof_type != "flat":
            chimney_width = door_width * 0.3
            chimney_height = roof_height * 0.8
            
            # Place chimney on roof
            chimney_left = wall_points[0][0] + wall_space_width * random.uniform(0.2, 0.8)
            chimney_bottom = wall_points[0][1] - roof_height * 0.2
            
            chimney_points = [
                (chimney_left, chimney_bottom),
                (chimney_left + chimney_width, chimney_bottom),
                (chimney_left + chimney_width, chimney_bottom - chimney_height),
                (chimney_left, chimney_bottom - chimney_height)
            ]
            
            house_data[HousePart.CHIMNEY] = {
                'points': chimney_points
            }
        
        self.current_house = house_data
        return house_data
    
    def draw_human(self, human_data, style="realistic"):
        """Draw the generated human"""
        if not human_data:
            return
        
        # Draw torso
        torso_points = human_data[BodyPart.TORSO]['points']
        torso_color = random.choice(self.human_palette['clothing'])
        pygame.draw.polygon(self.screen, torso_color, torso_points)
        pygame.draw.lines(self.screen, (0, 0, 0), True, torso_points, 2)
        
        # Draw head
        head_points = human_data[BodyPart.HEAD]['points']
        skin_color = random.choice(self.human_palette['skin'])
        
        # Create head shape with Bézier
        self.draw_bezier_shape(head_points, skin_color)
        
        # Fill head
        if len(head_points) > 2:
            pygame.draw.polygon(self.screen, skin_color, head_points)
            pygame.draw.lines(self.screen, (0, 0, 0), True, head_points, 2)
        
        # Draw facial features (simplified)
        head_center = human_data[BodyPart.HEAD]['center']
        head_radius = human_data[BodyPart.HEAD]['radius']
        
        # Eyes
        eye_y = head_center[1] - head_radius * 0.2
        eye_spacing = head_radius * 0.3
        
        pygame.draw.circle(self.screen, (0, 0, 0), 
                          (int(head_center[0] - eye_spacing), int(eye_y)), 
                          int(head_radius * 0.08))
        pygame.draw.circle(self.screen, (0, 0, 0), 
                          (int(head_center[0] + eye_spacing), int(eye_y)), 
                          int(head_radius * 0.08))
        
        # Mouth - simple curve
        mouth_points = []
        for i in range(5):
            x = head_center[0] - head_radius * 0.2 + i * head_radius * 0.1
            y = head_center[1] + head_radius * 0.2 + math.sin(i * 0.5) * 3
            mouth_points.append((x, y))
        
        if len(mouth_points) > 1:
            pygame.draw.lines(self.screen, (0, 0, 0), False, mouth_points, 2)
        
        # Draw arms
        for arm_part in [BodyPart.ARM_LEFT, BodyPart.ARM_RIGHT]:
            arm_points = human_data[arm_part]['points']
            if len(arm_points) >= 3:
                # Draw arm as curved line
                pygame.draw.lines(self.screen, (0, 0, 0), False, arm_points, 3)
        
        # Draw legs
        for leg_part in [BodyPart.LEG_LEFT, BodyPart.LEG_RIGHT]:
            leg_points = human_data[leg_part]['points']
            if len(leg_points) >= 3:
                # Draw leg as curved line
                pygame.draw.lines(self.screen, (0, 0, 0), False, leg_points, 3)
    
    def draw_house(self, house_data, style="modern"):
        """Draw the generated house"""
        if not house_data:
            return
        
        # Draw foundation
        foundation_points = house_data[HousePart.FOUNDATION]['points']
        pygame.draw.polygon(self.screen, (100, 100, 100), foundation_points)
        pygame.draw.lines(self.screen, (0, 0, 0), True, foundation_points, 2)
        
        # Draw walls
        wall_points = house_data[HousePart.WALLS]['points']
        wall_color = random.choice(self.house_palette['walls'])
        pygame.draw.polygon(self.screen, wall_color, wall_points)
        pygame.draw.lines(self.screen, (0, 0, 0), True, wall_points, 2)
        
        # Draw roof
        roof_points = house_data[HousePart.ROOF]['points']
        roof_color = random.choice(self.house_palette['roof'])
        pygame.draw.polygon(self.screen, roof_color, roof_points)
        pygame.draw.lines(self.screen, (0, 0, 0), True, roof_points, 2)
        
        # Draw door
        door_points = house_data[HousePart.DOOR]['points']
        door_color = random.choice(self.house_palette['door'])
        pygame.draw.polygon(self.screen, door_color, door_points)
        pygame.draw.lines(self.screen, (0, 0, 0), True, door_points, 2)
        
        # Draw door handle
        door_center = house_data[HousePart.DOOR]['center']
        pygame.draw.circle(self.screen, (200, 200, 0), 
                          (int(door_center[0] + door_points[1][0] - door_points[0][0]) // 4, 
                           int(door_center[1])), 3)
        
        # Draw windows
        windows = house_data[HousePart.WINDOWS]['windows']
        window_color = random.choice(self.house_palette['windows'])
        
        for window_points in windows:
            pygame.draw.polygon(self.screen, window_color, window_points)
            pygame.draw.lines(self.screen, (0, 0, 0), True, window_points, 2)
            
            # Window cross
            center_x = (window_points[0][0] + window_points[1][0]) / 2
            center_y = (window_points[0][1] + window_points[2][1]) / 2
            
            pygame.draw.line(self.screen, (0, 0, 0),
                            (center_x, window_points[0][1]),
                            (center_x, window_points[2][1]), 1)
            pygame.draw.line(self.screen, (0, 0, 0),
                            (window_points[0][0], center_y),
                            (window_points[1][0], center_y), 1)
        
        # Draw chimney if exists
        if HousePart.CHIMNEY in house_data:
            chimney_points = house_data[HousePart.CHIMNEY]['points']
            chimney_color = (80, 80, 80)
            pygame.draw.polygon(self.screen, chimney_color, chimney_points)
            pygame.draw.lines(self.screen, (0, 0, 0), True, chimney_points, 2)
    
    def create_scene(self, human_config=None, house_config=None):
        """Create a complete scene with human and house"""
        if human_config is None:
            human_config = HumanConfig()
        
        if house_config is None:
            house_config = HouseConfig()
        
        # Generate both
        human = self.generate_human(human_config)
        house = self.generate_house(house_config)
        
        return human, house
    
    def save_scene(self, filename="algorithmic_scene.json"):
        """Save the current scene configuration"""
        if self.current_human and self.current_house:
            scene_data = {
                'human': {
                    str(k.value): v for k, v in self.current_human.items()
                },
                'house': {
                    str(k.value): v for k, v in self.current_house.items()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            print(f"Scene saved to {filename}")
    
    def run(self):
        """Main loop"""
        running = True
        
        # Create initial scene
        human_config = HumanConfig(
            height=random.uniform(0.8, 1.2),
            posture=random.uniform(0.3, 0.9),
            movement=random.uniform(0.0, 0.5),
            style=random.choice(["realistic", "stylized", "abstract"])
        )
        
        house_config = HouseConfig(
            width=random.uniform(0.8, 1.5),
            height=random.uniform(0.8, 1.2),
            roof_type=random.choice(["gable", "flat", "hip", "mansard"]),
            stories=random.randint(1, 3),
            symmetry=random.uniform(0.7, 1.0),
            style=random.choice(["modern", "traditional", "cottage"])
        )
        
        self.create_scene(human_config, house_config)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Generate new random scene
                        human_config = HumanConfig(
                            height=random.uniform(0.8, 1.2),
                            posture=random.uniform(0.3, 0.9),
                            movement=random.uniform(0.0, 0.5),
                            style=random.choice(["realistic", "stylized", "abstract"])
                        )
                        
                        house_config = HouseConfig(
                            width=random.uniform(0.8, 1.5),
                            height=random.uniform(0.8, 1.2),
                            roof_type=random.choice(["gable", "flat", "hip", "mansard"]),
                            stories=random.randint(1, 3),
                            symmetry=random.uniform(0.7, 1.0),
                            style=random.choice(["modern", "traditional", "cottage"])
                        )
                        
                        self.create_scene(human_config, house_config)
                    
                    elif event.key == pygame.K_s:
                        # Save scene
                        self.save_scene()
                    
                    elif event.key == pygame.K_h:
                        # Change human posture
                        if self.current_human:
                            human_config.posture = random.uniform(0.3, 0.9)
                            human_config.movement = random.uniform(0.0, 0.5)
                            self.generate_human(human_config)
                    
                    elif event.key == pygame.K_r:
                        # Change house roof
                        if self.current_house:
                            house_config.roof_type = random.choice(["gable", "flat", "hip", "mansard"])
                            self.generate_house(house_config)
            
            # Clear screen
            self.screen.fill((240, 240, 235))
            
            # Draw ground
            pygame.draw.rect(self.screen, (200, 220, 180), 
                            (0, self.height * 0.7, self.width, self.height * 0.3))
            
            # Draw sky
            for i in range(10):
                y = random.randint(0, int(self.height * 0.7))
                x = random.randint(0, self.width)
                size = random.randint(20, 60)
                alpha = random.randint(30, 80)
                cloud_color = (255, 255, 255, alpha)
                
                # Simple cloud circles
                for j in range(3):
                    offset_x = random.randint(-10, 10)
                    offset_y = random.randint(-5, 5)
                    pygame.draw.circle(self.screen, cloud_color, 
                                      (x + offset_x, y + offset_y), size // 2)
            
            # Draw house
            self.draw_house(self.current_house)
            
            # Draw human
            self.draw_human(self.current_human)
            
            # Draw instructions
            instructions = [
                "SPACE: Generate new scene",
                "S: Save scene to JSON",
                "H: Change human posture",
                "R: Change house roof type",
                "ESC: Quit"
            ]
            
            for i, instruction in enumerate(instructions):
                text = self.font.render(instruction, True, (0, 0, 0))
                self.screen.blit(text, (10, 10 + i * 25))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Additional algorithmic generation functions
def generate_parametric_human(age=30, gender="neutral", activity="standing"):
    """Generate human parameters based on characteristics"""
    config = HumanConfig()
    
    # Adjust based on age
    if age < 18:
        config.height = 0.7 + (age / 18) * 0.5
        config.posture = 0.9  # Children stand straighter
    elif age > 60:
        config.height = 0.9
        config.posture = 0.4  # Older people may slump more
    else:
        config.height = 1.0
    
    # Adjust based on gender
    if gender == "male":
        config.proportions['shoulder_width'] = 0.25
        config.proportions['hip_width'] = 0.12
    elif gender == "female":
        config.proportions['shoulder_width'] = 0.18
        config.proportions['hip_width'] = 0.18
    
    # Adjust based on activity
    if activity == "walking":
        config.movement = 0.3
    elif activity == "running":
        config.movement = 0.7
    elif activity == "sitting":
        config.posture = 0.2
        config.proportions['leg_length'] = 0.3
    
    return config

def generate_parametric_house(style="family", size="medium", location="suburban"):
    """Generate house parameters based on characteristics"""
    config = HouseConfig()
    
    if style == "cottage":
        config.width = 0.9
        config.height = 0.8
        config.roof_type = "gable"
        config.stories = 1
        config.symmetry = 0.6
    elif style == "modern":
        config.width = 1.2
        config.height = 0.9
        config.roof_type = "flat"
        config.stories = 2
        config.symmetry = 0.9
    elif style == "mansion":
        config.width = 1.8
        config.height = 1.3
        config.roof_type = "mansard"
        config.stories = 3
        config.symmetry = 0.95
    
    if size == "small":
        config.width *= 0.7
        config.height *= 0.7
    elif size == "large":
        config.width *= 1.3
        config.height *= 1.3
    
    if location == "urban":
        config.window_count = 8
        config.symmetry = 0.8
    elif location == "rural":
        config.window_count = 4
        config.symmetry = 0.5
    
    return config

def create_story_scene(story_text):
    """Create scene based on story description"""
    # Simple NLP for scene generation
    story_lower = story_text.lower()
    
    human_config = HumanConfig()
    house_config = HouseConfig()
    
    # Analyze story for human characteristics
    if "old" in story_lower:
        human_config = generate_parametric_human(age=70)
    elif "child" in story_lower or "young" in story_lower:
        human_config = generate_parametric_human(age=10)
    else:
        human_config = generate_parametric_human(age=30)
    
    if "walking" in story_lower:
        human_config.movement = 0.3
    if "running" in story_lower:
        human_config.movement = 0.7
    if "tired" in story_lower or "sad" in story_lower:
        human_config.posture = 0.3
    
    # Analyze story for house characteristics
    if "cottage" in story_lower or "small" in story_lower:
        house_config = generate_parametric_house(style="cottage", size="small")
    elif "mansion" in story_lower or "big" in story_lower:
        house_config = generate_parametric_house(style="mansion", size="large")
    elif "modern" in story_lower:
        house_config = generate_parametric_house(style="modern")
    
    if "dark" in story_lower or "scary" in story_lower:
        house_config.roof_type = "hip"
        house_config.symmetry = 0.4
    
    return human_config, house_config

# Command line interface
def main():
    print("=" * 60)
    print("ALGORITHMIC HUMAN & HOUSE GENERATOR")
    print("=" * 60)
    print("\nGenerating organic forms through mathematics...")
    
    # Create and run the artist
    artist = AlgorithmicArtist()
    
    print("\nControls:")
    print("  SPACE - Generate new random scene")
    print("  S     - Save current scene to JSON")
    print("  H     - Change human posture/movement")
    print("  R     - Change house roof type")
    print("  ESC   - Quit")
    print("\nStarting visualization...")
    
    artist.run()

if __name__ == "__main__":
    main()