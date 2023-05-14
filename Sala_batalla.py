from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import os
os.environ['multiprocessing.spawn'] = 'False'
import multiprocessing

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30

class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [5, SIZE[Y]//2]
            #self.bullets_0 = manager.list()
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
            #self.bullets_1 = manager.list() 
        #self.bullets = [Bullet(self.pos)]
    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0
         
    #def shoot(self):
    #    for i in self.bullets:
    #        i.update
        """
        bullets = self.bullets
        bullets.append(Bullet(self.pos))
        self.bullets = bullets
        """
        
        #print (self.bullets[0])
        

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

class Ball():
    def __init__(self, velocity):
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]
        self.velocity = velocity

    def get_pos(self):
        return self.pos

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, side):
        self.bounce(X)
        self.pos[X] += 3*self.velocity[X]
        self.pos[Y] += 3*self.velocity[Y]


    def __str__(self):
        return f"B<{self.pos, self.velocity}>"

class Bullet():
    def __init__(self, side):
        #self.pos= pos
        self.side = side        
        if side == LEFT_PLAYER:
                self.pos = [5, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
        self.velocity = 10
    def get_pos(self):
        return self.pos
    
    def get_side (self):
        return self.side
    
    def moveDown(self, side):
        if side == 0 and self.pos[X] == 5:                
            self.pos[Y] += DELTA
            if self.pos[Y] > SIZE[Y]:
                self.pos[Y] = SIZE[Y]
        elif side == 1 and self.pos[X] == SIZE[X] - 5:
            self.pos[Y] += DELTA
            if self.pos[Y] > SIZE[Y]:
                self.pos[Y] = SIZE[Y]

    def moveUp(self, side): #Cambiamos lo de que la bala vaya recta 
        if side == 0 and self.pos[X] == 5:
            self.pos[Y] -= DELTA
            if self.pos[Y] < 0:
                self.pos[Y] = 0
        elif side == 1 and self.pos[X] == SIZE[X] - 5:
            self.pos[Y] -= DELTA
            if self.pos[Y] < 0:
                self.pos[Y] = 0
            
    def update(self, side):
        if (side == 0):
            self.pos[X] += self.velocity
        else:
            self.pos[X] -= self.velocity
        
    """
    def collide_player(self, side):
        self.bounce(X)
        self.pos[X] += 3*self.velocity[X]
        self.pos[Y] += 3*self.velocity[Y]
    """

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self, manager):
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        self.bullets = manager.list( [Bullet(LEFT_PLAYER), Bullet(RIGHT_PLAYER)] )
        self.ball = manager.list( [ Ball([-2,2]) ] )
        self.score = manager.list( [0,0] )
        self.running = Value('i', 1) 
        self.lock = Lock()
        
    def get_player(self, side):
        return self.players[side]

    def get_ball(self):
        return self.ball[0]

    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0
    """
    def get_lista0 (self):
        return self.lista0
    
    def get_lista1 (self):
        return self.lista1
    """
    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        q = self.bullets[player]
        p.moveUp()
        q.moveUp(player)
        self.players[player] = p
        self.bullets[player] = q
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        q = self.bullets[player]
        p.moveDown()
        q.moveDown(player)
        self.players[player] = p
        self.bullets[player] = q
        self.lock.release()

    def ball_collide(self, player):
        self.lock.acquire()
        ball = self.ball[0]
        ball.collide_player(player)
        self.ball[0] = ball
        self.lock.release()
        
    def bullet_collide(self, player):
        self.lock.acquire()
        score = self.score
        if player == 0:
            score[1] += 1
        else:
            score[0] += 1
        self.score = score
        self.lock.release()
    """
    def bullet_collide(self, player, bullet):
        self.lock.acquire()
        bullet.collide_player(player)
        self.lock.release()
    """
    def shoot (self, player): #Es necesario el manager?? 
        self.lock.acquire()
        p = self.bullets[player]
        p.velocity = 10
        p.update(player)
        self.bullets[player] = p
        self.lock.release()

    def move_bullets (self, player):
        self.lock.acquire()
        p = self.bullets[player]
        q = self.players[player]
        p.update(player)
        pos = p.get_pos()
        pos2 = q.get_pos()
        if player == 0:
            if pos[X] > SIZE[X]:
                p.velocity = 0
                p.pos = pos2
        else:
            if pos[X] < 0:
                p.velocity = 0
                p.pos = pos2   
        self.bullets[player] = p
        self.lock.release()
        
    def get_info(self):
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_ball': self.ball[0].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1,
            'pos_left_bullet': self.bullets[0].get_pos(),
            'pos_right_bullet': self.bullets[1].get_pos()
            #'lista_bullets': self.bullets
        }
        return info
    
    def move_ball(self):
        self.lock.acquire()
        ball = self.ball[0]
        ball.update()
        pos = ball.get_pos()
        if pos[Y]<0 or pos[Y]>SIZE[Y]:
            ball.bounce(Y)
        if pos[X]>SIZE[X]:
            self.score[LEFT_PLAYER] += 1
            ball.bounce(X)
        elif pos[X]<0:
            self.score[RIGHT_PLAYER] += 1
            ball.bounce(X)
        self.ball[0]=ball
        self.lock.release()


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball[0]}:{self.running.value}>"

def player(side, conn, game):
    try:
        dispara_0 = 0
        dispara_1 = 0
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        print('Va a enviaaaaaaar', game.get_info())
        conn.send( (side, game.get_info()) ) #Mandas al jugador la situacion actual y que jugador es 
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                #elif command == "collide":
                    #game.ball_collide(side)
                elif command == "collide_bullet":
                    game.bullet_collide(side)
                elif command == "quit":
                    game.stop()
                elif command == "espace":
                    print ('comprobacion de que recibe que tiene que lanzar la bala')
                    #game.shoot(side)
                    if side == 0:
                        game.shoot(0)
                        dispara_0 = 1
                    else:
                        game.shoot(1)
                        dispara_1 = 1
            #if side == 1:
                #game.move_ball()
            if dispara_0 == 1:
                game.move_bullets(0)
            elif dispara_1 == 1:
                game.move_bullets(1)
                
                
                #game.move_bullets()
            print ('pruebaaa')
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

"""La sala actua como una centralita que manda la informacion actual del juego a ambos 
jugadores es un intermediario"""
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener: #Escuchas por el canal local
            n_player = 0
            players = [None, None]
            game = Game(manager)           
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept() #Aceptas el jugador como interlocutor
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game)) #Ejecutas los player asociando a conn el canal de comunicacion
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)
                
                

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)