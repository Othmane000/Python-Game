import pygame, csv
from random import randint
from math import atan2, degrees
from datetime import datetime
import pytmx
import pyscroll




pygame.init() 



window = pygame.display.set_mode((800,800)) # fenetre de taille : 800x800
pygame.display.set_caption("PyGame - Pokemon")



# Pour tout les objets avec lesquelles on peut interagir 
canInteract = False # si le joueur est a porte de l'objet

# initialiser les variables qui vont permettre de switcher d'une animation a l'autre
anim=0
compteur = 0 # permet de ralentir le changement d'animation par rapport au clock.tick

walk_speed = 1.5
sprint_speed = 3.75
direction = 0 # Droite : 1 ; Bas : 2 ; Gauche = 3 ; Haut : 4

# jump
jump = False
vel_y = 10

startgame_time = datetime.now()
delta_time = [startgame_time] # initialiser la boucle avec le temps a laquelle elle a ete cree

# Player dict
Player= {'PlayerImage':pygame.image.load('1620294984-you.png'),
 'InitPlayerPosition':(100,400),
  'SpriteSheetPlayerPosition':(0,0),
  'PlayerRect': pygame.Rect(100,400,32,32)}

# Monster dict
Monster = {'MonsterImage':pygame.transform.scale(pygame.image.load("alien.png"), (64,64)),
 'MonsterPosition': (568,241),
 'MonsterRect': pygame.Rect(568,241,64,64) }

# Barre de vie du joueur
health = 100





# mettre en place les projectiles, les bullets, et collisions
projectile = [(Monster['MonsterPosition'][0]+32, Monster['MonsterPosition'][1]+32)]
mousePosition = (0,0) # afin de pouvoir viser les monstres
bullets = []
walls = []



def get_player_image(x,y): # x and y represent the position of the player image on the spritesheet (.png file)
    global image, Player
    image = pygame.Surface([32, 32]) #permet de definir la taille de l'image qu'on va couper du sprite sheet
    image.blit(Player['PlayerImage'], (0,0), (x, y, 32,32)) # x,y sont les coordoones de l'image
    return image



def draw():
    global player,window, Monster, projectile, throw_time, calqueGroupe, health
    player = get_player_image(Player['SpriteSheetPlayerPosition'][0],Player['SpriteSheetPlayerPosition'][1])
    #player = pygame.transform.scale(player,(64,64)) # permet de modifier la taille du personnage a l'echelle
    window.fill((0,0,0))
    #on affiche la tileMap
    calqueGroupe.draw(window)
    window.blit(player, (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1]))
    pygame.draw.rect(window,(0,0,255),Player['PlayerRect'], 2) # on dessine la hitbox du Player
    pygame.draw.rect(window,(0,0,255),Monster['MonsterRect'], 2) # on dessine la hitbox du Monstre
    pygame.draw.rect(window,(0,0,0),pygame.Rect(30,15,110,30)) # on dessine le fond cadre de la barre de vie
    pygame.draw.rect(window,(255,0,0),pygame.Rect(35,20,health,20)) # on dessine la barre de vie
    #print(f"{[Player['PlayerRect'].x, Player['PlayerRect'].y, Player['PlayerRect'].width, Player['PlayerRect'].height]}")
    window.blit(Monster['MonsterImage'], (Monster['MonsterPosition'][0], Monster['MonsterPosition'][1]))

    for elt in projectile:
        projectile_rect = pygame.Rect(elt[0]-7, elt[1]-7, 14, 14)
        if elt != (-1,-1):
            pygame.draw.circle(window, (255,255,255), elt, 7) # dessin du projectile --> a modifier par un asset (.png)
            pygame.draw.rect(window,(255,0,0), projectile_rect, 2)
        if elt[1] == 0:
            elt = (-1,-1)
        if pygame.Rect.colliderect(projectile_rect,Player['PlayerRect']):
            health = health - 2
            print(health)
            print("Projectile WHITE removed")
            projectile.remove(elt)
         

    
    for elt in range(len(bullets)):
        bullets_rect = pygame.Rect(bullets[elt][0]-7, bullets[elt][1]-7, 14, 14)
        if bullets[elt] != (-1,-1) :
            pygame.draw.circle(window, (255,0,0), bullets[elt], 7)
            pygame.draw.rect(window,(0,0,255), bullets_rect, 2)
        if pygame.Rect.colliderect(bullets_rect,Monster['MonsterRect']):
            print("Projectile RED removed.")
            bullets[elt] = (-1,-1) 

    pygame.display.flip()


def get_input():
    global keyPressed, anim, speed, direction, projectile, IsProjectile, delta_time, Player, canInteract, Monster
    keyPressed = pygame.key.get_pressed()
    #  *** Gerer le spawn du projectile
    if tick_compteur // 25 == 3 and tick_compteur % 25 == 0: # (datetime.now() - delta_time[0]).total_seconds() >=0.75
        projectile.append((Monster['MonsterPosition'][0]+32, Monster['MonsterPosition'][1]+32))
        throw_time = datetime.now() # enregistre le temps au moment de l'ajout du projectile dans la liste de projectile a lancer
        delta_time.insert(0,throw_time) # ajoute ce temps a la liste de temps pour comparer le temps entre le dernier lancer et celui demander
        
    # gerer le input des Bullets
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousePosition = pygame.mouse.get_pos()
            bullets.append((Player['InitPlayerPosition'][0] + 8,Player['InitPlayerPosition'][1] + 8))

    # *** Gerer le mouvement et changement d'animation du personnage

    Player['PlayerRect'].x = Player['InitPlayerPosition'][0]
    Player['PlayerRect'].y = Player['InitPlayerPosition'][1]

    if keyPressed[pygame.K_w] == True :
        direction = 4
        if keyPressed[pygame.K_LSHIFT]== True: # LSHIFT touche de sprint -- augmente la vitesse de deplacement
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] - sprint_speed) # change la PP du Player pour le mouvement
              
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] - walk_speed)
        #Player['PlayerRect'].y = Player['PlayerRect'].y - 5
        Player['SpriteSheetPlayerPosition'] = (anim,96)

        

    elif keyPressed[pygame.K_s] == True:
        direction = 2
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] + sprint_speed)
            
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] + walk_speed)
        #Player['PlayerRect'].y = Player['PlayerRect'].y + 5
        Player['SpriteSheetPlayerPosition'] = (anim,0)

    elif keyPressed[pygame.K_d] == True:
        direction = 1
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]+sprint_speed, Player['InitPlayerPosition'][1])
 
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]+walk_speed, Player['InitPlayerPosition'][1])
        #Player['PlayerRect'].x = Player['PlayerRect'].x + 5
        Player['SpriteSheetPlayerPosition'] = (anim,64)

    elif keyPressed[pygame.K_a] == True:
        direction = 3
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]-sprint_speed, Player['InitPlayerPosition'][1])
        
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]-walk_speed, Player['InitPlayerPosition'][1])
        #Player['PlayerRect'].x = Player['PlayerRect'].x - 5
        Player['SpriteSheetPlayerPosition'] = (anim,32)

    if keyPressed[pygame.K_e] == True and canInteract == True: # need to add dialogState == True so the player doesnt trigger interaction if he isnt close to a pnj
        DrawSpeechBubble('Hello this is a test', 'ADMIN')




 
def checkCollision(): # pour etablir les collisions entre Player et son environnement
    global collisionObj, Player, window
    collisionObj = []
    for obj in tmx_data.objects: # boucle qui va permettre de filtrer entre les differents types d'objets enregistre dans la map
        if obj.type == 'collision':
            #creation d'un tuple qui prend l'objet de type collision et cree un Rect de meme taille et coordonne
            #on fait ca pour le comparer au Player['Rect']
            collisionObj.append( {'obj':obj,'Rect': pygame.Rect(obj.x,obj.y,obj.width,obj.height), 'Name': obj.name, 'Type': obj.type} ) # {'obj':obj, 'Rect':pygame.Rect(obj.x- 10,obj.y - 10,obj.width + 10,obj.height + 10), 'Name': obj.name, 'Text':f" Bonjour je suis {obj.name}"}
    
    
    for obj in collisionObj:
        if pygame.Rect.colliderect(Player['PlayerRect'], obj['Rect']):

            # Collision avec un objet cote DROIT (de l'objet)        
            if direction == 3 and (obj['Rect'].right + obj['Rect'].width)-Player['PlayerRect'].left > 0 and Player['InitPlayerPosition'][0] > obj['Rect'].x: # and (Player['InitPlayerPosition'][0] - (rect[1].x + rect[1].width)) >= 0
                print(f"COLLIDE ON RIGHT SIDE OF THE OBJECT {obj['Name']}")
                pygame.draw.rect(window, (255,0,0), obj['Rect'], 2)
                pygame.display.flip()
                Player['InitPlayerPosition']= (obj['Rect'].x + obj['Rect'].width, Player['InitPlayerPosition'][1])


            # Collision avec un objet cote GAUCHE (de l'objet)
            elif direction == 1 and obj['Rect'].left - Player['PlayerRect'].right < 0 and Player['InitPlayerPosition'][0] < (obj['Rect'].x + obj['Rect'].width): 
                print(f"COLLIDE ON LEFT SIDE OF THE OBJECT {obj['Name']}")
                pygame.draw.rect(window, (255,0,0), obj['Rect'], 2)
                pygame.display.flip()
                Player['InitPlayerPosition']= (obj['Rect'].x - Player['PlayerRect'].width, Player['InitPlayerPosition'][1])
                

            # Collision avec un objet cote BOTTOM (de l'objet)
            elif direction == 4 and (obj['Rect'].bottom - Player['PlayerRect'].top) > 0 and Player['PlayerRect'].y < (obj['Rect'].y + obj['Rect'].height):
                print(f"COLLIDE ON BOTTOM SIDE OF THE OBJECT {obj['Name']}")
                pygame.draw.rect(window, (255,0,0), obj['Rect'], 2)
                pygame.display.flip()
                Player['InitPlayerPosition']= (Player['InitPlayerPosition'][0],obj['Rect'].y + obj['Rect'].height)
    
            # Collision avec un objet cote TOP (de l'objet)
            elif direction == 2 and (obj['Rect'].top - Player['PlayerRect'].bottom) < 0 and (Player['PlayerRect'].y + Player['PlayerRect'].height) > obj['Rect'].y:
                print(f"COLLIDE ON TOP SIDE OF THE OBJECT {obj['Name']}")
                pygame.draw.rect(window, (255,0,0), obj['Rect'], 2)
                pygame.display.flip()
                Player['InitPlayerPosition']= (Player['InitPlayerPosition'][0],obj['Rect'].y - Player['PlayerRect'].height)
            
            
            




def DrawSpeechBubble(text, speaker): # interaction avec l'environnement.
    font = pygame.font.SysFont(None,14) # fontName / fontSize
    text_surface = font.render(f'{speaker} : {text}', True, (0,0,0)) # need to add color

    bg_text = pygame.transform.scale(pygame.image.load('battlestatbox.png'),(500,75))

    window.blit(bg_text, (20,700))
    window.blit(text_surface,(30,710))
    pygame.display.flip()
    
def checkforInteraction(): # problemes de collision avec la portée de l'interaction (collision des rects), meme prblm qu'avec l'environnement A FIXER
    global interactionObj, canInteract, pathToMap, mapLoaded
    interactionObj = []
    for obj in tmx_data.objects: # boucle qui va permettre de filtrer entre les differents types d'objets enregistre dans la map
        
        if obj.type == 'interaction_static' or obj.type == 'interaction_pnj' or obj.type == 'door' :
            #creation d'un tuple qui prend l'objet de type collision et cree un Rect de meme taille et coordonne
            #on fait ca pour le comparer au Player['Rect']
            interactionObj.append( {'obj':obj, 'Rect':pygame.Rect(obj.x- 10,obj.y - 10,obj.width + 10,obj.height + 10), 'Name': obj.name, 'Text':f" Bonjour je suis {obj.name}"} )
    
    
    for pnj in interactionObj:
        if pnj['Rect'].colliderect(Player['PlayerRect']) :
            print(interactionObj)
            pygame.draw.rect(window, (255,0,0), pnj['Rect'], 2)
            pygame.display.flip()
            canInteract = True
            if pnj['obj'].type == 'interaction_static' :
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    DrawSpeechBubble(pnj['Text'], pnj['Name'])
            if pnj['obj'].type == 'interaction_pnj':
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    DrawSpeechBubble(pnj['Text'], pnj['Name'])
            if pnj['obj'].type == 'door':
                print("collision with door")
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    mapLoaded = False
                    pathToMap = 'tilesetTMX\\dungeon.tmx'


loop = True
# on definit le tick rate
clock = pygame.time.Clock()
tick_compteur = 0
mapLoaded = False
pathToMap = 'tilesetTMX\\untitled.tmx'
while loop == True:
    clock.tick(60) # meaning it refreshes 25 times a sec --> 1 sec = 25 frames ---- 5 secs = 25 * 5 = 125
    mousePosition = pygame.mouse.get_pos() # permet de viser l'ennemi pour tirer les projectiles.
    
    # Ce bloc de code nous permet de pouvoir generer une map selon la condition ou le stade du jeu.
    if mapLoaded == False:
        # charger la map
        tmx_data = pytmx.load_pygame(pathToMap)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, window.get_size())

        # dessiner le groupe de calque 
        calqueGroupe = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=3)
        mapLoaded = True
    
    



    tick_compteur += 1
    if tick_compteur == 100:
        tick_compteur = 0

    IsProjectile = randint(0,10) # nombre choisi pr determiner si le projectile doit etre lancer --- But etant de tirer aleatoirement des projectiles  
    compteur += 1

    if compteur % 5 == 0:
        if anim == 0:
            anim = 64
        elif anim == 64:
            anim = 0

    # definition de la distance x et y entre le monstre et le joueur 
    dx = (Player['InitPlayerPosition'][0]-Monster['MonsterPosition'][0])
    dy = (Player['InitPlayerPosition'][1]-Monster['MonsterPosition'][1])
    

    # definition de l'angle entre le monstre et le joueur
    angle = atan2(dy,dx) # on definit l'angle en radiant d'abord
    angle = degrees(angle) # transforme les radians en degres
    VectorMonsterPlayer = (dx , dy)

    ballspeedX = dx / 10 
    ballspeedY = dy / 10
    ballspeed = (ballspeedX,ballspeedY)

        
    # on appelle les fonctions
    get_input()
    checkCollision()
    draw()
    checkforInteraction()
    
    for elt in projectile:    # Premiere boucle qui fait bouger les projectiles
        projectemp = (elt[0] + ballspeed[0], elt[1] + ballspeed[1]) # deplacement du projectile vers sa cible # l_speed[i-1][0] == ballspeedX #
        #print(l_dx[elt],l_dy[elt])
        projectile.remove(elt)
        projectile.insert(0,projectemp)

    for elt in projectile:
        if elt[1]<0 or elt[0] < 0 or elt[1] > 800 or elt[0] > 800:
            projectile.remove(elt)


    bulletspeedx = (mousePosition[0]-Player['InitPlayerPosition'][0]) / 10
    bulletspeedy = (mousePosition[1]-Player['InitPlayerPosition'][1]) / 10

    for elt in bullets:
        if elt != (-1,-1):
            bullettemp = (elt[0] + bulletspeedx, elt[1] + bulletspeedy) # a remplacer par difference entrre mouseposition et playerposition
            bullets.remove(elt)
            bullets.insert(0,bullettemp)
    for elt in bullets:
        if elt[1]<0 or elt[0] < 0 or elt[1] > 800 or elt[0] > 800:
            bullets.remove(elt)


    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
            
    # fin de la boucle 

pygame.quit()