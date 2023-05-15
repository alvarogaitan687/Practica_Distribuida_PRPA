from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import multiprocessing

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30

class Player(): #Jugador 
    def __init__(self, side):
        self.side = side #Lado del jugador (izq/der)
        if side == LEFT_PLAYER: #Inicializamos las posiciones
            self.pos = [5, SIZE[Y]//2] 
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
    
    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):  
        self.pos[Y] += DELTA  #Movemos hacia abajo
        if self.pos[Y] > SIZE[Y]: #Si nos pasamos del limite superior bloqueamos la nave en esa posicion (para que no se salga de la pantalla)
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA #Movemos hacia arriba 
        if self.pos[Y] < 0:  #Si nos pasamos del limite inferior bloqueamos la nave en esa posicion (para que no se salga de la pantalla)
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"


class Bullet():
    def __init__(self, side):
        self.side = side #Lado de la bala (izq/der)   
        if side == LEFT_PLAYER: #Inicializamos las posiciones
                self.pos = [5, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]
        self.velocity = 0 #Inicializamos la velocidad 
        
    def get_pos(self):
        return self.pos
    
    def get_side (self):
        return self.side
    
    def moveDown(self, side):
        if side == 0 and self.pos[X] == 5: #Si es la bala del jugador izq, en caso de estar la bala en la nave se mueve con ella, si no, sigue su recorrido horizontal               
            self.pos[Y] += DELTA
            if self.pos[Y] > SIZE[Y]:
                self.pos[Y] = SIZE[Y]
        elif side == 1 and self.pos[X] == SIZE[X] - 5: #Si es la bala del jugador derecho, de nuevo comprueba si esta en la nave para moverla con ella 
            self.pos[Y] += DELTA
            if self.pos[Y] > SIZE[Y]:
                self.pos[Y] = SIZE[Y]

    def moveUp(self, side): #De igual forma que moveDown
        if side == 0 and self.pos[X] == 5: 
            self.pos[Y] -= DELTA
            if self.pos[Y] < 0:
                self.pos[Y] = 0
        elif side == 1 and self.pos[X] == SIZE[X] - 5:
            self.pos[Y] -= DELTA
            if self.pos[Y] < 0:
                self.pos[Y] = 0
            
    def update(self, side): #Actualizacion de la posicion de la bala 
        if (side == 0): #Si es la bala del jugador izq 
            self.pos[X] += self.velocity #Avanza hacia la derecha 
        else: #Si es la bala del jugador der
            self.pos[X] -= self.velocity #Avanza hacia la izquierda 
            
    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self, manager): #Inicializamos las componentes del juego 
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        self.bullets = manager.list( [Bullet(LEFT_PLAYER), Bullet(RIGHT_PLAYER)] )
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
        
    def moveUp(self, player): #moveUp llamado por un jugador 'player'
        self.lock.acquire()
        p = self.players[player]
        q = self.bullets[player]
        p.moveUp() #Movemos la posicion del jugador 'player'
        q.moveUp(player) #Movemos la posicion de su bala en ese sentido (se movera si se encuentra en la nave)
        self.players[player] = p
        self.bullets[player] = q
        self.lock.release()

    def moveDown(self, player): #De igual forma que moveUp
        self.lock.acquire()
        p = self.players[player]
        q = self.bullets[player]
        p.moveDown()
        q.moveDown(player)
        self.players[player] = p
        self.bullets[player] = q
        self.lock.release()
        
    def bullet_collide(self, player):
        self.lock.acquire()
        score = self.score
        if player == 0: #Si el choque de la bala se produce con el jugador izq
            score[1] += 1 #Sumamos un punto a su rival
        else: #En caso contrario 
            score[0] += 1  #Se lo sumamos a el 
        self.score = score
        self.lock.release()
        
    def shoot (self, player): #Si un jugador 'player' dispara
        self.lock.acquire()
        p = self.bullets[player]
        p.velocity = 20 #Cambia la velocidad de su bala poniendola en movimiento 
        p.update(player)
        self.bullets[player] = p
        self.lock.release()

    def move_bullets (self, player):
        self.lock.acquire()
        p = self.bullets[player]
        q = self.players[player]
        p.update(player)
        pos = p.get_pos()
        pos2 = q.get_pos() #Guardamos la posicion actual del jugador (para recolocar la bala si se sale de la pantalla)
        if player == 0: #Si es la bala izq 
            if pos[X] > SIZE[X]: #Si se sale de la pantalla 
                p.velocity = 0 #Paramos la bala 
                p.pos = pos2 #La recolocamos en la nave 
        else: #Si es la bala der
            if pos[X] < 0:  #Si se sale de la pantalla 
                p.velocity = 0  #Paramos la bala 
                p.pos = pos2  #La recolocamos en la nave 
        self.bullets[player] = p
        self.lock.release()
        
    def get_info(self): #Informacion que se compartirá con los Clients para transmitir el estado actual del juego 
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1,
            'pos_left_bullet': self.bullets[0].get_pos(),
            'pos_right_bullet': self.bullets[1].get_pos()
        }
        return info


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball[0]}:{self.running.value}>"

def player(side, conn, game):
    try:
        #dispara_0 = 0
        #dispara_1 = 0
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) ) #Mandas a los Clients la situacion actual y que jugador es 
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv() #Recibe la informacion de los Clients para actualizar el juego 
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "collide_bullet":
                    game.bullet_collide(side)
                elif command == "quit":
                    game.stop()
                elif command == "espace":
                    if side == 0: #Si dispara el jugador izq
                        game.shoot(0) #Disparamos 
                        #dispara_0 = 1 #Pasamos a mover 
                    else: #Si dispara el jugador der 
                        game.shoot(1) #Disparamos 
                        #dispara_1 = 1
            #if dispara_0 == 1:
            game.move_bullets(0)
            #elif dispara_1 == 1:
            game.move_bullets(1)
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

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
                conn = listener.accept() 
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game)) #Ejecutas los jugadores asociando a conn el canal de comunicacion
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