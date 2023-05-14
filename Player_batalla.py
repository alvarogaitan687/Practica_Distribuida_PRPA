
from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
os.environ['multiprocessing.spawn'] = 'False'
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
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]
        if side == LEFT_PLAYER:
            self.pos = [5, SIZE[Y]//2]
            #self.bullets_0 = []
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
            #self.bullets_1 =[]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"
 
class Ball():
    def __init__(self):
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"
    
class Bullet():
    def __init__(self, side):
        self.side = side
        self.pos=[ None, None ]
        if side == 0:
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
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ball = Ball()
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


    def get_ball(self):
        return self.ball
    
    #def get_lista_bullets(self, i):
    #    return self.lista_bullets[i]
    
    
    def set_ball_pos(self, pos):
        self.ball.set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
    
    #def set_lista_bullets (self, lista_0):
    #    self.lista_bullets = lista_0
    
    
    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos(gameinfo['pos_ball'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        self.set_pos_bullet(LEFT_PLAYER, gameinfo['pos_left_bullet'])
        self.set_pos_bullet(RIGHT_PLAYER, gameinfo['pos_right_bullet'])
        #self.set_lista_bullets (gameinfo['lista_bullets'])

        
    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)#drawing the paddle
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        print('ESTO ES EL SELF.PLAYER antes de donde tiene el otro el error', self.player)
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos
    def __str__(self):
        return f"S<{self.player}>"
    
class BulletSprite (pygame.sprite.Sprite):
    def __init__ (self, bullet):
        super().__init__()
        self.image = pygame.Surface([40, 10])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)#drawing the paddle
        self.bullet = bullet
        #print('generator error ', self.bullet)
        color = PLAYER_COLOR[self.bullet.get_side()]
        pygame.draw.rect(self.image, color, [0,0,40, 10])
        self.rect = self.image.get_rect()
        self.update()
        """
        super().__init__()
        self.bullet =bullet
        self.image = pygame.Surface ((10,20))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, YELLOW, [0, 0, 10, 20])
        self.rect = self.image.get_rect()
        self.update()
        """
        
    def update(self):
        print ('Esto es self.bullet antes del error', self.bullet)
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        #print (pos)
    def __str__(self):
        return f"S<{self.bullet}>"
        
class BallSprite(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):        
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos


class Display():
    def __init__(self, game):
        self.game = game
        #print('PRIIIIIIIIINT', self.game.get_player(0))
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        #print('PRIIIIINT', self.paddles)
        self.ball = BallSprite(self.game.get_ball())
        #print('PRIIIIIIIIINT', self.game.get_bullet(0))

        self.bullets= [BulletSprite(self.game.get_bullet(i)) for i in range (2)]
        #print('PRIIIIINT', self.bullets)
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group() #Creamos un nuevo grupo para las balas 
        #self.bullets_1_group = pygame.sprite.Group() #Creamos un nuevo grupo para las balas 
        for bullet in self.bullets:
            self.all_sprites.add(bullet)
            self.bullets_group.add(bullet)
        for paddle in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        #self.all_sprites.add(self.ball)
        #self.all_sprites.add(self.bullet)

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
        if pygame.sprite.collide_rect(self.ball, self.paddles[side]):
            events.append("collide")
        if side == 0:
            if pygame.sprite.collide_rect(self.bullets[1], self.paddles[side]):
                events.append("collide_bullet")
        else:
            if pygame.sprite.collide_rect(self.bullets[0], self.paddles[side]):
                events.append("collide_bullet")
        return events


    def refresh(self):
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

"""Cada jugador actua como un cliente que recibe la informacion de la centralita para saber 
la situacion actual y realiza acciones que se modifican en la representacion local
y se lo manda a la centralita para modificar la informacion"""
def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            print('HOLA DE NUEVOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
            #multiprocessing.current_process().authkey = b'secret password'
            side,gameinfo = conn.recv()  #Recibe la informacion 
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo) #La actualiza en su 'game' local 
            display = Display(game) #Representa el juego en su propia ventana 
            print('prueba1')
            while game.is_running():
                events = display.analyze_events(side) #Se registran las acciones realizadas por el jugador 
                for ev in events:
                    conn.send(ev) #Se mandan a la centralita 
                    print('prueba2')
                    if ev == 'quit': #Si alguno de los eventos te dice que pares 
                        game.stop()
                conn.send("next")
                print('prueba3')
                gameinfo = conn.recv() #Vuelve a recibir la informacion actual de la centralita
                print ('prueba4')
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
