import pygame
import math

# Set-up
pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('./assets/font/myFont.ttf', 32) #freesansbold.ttf
big_font = pygame.font.Font('./assets/font/myFont.ttf', 60)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Duck Hunter in Python!')
icon = pygame.image.load('assets/targets/1/3.png')
pygame.display.set_icon(icon)
level = 0
points = 0
shot = False
total_shots = 0
ammo = 0
mode = 0
time_passed = 0
time_left = 0

menu = True
game_over = False
pause = False
menu_img = pygame.image.load('assets/menus/mainMenu.png')
game_over_img = pygame.image.load('assets/menus/gameOver.png')
pause_img = pygame.image.load('assets/menus/pause.png')
clicked = False
write_values = False

bgs = []
banners = []
guns = []
levels = []
target_images = [[], [], []]
targets = {
    1: [10, 5, 3],
    2: [12, 8, 5],
    3: [15, 12, 8, 3]
}

# Read scores
file = open('high_scores.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_time = int(read_file[2])

# Sounds
#pygame.mixer.init()
#pygame.mixer.music.load('assets/sounds/bg_music.mp3')
#plate_sound = pygame.mixer.Sound('assets/sounds/Broken plates.wav')
#plate_sound.set_volume(.2)
#bird_sound = pygame.mixer.Sound('assets/sounds/Drill Gear.wav')
#bird_sound.set_volume(.2)
#laser_sound = pygame.mixer.Sound('assets/sounds/Laser Gun.wav')
#laser_sound.set_volume(.3)
#pygame.mixer.music.play()

# Populate from assets
for i in range(1, 4):
    bgs.append(pygame.image.load(f'assets/bgs/{i}.png'))
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (100, 100)))

    if i < 3:
        for j in range(1, 4):
            target_images[i-1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120-j*18, 80-j*12)
            ))
    else: 
        for j in range(1, 5):
            target_images[i-1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120-j*18, 80-j*12)
            ))

# Initialize enemy coordinates
def init_coords():
    one_coords = [[], [], []]
    two_coords = [[], [], []]
    three_coords = [[], [], [], []]

    for i in range(3):
        my_list = targets[1]
        for j in range(my_list[i]):
            one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
    for i in range(3):
        my_list = targets[2]
        for j in range(my_list[i]):
            two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
    for i in range(4):
        my_list = targets[3]
        for j in range(my_list[i]):
            three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
    
    return [one_coords, two_coords, three_coords]

[one_coords, two_coords, three_coords] = init_coords()

# Gun mechanics
def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH/2, HEIGHT - 200)
    lasers = ['red', 'purple', 'green']
    clicks = pygame.mouse.get_pressed()

    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = -100000

    angle = math.atan(slope)
    rotation = math.degrees(angle)

    if mouse_pos[0] < WIDTH/2:
        gun = pygame.transform.flip(guns[level-1], True, False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90-rotation), (WIDTH/2-90, HEIGHT-250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level-1], mouse_pos, 5)
    else:
        gun = guns[level-1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270-rotation), (WIDTH/2-30, HEIGHT-250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level-1], mouse_pos, 5)

def check_shot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    
    for i in range (len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + (10 * (i**2))
                
                #if level == 1:
                #    bird_sound.play()
                #elif level == 2:
                #    plate_sound.play()
                #elif level == 3:
                #    laser_sound.play()
                
    return coords

# Add enemies to level
def draw_level(coords):
    if level == 3:
        target_rects = [[], [], [], []]
    else:
        target_rects = [[], [], []]

    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect(
                (coords[i][j][0]+20, coords[i][j][1]), (60-i*12, 60-i*12)
                ))
            screen.blit(target_images[level-1][i], coords[i][j])
    
    return target_rects

def move_level(coords):
    if level == 3:
        max_val = 4
    else:
        max_val = 3

    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2**i, my_coords[1])
    
    return coords

# Scoring
def draw_score():
    points_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(points_text, (320, 660))
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (320, 687))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (320, 714))

    if mode == 0:
        mode_text = font.render('Freeplay!', True, 'black')
    elif mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
    elif mode == 2:
        mode_text = font.render(f'Time remaining: {time_left}', True, 'black')

    screen.blit(mode_text, (320, 741))

# Resets
def reset_game():
    global points, time_passed, total_shots, level, ammo, time_left, one_coords, two_coords, three_coords
    level = 1
    time_passed = 0
    total_shots = 0
    points = 0
    
    if mode == 1:
        ammo = 81
    elif mode == 2:
        time_left = 45

    [one_coords, two_coords, three_coords] = init_coords()

def reset_points():
    global best_freeplay, best_ammo, best_time, write_values
    best_freeplay = 0
    best_ammo = 0
    best_time = 0
    write_values = True

# Updates
def update_scores():
    global write_values, best_ammo, best_time, best_freeplay
    if mode == 0:
        if time_passed < best_freeplay or best_freeplay == 0:
            best_freeplay = time_passed
            write_values = True
    elif mode == 1:
        if points > best_ammo:
            best_ammo = points
            write_values = True
    elif mode == 2:
        if points > best_time:
            best_time = points
            write_values = True

# Screens
def draw_menu():
    #pygame.mixer.music.play()
    global game_over, pause, mode, menu, clicked
    game_over = False
    pause = False
    screen.blit(menu_img, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (340, 580))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 580))
    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    screen.blit(font.render(f'{best_time}', True, 'black'), (350, 710))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))

    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        mode = 0
        reset_game()
        menu = False
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        mode = 1
        reset_game()
        menu = False
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        mode = 2
        reset_game()
        menu = False
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        reset_points()

def draw_pause():
    global level, menu, pause, clicked
    screen.blit(pause_img, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))

    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = resume_level
        pause = False
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        menu = True
        pause = False
        
def draw_game_over():
    global level, menu, game_over, running, clicked
    screen.blit(game_over_img, (0, 0))

    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    
    screen.blit(big_font.render(f'{display_score}', True, 'black'), (650, 570))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100)) 

    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        running = False
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        menu = True
        game_over = False

# Game loop
running = True
counter = 1

while running:
    timer.tick(fps)
    if level != 0:    
        if counter < 60:
            counter+=1
        else:
            counter = 1
            time_passed+=1
            if mode == 2:
                time_left-=1

    screen.fill('black')
    screen.blit(bgs[level-1], (0,0))
    screen.blit(banners[level-1], (0, HEIGHT-200))

    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        update_scores()
        draw_game_over()
    if pause:
        level = 0
        draw_pause() 

    if level > 0:
        draw_gun()
        draw_score()

    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT-200):
                shot = True
                total_shots+=1
                if mode == 1:
                    ammo-=1
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):
                clicked = True
                resume_level = level
                pause = True
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                clicked = True
                menu = True
                [one_coords, two_coords, three_coords] = init_coords()
            
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level+=1
        elif target_boxes == [[], [], [], []]:
            game_over = True

    if mode == 1 and ammo == 0:
        game_over = True
    if mode == 2 and time_left == 0:
        game_over = True

    if write_values:
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_time}')
        file.close()
        write_values = False
    
    pygame.display.flip()

pygame.quit()