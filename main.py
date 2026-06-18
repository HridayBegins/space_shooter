import pygame
import random
import json
import os
import sys

pygame.init()
pygame.mixer.init()  # ADDED — initialize sound mixer

# SCREEN
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()

WHITE=(255,255,255)
GRAY=(170,170,170)
BLACK=(0,0,0)

font=pygame.font.SysFont(None,60)
small_font=pygame.font.SysFont(None,35)

# LOAD ASSETS
def load_image(path,size):

    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img,size)
    return img

player_img = load_image("assets/player.png",(80,80))
enemy_img = load_image("assets/enemy.png",(70,70))
bullet_img = load_image("assets/bullet.png",(15,35))
background = load_image("assets/background.png",(WIDTH,HEIGHT))

# ADDED — Load sound effects
shoot_sound = pygame.mixer.Sound(os.path.join("assets", "shoot.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join("assets", "explosion.wav"))
shoot_sound.set_volume(0.5)       # Optional: adjust volume (0.0 to 1.0)
explosion_sound.set_volume(0.6)   # Optional: adjust volume

# SCORE FILE
FILE="scores.json"

if not os.path.exists(FILE):

    with open(FILE,"w") as f:

        json.dump({
            "Player1":0,
            "Player2":0,
            "Player3":0
        },f)

def load_scores():

    with open(FILE,"r") as f:
        return json.load(f)

def save_scores(data):

    with open(FILE,"w") as f:
        json.dump(data,f)

scores=load_scores()
current_player=None

# BUTTON
def button(text,x,y):

    rect=pygame.Rect(x,y,350,70)

    pygame.draw.rect(screen,GRAY,rect)

    label=font.render(text,True,BLACK)

    screen.blit(label,(x+175-label.get_width()/2,y+15))

    return rect

# START MENU
def start_menu():

    global current_player

    while True:

        screen.blit(background,(0,0))

        title=font.render("SPACE SHOOTER",True,WHITE)

        screen.blit(title,(WIDTH/2-title.get_width()/2,100))

        p1=button("PLAYER 1",WIDTH/2-175,260)
        p2=button("PLAYER 2",WIDTH/2-175,350)
        p3=button("PLAYER 3",WIDTH/2-175,440)
        quitb=button("QUIT",WIDTH/2-175,560)

        h1=small_font.render("Highscore: "+str(scores["Player1"]),True,WHITE)
        h2=small_font.render("Highscore: "+str(scores["Player2"]),True,WHITE)
        h3=small_font.render("Highscore: "+str(scores["Player3"]),True,WHITE)

        screen.blit(h1,(WIDTH/2+220,280))
        screen.blit(h2,(WIDTH/2+220,370))
        screen.blit(h3,(WIDTH/2+220,460))

        pygame.display.update()

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type==pygame.MOUSEBUTTONDOWN:

                mx,my=pygame.mouse.get_pos()

                if p1.collidepoint(mx,my):

                    current_player="Player1"
                    game()

                if p2.collidepoint(mx,my):

                    current_player="Player2"
                    game()

                if p3.collidepoint(mx,my):

                    current_player="Player3"
                    game()

                if quitb.collidepoint(mx,my):

                    pygame.quit()
                    sys.exit()

# GAME OVER
def game_over(score):

    global scores,current_player

    if score>scores[current_player]:

        scores[current_player]=score
        save_scores(scores)

    while True:

        screen.blit(background,(0,0))

        over=font.render("GAME OVER",True,WHITE)
        screen.blit(over,(WIDTH/2-over.get_width()/2,200))

        sc=small_font.render("Score: "+str(score),True,WHITE)
        screen.blit(sc,(WIDTH/2-sc.get_width()/2,300))

        restart=button("RESTART",WIDTH/2-175,420)
        menu=button("MAIN MENU",WIDTH/2-175,510)

        pygame.display.update()

        for event in pygame.event.get():

            if event.type==pygame.MOUSEBUTTONDOWN:

                mx,my=pygame.mouse.get_pos()

                if restart.collidepoint(mx,my):
                    game()

                if menu.collidepoint(mx,my):
                    start_menu()

# PAUSE
def pause_menu():

    while True:

        screen.blit(background,(0,0))

        label=font.render("PAUSED",True,WHITE)
        screen.blit(label,(WIDTH/2-label.get_width()/2,200))

        resume=button("RESUME",WIDTH/2-175,350)
        menu=button("MAIN MENU",WIDTH/2-175,440)

        pygame.display.update()

        for event in pygame.event.get():

            if event.type==pygame.MOUSEBUTTONDOWN:

                mx,my=pygame.mouse.get_pos()

                if resume.collidepoint(mx,my):
                    return

                if menu.collidepoint(mx,my):
                    start_menu()

# GAME
def game():

    player=pygame.Rect(WIDTH//2,HEIGHT-120,80,80)

    bullets=[]
    enemies=[]

    score=0
    spawn=0

    while True:

        clock.tick(60)

        spawn+=1

        if spawn>45:

            enemy=pygame.Rect(random.randint(0,WIDTH-70),-70,70,70)
            enemies.append(enemy)

            spawn=0

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                quit()

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_SPACE:

                    bullet=pygame.Rect(player.x+32,player.y,15,35)
                    bullets.append(bullet)
                    shoot_sound.play()  # ADDED — play shoot sound

                if event.key==pygame.K_ESCAPE:
                    pause_menu()

        keys=pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.x-=7
        if keys[pygame.K_d]:
            player.x+=7
        if keys[pygame.K_w]:
            player.y-=7
        if keys[pygame.K_s]:
            player.y+=7

        for bullet in bullets:
            bullet.y-=12

        for enemy in enemies:
            enemy.y+=6

        for enemy in enemies[:]:  # MODIFIED — iterate over copy to safely remove

            for bullet in bullets[:]:  # MODIFIED — iterate over copy to safely remove

                if enemy.colliderect(bullet):

                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    explosion_sound.play()  # ADDED — play explosion sound

                    score+=1
                    break

        for enemy in enemies:

            if enemy.colliderect(player):
                game_over(score)

        screen.blit(background,(0,0))

        screen.blit(player_img,(player.x,player.y))

        for bullet in bullets:
            screen.blit(bullet_img,(bullet.x,bullet.y))

        for enemy in enemies:
            screen.blit(enemy_img,(enemy.x,enemy.y))

        txt=small_font.render("Score: "+str(score),True,WHITE)
        screen.blit(txt,(20,60))

        pygame.display.update()

start_menu()