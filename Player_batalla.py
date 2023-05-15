from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import multiprocessing

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10

BALL_COLOR = WHITE
BALL_SIZE = 10
FPS = 60


SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Player():
    def __init__(self, side): #Jugador 
        self.side = side #Jugador izq / der
        self.pos = [None, None]
        if side == LEFT_PLAYER: #Inicializamos las posiciones 
            self.pos = [5, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

    
class Bullet():
    def __init__(self, side):
        self.side = side #Bala del jugador izq / der 
        self.pos=[ None, None ]
        if side == 0: #Inicializamos las posiciones 
            self.pos = [5, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
    def get_pos(self):
        return self.pos
    
    def get_side (self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

class Game():
    def __init__(self):  #Inicializamos las componentes del juego 
        self.players = [Player(i) for i in range(2)]
        self.score = [0,0]
        self.bullets = [Bullet(i) for i in range(2)]
        self.running = True

    def get_player(self, side):
        return self.players[side]
    
    def get_bullet(self,side):
        return self.bullets[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)
        
    def set_pos_bullet(self, side, pos):
        self.bullets[side].set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
    
    def update(self, gameinfo): #Informacion de la situacion actual del juego recibida de la sala 
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        self.set_pos_bullet(LEFT_PLAYER, gameinfo['pos_left_bullet'])
        self.set_pos_bullet(RIGHT_PLAYER, gameinfo['pos_right_bullet'])

        
    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"

imagen = pygame.transform.scale(pygame.image.load("player.png"), (54,42)) #Reescalamos la imagen para proporcionarla al tablero 
class Paddle(pygame.sprite.Sprite): #Sprite de la nave 
    def __init__(self, player):
      super().__init__()
      if player.side == 0: #Rotamos las imagenes para que queden enfrentadas 
          self.image = pygame.transform.rotate(imagen, 90) 
      else:
          self.image = pygame.transform.rotate(imagen, 270)
      self.image.set_colorkey(BLACK) 
      self.player = player
      self.rect = self.image.get_rect()
      self.radius = 21 #Radio que pauta las colisiones (mejorando la version rectangular)
      #pygame.draw.circle(self.image, RED, self.rect.center, self.radius) #Referencia del radio que pauta las colisiones 
      self.update()

    def update(self): #Actualizacion de la posicion del jugador 
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    def __str__(self):
        return f"S<{self.player}>"
    
imagen1 = pygame.transform.scale(pygame.image.load("bullet.png"), (7,27)) #Reescalamos la imagen para proporcionarla al tablero 
class BulletSprite (pygame.sprite.Sprite): #Sprite de las balas 
    def __init__ (self, bullet):
        super().__init__()
        if bullet.side == 0: #Rotamos las imagenes para que queden enfrentadas 
            self.image = pygame.transform.rotate(imagen1, 90)
        else:
            self.image = pygame.transform.rotate(imagen1, 270)
        self.image.set_colorkey(BLACK)
        self.bullet = bullet
        self.rect = self.image.get_rect()
        self.update()
        
    def update(self): #Actualizacion de la posicion de la bala 
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    def __str__(self):
        return f"S<{self.bullet}>"

class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        self.bullets= [BulletSprite(self.game.get_bullet(i)) for i in range (2)]
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group() #Creamos un nuevo grupo para las balas 
        for bullet in self.bullets:
            self.all_sprites.add(bullet)
            self.bullets_group.add(bullet)
        for paddle in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    events.append("espace")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
            elif event.type == pygame.QUIT:
                events.append("quit")
        if side == 0: #Si es el jugador izq 
            if pygame.sprite.collide_circle(self.bullets[1], self.paddles[side]): #Si colisiona con la bala del rival 
                events.append("collide_bullet") #Añadimos este evento 
        else: #En caso de ser el jugador der 
            if pygame.sprite.collide_circle(self.bullets[0], self.paddles[side]): #Si colisiona con la bala del rival 
                events.append("collide_bullet") #Añadimos este evento 
        return events


    def refresh(self): #Actualizacion del marcador y los sprites 
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()  #Recibe la informacion 
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo) #La actualiza en su 'game' local 
            display = Display(game) #Representa el juego en su propia ventana 
            while game.is_running():
                events = display.analyze_events(side) #Se registran las acciones realizadas por el jugador 
                for ev in events:
                    conn.send(ev) #Se mandan a la centralita 
                    if ev == 'quit': #Si alguno de los eventos te dice que pares 
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv() #Vuelve a recibir la informacion actual de la centralita
                game.update(gameinfo) #La actualiza en su juego local
                display.refresh() #Actualiza el display
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
