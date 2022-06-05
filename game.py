import pygame
from random import randint
from math import atan2, degrees, pi
from datetime import datetime
import pytmx
import pyscroll

pygame.init() 

window = pygame.display.set_mode((800,800)) # fenetre de taille : 800x800
pygame.display.set_caption("My Game")

# Pour tout les objets avec lesquelles on peut interagir 
canInteract = False # si le joueur est a porte de l'objet

# initialiser les variables qui vont permettre de switcher d'une animation a l'autre
anim=0
compteur = 0 # permet de ralentir le changement d'animation par rapport au clock.tick

walk_speed = 1.5
sprint_speed = 2.75

# *** texte des personnage avec lesquelles on peut interagir
text_pancarte = pygame.image.load("assets/panneau.png") # fenetre pr interaction avec le pnj
text_sorcier = pygame.image.load("assets/wizardboard.png")
text_villageoise = pygame.image.load("assets/villageoise_board.png")
gameFinished = pygame.image.load("assets/gameFinished.png") # afficher l'image de fin pancarte vous avez gagne ....

# Player dict
Player= {'PlayerImage':pygame.image.load('assets/player.png'),
 'InitPlayerPosition':(200,790),
  'SpriteSheetPlayerPosition':(0,0), # represente la position sur la sprite sheet de l'image que l'on va prendre.
  'PlayerRect': pygame.Rect(100,400,32,32),
  'PlayerItems': 0}

# Monster dict
Monster = {'MonsterImage':pygame.transform.scale(pygame.image.load("assets/alien.png"), (64,64)),
 'MonsterPosition': (568,241),
 'MonsterRect': pygame.Rect(568,241,64,64),
 'MonsterThere': False,
 'Battu': False }

#Items dict 
Items={'casque':False,
    'plastron': False,
    'jambiere':True,
    'gantelet': False}

loot= [True,True,True,True] # ces booleens vont nous permettre de ne pas looter plusieurs fois le meme coffre/personne, ce serait trop facil
# ces booleens refere au fait qu'ils sont "lootables" ou non


# Barre de vie du joueur
health = 100
degats = 0

# barre de vie du monstre
Monster_health = 220



# mettre en place les projectiles, les bullets, et collisions
projectile = []
arc = []
bullets = []


def get_player_image(x,y): # x and y represent the position of the player image on the spritesheet (.png file)
    global image, Player
    image = pygame.Surface([32, 32]) #permet de definir la taille de l'image qu'on va couper du sprite sheet
    image.blit(Player['PlayerImage'], (0,0), (x, y, 32,32)) # x,y sont les coordoones de l'image
    return image



def draw():
    global player,window, Monster, projectile, throw_time, calqueGroupe, health, armure, degats, Monster_health, loop
    player = get_player_image(Player['SpriteSheetPlayerPosition'][0],Player['SpriteSheetPlayerPosition'][1])
    window.fill((0,0,0))
    #on affiche la tileMap
    calqueGroupe.draw(window)
    DrawHUD()
    checkforInteraction()
    window.blit(player, (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1]))
    pygame.draw.rect(window,(0,0,255),Player['PlayerRect'], 2) # on dessine la hitbox du Player
    pygame.draw.line(window,(255,255,255),Player['InitPlayerPosition'],(mousePosition[0],mousePosition[1]), width=1) # essayer de reduire la taille de la ligne
    

     # Le joueur ne peut pas depasser les limites de l'ecran
    if Player['InitPlayerPosition'][0] < 0:
        Player['InitPlayerPosition'] = (0, Player['InitPlayerPosition'][1])
        
    if Player['InitPlayerPosition'][0] > (800-Player['PlayerRect'].width):
        Player['InitPlayerPosition'] = ((800-Player['PlayerRect'].width), Player['InitPlayerPosition'][1])

    if Player['InitPlayerPosition'][1] < 0:
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], 0)
        
    if Player['InitPlayerPosition'][1] > (800-Player['PlayerRect'].height):
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0],(800-Player['PlayerRect'].height))


    
    if Monster['MonsterThere'] == True:
        pygame.draw.rect(window,(0,0,255),Monster['MonsterRect'], 2) # on dessine la hitbox du Monstre
    
    if Monster['MonsterThere'] == True:
        window.blit(Monster['MonsterImage'], (Monster['MonsterPosition'][0], Monster['MonsterPosition'][1]))

    if Monster['MonsterThere'] == True:
        for elt in projectile:
            projectile_rect = pygame.Rect(elt[0]-7, elt[1]-7, 14, 14)
            if elt != (-1,-1):
                pygame.draw.circle(window, (255,255,255), elt, 7) # dessin du projectile --> a modifier par un asset (.png)
                pygame.draw.rect(window,(255,0,0), projectile_rect, 2)
            if elt[1] == 0:
                elt = (-1,-1)
            if pygame.Rect.colliderect(projectile_rect,Player['PlayerRect']):
                if armure > 0:
                    degats -= 2
                else:
                    health = health - 2
                    print(health)
                projectile.remove(elt)

        for elt in arc:
            arc_rect = pygame.Rect(elt[0],elt[1],30,30)
            if elt != (-1,-1):
                pygame.draw.arc(window, (0,0,0), arc_rect, 3*pi/4, 3*pi/2, width=2) # dessin du projectile --> a modifier par un asset (.png)
            if pygame.Rect.colliderect(arc_rect,Player['PlayerRect']):
                if armure > 0:
                    degats -= 4
                    arc.remove(elt)
                else:
                    health = health - 4
                    print(health)
                    arc.remove(elt)
        
        if health <= 0:
            loop = False

        if Monster_health <= 0 :
            Monster['MonsterThere'] = False
            Monster['Battu'] = True

                
                    
         

    
    for elt in range(len(bullets)):
        bullets_rect = pygame.Rect(bullets[elt][0]-7, bullets[elt][1]-7, 14, 14)
        if bullets[elt] != (-1,-1) :
            pygame.draw.circle(window, (255,0,0), bullets[elt], 7)
            pygame.draw.rect(window,(0,0,255), bullets_rect, 2)
        if pygame.Rect.colliderect(bullets_rect,Monster['MonsterRect']):
            Monster_health = Monster_health -4
            bullets[elt] = (-1,-1) 

    pygame.display.flip()


def get_input():
    global keyPressed, anim, speed, projectile, IsProjectile, Player, canInteract, Monster, mousePosition, bullet_cooldown
    keyPressed = pygame.key.get_pressed()
    #  *** Gerer le spawn du projectile
    if Monster['MonsterThere'] == True: # afin que les projectiles ne s'accumulent pas tout dans la liste et ne soit pas envoyer tous d'un coup, on evite un bug
        if projectile_cooldown % tick == 0:
            projectile.append((Monster['MonsterPosition'][0]+32, Monster['MonsterPosition'][1]+32))
        if projectile_cooldown % (3*tick) == 0:
            arc.append((Monster['MonsterPosition'][0]+32, Monster['MonsterPosition'][1]+32))
        
        # gerer le input des Bullets
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN  and bullet_cooldown / (1.25*tick) >= 1:
                mousePosition = pygame.mouse.get_pos()
                bullets.append((Player['InitPlayerPosition'][0] + 8,Player['InitPlayerPosition'][1] + 8))
                bullet_cooldown = 0

    # *** Gerer le mouvement et changement d'animation du personnage

    Player['PlayerRect'].x = Player['InitPlayerPosition'][0]
    Player['PlayerRect'].y = Player['InitPlayerPosition'][1]

    if keyPressed[pygame.K_w] == True :
        if keyPressed[pygame.K_LSHIFT]== True: # LSHIFT touche de sprint -- augmente la vitesse de deplacement
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] - sprint_speed) # change la PP du Player pour le mouvement
              
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] - walk_speed)
        Player['SpriteSheetPlayerPosition'] = (anim,0)

        

    elif keyPressed[pygame.K_s] == True:
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] + sprint_speed)
            
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], Player['InitPlayerPosition'][1] + walk_speed)
        Player['SpriteSheetPlayerPosition'] = ((64+anim),0)

    elif keyPressed[pygame.K_d] == True:
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]+sprint_speed, Player['InitPlayerPosition'][1])
 
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]+walk_speed, Player['InitPlayerPosition'][1])
        Player['SpriteSheetPlayerPosition'] = ((64+anim),32)

    elif keyPressed[pygame.K_a] == True:
        if keyPressed[pygame.K_LSHIFT]== True:
            Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]-sprint_speed, Player['InitPlayerPosition'][1])
        
        Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0]-walk_speed, Player['InitPlayerPosition'][1])
        Player['SpriteSheetPlayerPosition'] = (anim,32)





 
def checkCollision(): # pour etablir les collisions entre Player et son environnement
    global collisionObj, Player, window
    collisionObj = [] # liste qui va contenir des dictionnaires
    for obj in tmx_data.objects: # boucle qui va permettre de filtrer entre les differents types d'objets enregistre dans la map
        if obj.type == 'collision' or obj.type == 'collision_chest' or obj.type == 'interaction_pnj':
            #creation d'un tuple qui prend l'objet de type collision et cree un Rect de meme taille et coordonne
            #on fait ca pour le comparer au Player['Rect']
            collisionObj.append( {'obj':obj,'Rect': pygame.Rect(obj.x,obj.y,obj.width,obj.height), 'Name': obj.name, 'Type': obj.type} ) # {'obj':obj, 'Rect':pygame.Rect(obj.x- 10,obj.y - 10,obj.width + 10,obj.height + 10), 'Name': obj.name, 'Text':f" Bonjour je suis {obj.name}"}
    
    
    for obj in collisionObj:
        if pygame.Rect.colliderect(Player['PlayerRect'], obj['Rect']):
           
            # Collision avec un objet cote DROIT (de l'objet)
            if obj['Rect'].right < Player['PlayerRect'].right:
                Player['InitPlayerPosition'] = ((obj['Rect'].right), Player['InitPlayerPosition'][1])

            # Collision avec un objet cote GAUCHE (de l'objet)
            elif obj['Rect'].left > Player['PlayerRect'].left:
                Player['InitPlayerPosition'] = (((obj['Rect'].left- Player['PlayerRect'].width)), Player['InitPlayerPosition'][1])

            # Collision avec un objet cote TOP (de l'objet)
            elif obj['Rect'].top > Player['PlayerRect'].top:
                Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], ((obj['Rect'].y - Player['PlayerRect'].height)))
            
            # Collision avec un objet cote BOTTOM (de l'objet)
            elif obj['Rect'].bottom < Player['PlayerRect'].bottom:
                Player['InitPlayerPosition'] = (Player['InitPlayerPosition'][0], obj['Rect'].bottom)
            
            

            

            
            





def DrawSpeechBubble(speaker): # interaction avec l'environnement.
    image = speaker
    image = pygame.transform.scale(speaker,(500,75))
    window.blit(image,(0,725))
    
    
def checkforInteraction(): # problemes de collision avec la portée de l'interaction (collision des rects), meme prblm qu'avec l'environnement A FIXER
    global interactionObj, canInteract, pathToMap, mapLoaded, tmx_data
    interactionObj = []
    for obj in tmx_data.objects: # boucle qui va permettre de filtrer entre les differents types d'objets enregistre dans la map
        if obj.type == 'interaction_static' or obj.type == 'dungeon_door' or obj.type == 'interaction_pnj' or obj.type == 'collision_chest' :
            #creation d'un tuple qui prend l'objet de type collision et cree un Rect de meme taille et coordonne
            #on fait ca pour le comparer au Player['Rect']
            interactionObj.append( {'obj':obj, 'Rect':pygame.Rect(obj.x- 10,obj.y - 10,(obj.width + 20),(obj.height + 20)), 'Name': obj.name, 'Text':f" Bonjour je suis {obj.name}"} )
    
    
    for pnj in interactionObj:
        if pnj['Rect'].colliderect(Player['PlayerRect']) :
            pygame.draw.rect(window, (255,0,0), pnj['Rect'], 2)
            pygame.display.flip()
            canInteract = True
            if pnj['obj'].name == 'wizard dungeon' :
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    DrawSpeechBubble(text_sorcier)

            if pnj['obj'].name == 'pancarte' :
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    DrawSpeechBubble(text_pancarte)

            if pnj['obj'].name == 'villageoise' :
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    DrawSpeechBubble(text_villageoise)
            
            if pnj['obj'].name == 'chest1' and loot[0] == True : # choisir un item parmis 4 disponible # verifie si le coffre est lootable
                 # c'est possible de looter deux fois le meme objets, effet de n'avoir rien loot.
                item = randint(0,3)
                liste_items = ['casque','plastron','jambiere','gantelet']
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    Items[liste_items[item]] = True 
                    print(liste_items[item])
                    loot[0] = False

            if pnj['obj'].name == 'chest2' and loot[1] == True : # choisir un item parmis 4 disponible # verifie si le coffre est lootable
                # c'est possible de looter deux fois le meme objets, effet de n'avoir rien loot.
                item = randint(0,3)
                liste_items = ['casque','plastron','jambiere','gantelet']
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    Items[liste_items[item]] = True 
                    loot[1] = False
                



            if pnj['obj'].type == 'dungeon_door':
                if keyPressed[pygame.K_e] == True and canInteract == True:
                    mapLoaded = False
                    pathToMap = 'tilesetTMX\\dungeon.tmx'
                    Monster['MonsterThere'] = True
                    
        canInteract = False

def DrawHUD():
    # *** HUD DU MONSTRE
    if Monster['MonsterThere'] == True:
        rect_health_monstre = pygame.Rect(280,750,Monster_health,20) # barre de vie variable
        pygame.draw.rect(window,(0,0,0),pygame.Rect(270,740,230,40)) # cadre noir de la barre de vie du Player
        pygame.draw.rect(window,(255,0,0),rect_health_monstre) # on dessine la barre de vie


    # *** HUD DU PLAYER
    rect_health = pygame.Rect(35,20,health,20) # barre de vie variable
    rect_armure = pygame.Rect((35,40),(armure,20)) # barre d'armure --> en fonction du nombre d'items du Player
    pygame.draw.rect(window,(0,0,0),pygame.Rect(30,15,110,30)) # cadre noir de la barre de vie du Player
    pygame.draw.rect(window,(0,0,0),pygame.Rect(30,45,110,30)) # cadre noir de la barre d'armure du Player
    pygame.draw.rect(window,(255,0,0),rect_health) # on dessine la barre de vie
    pygame.draw.rect(window,(0,0,255),rect_armure) # on dessine la barre d'armure

    # on affiche le nombre de pv restant
    font = pygame.font.SysFont(None,30) # fontName / fontSize
    text_health = font.render(f'{health}', True, (255,0,0)) # need to add color
    # on affiche le nombre d'armure restant
    text_armure = font.render(f'{armure}', True, (0,0,255)) # need to add color
    
    window.blit(text_health, (150,15))
    window.blit(text_armure, (150,45))




    lines = 0
    rect_inventaire = pygame.Rect(200,-1,400,50)
    pygame.draw.rect(window,(0,0,0), rect_inventaire)
    for i in range(4):
        pygame.draw.line(window, (255,255,255), (300+lines,0),(300+lines,50), width=2)
        lines = lines + 100
    if Items['casque'] == True:
        casque = pygame.transform.scale(pygame.image.load("assets\\heavy-helm.png"),(50,50))
        window.blit(casque,(rect_inventaire.x + 25, rect_inventaire.y))
    if Items['gantelet'] == True:
        casque = pygame.transform.scale(pygame.image.load("assets\\gauntlet.png"),(50,50))
        window.blit(casque,(rect_inventaire.x + 125, rect_inventaire.y))
    if Items['jambiere'] == True:
        casque = pygame.transform.scale(pygame.image.load("assets\\leg-armor.png"),(50,50))
        window.blit(casque,(rect_inventaire.x + 225, rect_inventaire.y))
    if Items['plastron'] == True:
        casque = pygame.transform.scale(pygame.image.load("assets\\abdominal-armor.png"),(50,50))
        window.blit(casque,(rect_inventaire.x + 325, rect_inventaire.y))


def EndGame():
    global pathToMap, mapLoaded
    DrawSpeechBubble(gameFinished)
    pygame.display.flip()
    pygame.time.wait(5000)
    pathToMap = 'tilesetTMX\\spawn_map.tmx' # on renvoi le joueur a la map initial
    mapLoaded = False # on refait passer le booleen a False pour reconfigurer la map.
    


loop = True
# on definit le tick rate
clock = pygame.time.Clock()
tick = 50
projectile_cooldown = 0
bullet_cooldown = 0
mapLoaded = False
pathToMap = 'tilesetTMX\\spawn_map.tmx'
while loop == True:
    
    # A utiliser pour plus tard : pygame.time.wait(nMilliseconds)

    clock.tick(tick) # rafraichissement

    # nous donne un tuple(x,y)
    mousePosition = pygame.mouse.get_pos() # permet de viser l'ennemi pour tirer les projectiles.
    
    
    

    # Ce bloc de code nous permet de pouvoir generer une map selon la condition ou le stade du jeu.
    if mapLoaded == False:
        # charger la map
        tmx_data = pytmx.load_pygame(pathToMap)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, window.get_size())

        # dessiner le groupe de calque 
        calqueGroupe = pyscroll.PyscrollGroup(map_layer)
        mapLoaded = True # permet d'enregistrer une map dans calqueGroupe et de bloquer la re-creation de la map
        # jusqu'a qu'on change de map et que mapLoaded repasse a False, qui fait le process a nouveau
    
    
    if Monster['MonsterThere'] == True:
        bullet_cooldown += 1
        projectile_cooldown += 1

    IsProjectile = randint(0,10) # nombre choisi pr determiner si le projectile doit etre lancer --- But etant de tirer aleatoirement des projectiles  
    compteur += 1

    if compteur % 5 == 0:
        if anim == 0:
            anim = 32
        elif anim == 32:
            anim = 0

    

    
    for i in Items:
        if Items[i] == True:
            Player['PlayerItems'] += 1
    
    # barre d'armure 
    armure = 25*Player['PlayerItems']+degats # on loot des items, donc on peut augmenter en arumure,elle n;est pas fixe des l'initialisation
    # on appelle les fonctions
    
    get_input()
    checkCollision()
    draw()
    checkforInteraction()
    
    #Player['PlayerItems'] = 0 # l'image s'est cree, PlayerItems a influence lexecution, on le re-assigne a 0 pour traiter l'image suivante
    Player['PlayerItems'] = 0
    

    # definition de la distance x et y entre le monstre et le joueur 
    dx = ((Player['InitPlayerPosition'][0] - 16)-Monster['MonsterPosition'][0])
    dy = ((Player['InitPlayerPosition'][1]-16)-Monster['MonsterPosition'][1])
    VectorMonsterPlayer = (dx , dy)

    ballspeedX = dx / 15 
    ballspeedY = dy / 15
    ballspeed = (ballspeedX,ballspeedY)


    for elt in projectile:    # Premiere boucle qui fait bouger les projectiles
        projectemp = (elt[0] + ballspeed[0], elt[1] + ballspeed[1]) # deplacement du projectile vers sa cible # l_speed[i-1][0] == ballspeedX #
        projectile.remove(elt)
        projectile.insert(0,projectemp)

    for elt in projectile:
        if elt[1]<0 or elt[0] < 0 or elt[1] > 800 or elt[0] > 800:
            projectile.remove(elt)

    # defintion de la distance a parcourir entre le Player et le monstre
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


    # definition de la distance a parcourir entre l'arc et le Player
    arcspeedX = dx / 35
    arcspeedY = dy / 35
    arcspeed = (arcspeedX,arcspeedY)


    for elt in arc:    # Premiere boucle qui fait bouger les projectiles
        arctemp = (elt[0] + arcspeed[0], elt[1] + arcspeed[1]) # deplacement du projectile vers sa cible # l_speed[i-1][0] == ballspeedX #
        arc.remove(elt)
        arc.insert(0,arctemp)

    for elt in arc:
        if elt[1]<0 or elt[0] < 0 or elt[1] > 800 or elt[0] > 800:
            arc.remove(elt)
    
    if Monster['Battu'] == True:
        EndGame()
        Monster['Battu'] = False


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
            
    # fin de la boucle 

pygame.quit()