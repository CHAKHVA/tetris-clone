import pygame
from settings import *


class Piece(pygame.sprite.Sprite):
    def __init__(self, color, x, y, fixed=False):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(f'assets/{color}.png').convert(), (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.fixed = fixed

        # Speed
        self.fall_speed = TILE_SIZE
        self.fall_delay = 16
        self.fall_frame_counter = self.fall_delay - 1
        self.side_delay = 10
        self.side_frame_counter = self.side_delay
        self.down_delay = self.fall_delay // 2
        self.down_frame_counter = self.down_delay
    
    def move(self, can_move_down):
        if can_move_down and not self.stop_move:
            self.rect.y += self.fall_speed
    
    def event_handler(self, can_move_down, can_move_left, can_move_right):
        keys = pygame.key.get_pressed()
        self.stop_move = False
        if keys[pygame.K_RIGHT] and can_move_right:
            self.rect.x += TILE_SIZE
            self.side_frame_counter = 0
        elif keys[pygame.K_LEFT] and can_move_left:
            self.rect.x -= TILE_SIZE
            self.side_frame_counter = 0
        elif keys[pygame.K_DOWN] and can_move_down and self.down_frame_counter == self.down_delay:
            self.rect.y += self.fall_speed
            self.stop_move = True
            self.down_frame_counter = 0

    def update(self, can_move_down, can_move_left, can_move_right):
        self.fall_frame_counter += 1
        if self.side_frame_counter != self.side_delay:
            self.side_frame_counter += 1
        if self.down_frame_counter != self.down_delay:
            self.down_frame_counter += 1

        if self.side_frame_counter == self.side_delay:
            self.event_handler(can_move_down, can_move_left, can_move_right)

        if self.fall_frame_counter == self.fall_delay:
            self.move(can_move_down)
            self.fall_frame_counter = 0
        
