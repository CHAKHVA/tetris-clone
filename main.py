import pygame
from piece import Piece
from settings import *
from random import choice, randint

class Game:
    def __init__(self, surface, font, max_score):
        # Initializing
        self.surface = surface

        # Setting up clock
        self.clock = pygame.time.Clock()


        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.lines_after_level_up = 0
        self.level = 1
        self.multiplier = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.max_score = max_score

        self.font = font
        self.lines_text = self.font.render('LINES ' + str(self.lines), False, WHITE)
        self.score_text = self.font.render('SCORE', False, WHITE)
        self.score_number = self.font.render(str(self.score), False, WHITE)
        self.max_score_textt = self.font.render('MAX SCORE', False, WHITE)
        self.max_score_text = self.font.render(self.max_score, False, WHITE)
        self.next_text = self.font.render('NEXT', False, WHITE)
        self.level_text = self.font.render('LEVEL ' + str(self.level), False, WHITE)

        # Piece Setup
        self.pieces = []
        self.create_piece(first=True)
        self.next = 0

        # Audio
        self.background_music = pygame.mixer.Sound('audio/tetris_theme.ogg')
        self.background_music.set_volume(0.1)
        self.background_music.play(loops = -1)
        self.clear_sound = pygame.mixer.Sound('audio/clear.ogg')
        self.clear_sound.set_volume(0.7)
    
    def valid(self):
        for sprite in self.current_piece.sprites():
            if sprite.rect.x < 0 or sprite.rect.x >= WIDTH:
                return False
        for piece in self.pieces:
            if pygame.sprite.groupcollide(piece, self.current_piece, False, False):
                return False
        return True
    
    def draw_next_piece(self, shape):
        self.next_shape = pygame.sprite.Group()
        for row_index, row in enumerate(shape):
            for col_index, col in enumerate(row):
                if col == '1' or col == '2':
                    x = (col_index + COLS + 2) * TILE_SIZE - 30
                    y = (row_index + 10) * TILE_SIZE + 10
                    self.next_shape.add(Piece(self.next_color, x, y, False))
        self.next_shape.draw(self.surface)

    def create_piece(self, first=False):
        if first:
            self.color = choice(COLORS)
            self.shape_name = choice(SHAPE_NAMES)
            self.shape_type = SHAPES[self.shape_name]
            self.current_rotation = randint(0, len(self.shape_type) - 1)
            self.current_shape = self.shape_type[self.current_rotation]
        else:
            self.color = self.next_color
            self.shape_name = self.next_shape_name
            self.shape_type = self.next_shape_type
            self.current_rotation = self.next_current_rotation
            self.current_shape = self.next_current_shape
        
        self.next_color = choice(COLORS)
        self.next_shape_name = choice(SHAPE_NAMES)
        self.next_shape_type = SHAPES[self.next_shape_name]
        self.next_current_rotation = randint(0, len(self.next_shape_type) - 1)
        self.next_current_shape = self.next_shape_type[self.next_current_rotation]

        self.current_piece = pygame.sprite.Group()
        for row_index, row in enumerate(self.current_shape):
            for col_index, col in enumerate(row):
                if col == '1' or col == '2':
                    self.grid[int(row_index)][int(col_index + COLS / 2 - 2)] = 1
                    x = (col_index + COLS / 2 - 2) * TILE_SIZE
                    y = (row_index - 2) * TILE_SIZE
                    if col == '1':
                        self.current_piece.add(Piece(self.color, x, y, False))
                    else:
                        self.current_piece.add(Piece(self.color, x, y, True))

    def rotate_piece(self):
        # Remove old piece from the grid
        for sprite in self.current_piece.sprites():
            self.grid[int(sprite.rect.y / TILE_SIZE)][int(sprite.rect.x / TILE_SIZE)] = 0

        # Detect origin point
        for sprite in self.current_piece.sprites():
            if sprite.fixed:
                origin_x = sprite.rect.x
                origin_y = sprite.rect.y
                break
        
        # Rotate piece
        for sprite in self.current_piece.sprites():
            if not sprite.fixed:
                relative_pos_x = sprite.rect.x - origin_x
                relative_pos_y = sprite.rect.y - origin_y
                sprite.rect.x = origin_x - relative_pos_y
                sprite.rect.y = origin_y + relative_pos_x
        
        if not self.valid():
            # Rotate back

            # Detect origin point
            for sprite in self.current_piece.sprites():
                if sprite.fixed:
                    origin_x = sprite.rect.x
                    origin_y = sprite.rect.y
                    break
            
            # Rotate piece
            for sprite in self.current_piece.sprites():
                if not sprite.fixed:
                    relative_pos_x = sprite.rect.x - origin_x
                    relative_pos_y = sprite.rect.y - origin_y
                    sprite.rect.x = origin_x + relative_pos_y
                    sprite.rect.y = origin_y - relative_pos_x

        # Add rotated piece to the grid
        for sprite in self.current_piece.sprites():
            self.grid[int(sprite.rect.y / TILE_SIZE)][int(sprite.rect.x / TILE_SIZE)] = 1

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.shape_name != 'O':
                        self.rotate_piece()
            
            self.surface.fill(BLACK)

            # Draw old pieces
            if len(self.pieces) != 0:
                for piece in self.pieces:
                    piece.draw(self.surface)

            # Check for collisions
            can_move_down = True
            can_move_left = True
            can_move_right = True
            for sprite in self.current_piece.sprites():
                down_rect_copy = sprite.rect.copy()
                left_rect_copy = sprite.rect.copy()
                right_rect_copy = sprite.rect.copy()

                down_rect_copy.y += 1
                left_rect_copy.x -= 1
                right_rect_copy.x += 1

                down_sprite_copy = pygame.sprite.Sprite()
                down_sprite_copy.rect = down_rect_copy

                left_sprite_copy = pygame.sprite.Sprite()
                left_sprite_copy.rect = left_rect_copy

                right_sprite_copy = pygame.sprite.Sprite()
                right_sprite_copy.rect = right_rect_copy

                for piece in self.pieces:
                    if pygame.sprite.spritecollide(down_sprite_copy, piece, False) and can_move_down == True:
                        can_move_down = False
                        # down_sprite_copy.kill()
                        # down_sprite_copy = None
                        # if not (can_move_left and can_move_right):
                        #     break

                    if pygame.sprite.spritecollide(left_sprite_copy, piece, False) and can_move_left == True:
                        can_move_left = False
                        # left_sprite_copy.kill()
                        # left_sprite_copy = None
                        # if not (can_move_down and can_move_right):
                        #     break
                    
                    if pygame.sprite.spritecollide(right_sprite_copy, piece, False) and can_move_right == True:
                        can_move_right = False
                        # right_sprite_copy.kill()
                        # right_sprite_copy = None
                        # if not (can_move_down and can_move_left):
                        #     break

                if sprite.rect.bottom + TILE_SIZE > HEIGHT and can_move_down == True:
                    can_move_down = False
                if sprite.rect.right + TILE_SIZE > WIDTH and can_move_right == True:
                    can_move_right = False
                if sprite.rect.left - TILE_SIZE < 0 and can_move_left == True:
                    can_move_left = False

            # Update droping piece
            self.current_piece.update(can_move_down, can_move_left, can_move_right)
            self.current_piece.draw(self.surface)

            # Update grid
            self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            for piece in self.pieces:
                for sprite in piece.sprites():
                    self.grid[int(sprite.rect.y / TILE_SIZE)][int(sprite.rect.x / TILE_SIZE)] = 1

            for sprite in self.current_piece.sprites():
                self.grid[int(sprite.rect.y / TILE_SIZE)][int(sprite.rect.x / TILE_SIZE)] = 1


            # Create new piece
            if self.next == 5:
                # Clear rows
                rows_to_clear = []
                for i in range(ROWS):
                    row_checker = True
                    for j in range(COLS):
                        if self.grid[i][j] == 0:
                            row_checker = False
                            break
                    if row_checker:
                        rows_to_clear.append(i * TILE_SIZE)

                rows_to_clear.sort()
                for piece in self.pieces:
                    for sprite in piece.sprites():
                        if sprite.rect.y in rows_to_clear:
                            sprite.kill()
                for sprite in self.current_piece.sprites():
                    if sprite.rect.y in rows_to_clear:
                        sprite.kill()
                
                if len(rows_to_clear):
                    self.clear_sound.play()
                    self.lines += len(rows_to_clear)
                    self.lines_after_level_up += len(rows_to_clear)
                    self.score += self.multiplier[len(rows_to_clear)] * self.level

                if self.lines_after_level_up >= self.level * 10:
                    self.level += 1
                    self.lines_after_level_up = 0
                    for sprite in self.current_piece.sprites():
                        if sprite.fall_delay != 4:
                            sprite.fall_delay -= 2
                            sprite.down_delay = sprite.fall_delay / 2
                
                # Adjust rows
                for row in rows_to_clear:
                    for piece in self.pieces:
                        for sprite in piece.sprites():
                            if sprite.rect.y <= row:
                                sprite.rect.y += TILE_SIZE
                    for sprite in self.current_piece.sprites():
                        if sprite.rect.y <= row:
                            sprite.rect.y += TILE_SIZE

                # Check lose
                for sprite in self.current_piece.sprites():
                    if sprite.rect.y <= 0:
                        running = False
                
                # Create next piece
                self.next = False
                self.pieces.append(self.current_piece)
                self.create_piece()

            elif not can_move_down:
                self.next += 1
            
            # Draw stats
            self.lines_text = None
            self.score_text = None
            self.next_text = None
            self.level_text = None
            self.lines_text = self.font.render('LINES ' + str(self.lines), False, WHITE)
            self.score_text = self.font.render('SCORE', False, WHITE)
            self.score_number = self.font.render(str(self.score), False, WHITE)
            self.next_text = self.font.render('NEXT', False, WHITE)
            self.level_text = self.font.render('LEVEL ' + str(self.level), False, WHITE)
            pygame.draw.line(self.surface, WHITE, (WIDTH, 0), (WIDTH, HEIGHT))
            self.surface.blit(self.lines_text, (WIDTH + 50, 50))
            self.surface.blit(self.score_text, (WIDTH + 50, 100))
            self.surface.blit(self.score_number, (WIDTH + 50, 125))
            self.surface.blit(self.max_score_textt, (WIDTH + 50, 175))
            self.surface.blit(self.max_score_text, (WIDTH + 50, 200))
            self.surface.blit(self.next_text, (WIDTH + 50, 300))
            self.surface.blit(self.level_text, (WIDTH + 50, 500))
            self.draw_next_piece(self.next_current_shape)
            
            pygame.display.update()

        if int(self.max_score) < self.score:
            return str(self.score)
        return self.max_score

def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH + 280, HEIGHT))
    pygame.display.set_caption(NAME)
    font = pygame.font.Font('fonts/atari.ttf', 20)
    max_score = ''
    press_key = font.render('Press Any Key To Play', False, WHITE)
    run = True
    while run:
        surface.fill(BLACK)
        surface.blit(press_key, ((WIDTH + 280) // 2 - press_key.get_rect().width // 2, HEIGHT // 2 - press_key.get_rect().height // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                with open('max_score.txt', 'r') as f:
                    max_score = f.read()
                game = Game(surface, font, max_score)
                file = open('max_score.txt', 'w')
                file.write(game.run())
                file.close()
                game.background_music.fadeout(1000)
    pygame.quit()


if __name__ == '__main__':
    main_menu()
