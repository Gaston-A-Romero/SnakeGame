import pygame 
import random 
from enum import Enum
from collections import namedtuple
pygame.init()

#Variables constantes

ancho_ventana = 800
alto_ventana = 800
#cada cuadricula sera de un tamaño de 10 por lo que se podran dar 80*60 
bloque_size = 40


letra = pygame.font.Font(None, 25)

#Colores en rgb
BLANCO = (255,255,255)
NEGRO = (0,0,0)
VERDE = (0,255,0)
VERDE2 = (10,200,10)
ROJO = (255,0,0)

#Asocia a cada direccion un valor determinado para proteger contra errores de tipeo
class Direccion(Enum):
    DERECHA = 1
    IZQUIERDA = 2
    ARRIBA = 3
    ABAJO = 4

#Contra errores de tipeo
Coordenada = namedtuple("Coordenada", 'x, y')

class JuegoSerpiente:
    def __init__(self,ancho_ventana,alto_ventana):
        self.ancho_ventana = ancho_ventana
        self.alto_ventana = alto_ventana

        #Iniciar la ventana
        self.display = pygame.display.set_mode((self.ancho_ventana,self.alto_ventana))
        pygame.display.set_caption("Juego de la Serpiente")
        self.clock = pygame.time.Clock()

        #Inicio la serpiente para que vaya hacia la derecha y defino su bloque que cambiara la direccion(cabeza) y el cuerpo con el tamaño definido
        self.direccion = Direccion.DERECHA
        self.cabeza_serpiente = Coordenada(self.ancho_ventana/2,self.alto_ventana/2)
        self.cuerpo_serpiente = [self.cabeza_serpiente , Coordenada( (self.cabeza_serpiente.x - bloque_size) , (self.cabeza_serpiente.y)),
        Coordenada(self.cabeza_serpiente.x - (2 * bloque_size) , self.cabeza_serpiente.y)]

        #Puntaje, cuando colisione con la comida se le tendra que sumar 1
        self.puntaje = 0
        #Inicializo la comida
        self.comida = None
        #Utilizo una funcion de ayuda
        self._poner_comida()

        self.velocidad_clock = 10

    def _poner_comida(self):
        #Hay que poner comida en una posicion al azar que este dentro de los límites de la pantalla
        x = random.randint(0, (self.ancho_ventana-bloque_size)//bloque_size)*bloque_size
        y = random.randint(0, (self.alto_ventana-bloque_size)//bloque_size)*bloque_size
        self.comida = Coordenada(x,y)
        #Controlo que la comida no se ponga en alguna coordenada donde se encuentra la serpiente, si lo hace vuelvo a llamar a la funcion con recursion
        if self.comida in self.cuerpo_serpiente:
            self._poner_comida()

    def actualizar(self):
        
        #Mirar los inputs del usuario
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                perder = True
            #Si presiona una tecla defino la nueva direccion que puede tomar 
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and self.direccion != Direccion.DERECHA:
                    self.direccion = Direccion.IZQUIERDA
                elif evento.key == pygame.K_RIGHT and self.direccion != Direccion.IZQUIERDA:
                    self.direccion = Direccion.DERECHA
                elif evento.key == pygame.K_UP and self.direccion != Direccion.ABAJO:
                    self.direccion = Direccion.ARRIBA
                elif evento.key == pygame.K_DOWN and self.direccion != Direccion.ARRIBA:
                    self.direccion = Direccion.ABAJO

                    
        #Mover la serpiente con dichos inputs y cambiar la direccion de la cabeza
        self._mover_serpiente(self.direccion) # ----> Actualiza la serpiente 
        self.cuerpo_serpiente.insert(0, self.cabeza_serpiente)

        #Ver si hay colisiones 
        perder = False
        if self._colision():
            perder = True
            return perder, self.puntaje

        #Poner nueva comida si la serpiente colisiono con la coordenada de la comida y en el caso de no hacerlo le saco el ultimo elemento del cuerpo ya que muevo la cabeza
        if self.cabeza_serpiente == self.comida:
            self.puntaje += 1
            self._poner_comida()
        else:
            self.cuerpo_serpiente.pop()

            
        #Aumenta la velocidad a medida que el puntaje avanza
        if 10 > self.puntaje > 5 :
            self.velocidad_clock = 12
        elif 15 > self.puntaje > 10:
            self.velocidad_clock = 14
        elif 20 > self.puntaje > 15:
            self.velocidad_clock = 16
        elif self.puntaje > 30:
            self.velocidad_clock = 24
            

        #actualizar pantalla y el reloj del juego
        self._actualizar_pantalla()
        self.clock.tick(self.velocidad_clock)

        return perder , self.puntaje
        
        
        
    #Funcion que dibuja la serpiente y la comida
    def _actualizar_pantalla(self):
        self.display.fill(NEGRO)        
        for punto in self.cuerpo_serpiente:            
            pygame.draw.rect(self.display, VERDE , pygame.Rect(punto.x,punto.y,bloque_size,bloque_size))
            #Efecto
            pygame.draw.rect(self.display, VERDE2 , pygame.Rect(punto.x + 4 , punto.y + 4 ,30 ,30))

        #Funcion de pygame que dibuja pasandole como argumento (pantalla,color,forma(coordenadas))
        pygame.draw.rect(self.display,ROJO,pygame.Rect(self.comida.x,self.comida.y,bloque_size,bloque_size))


        texto_puntaje = letra.render("Puntaje: "+ str(self.puntaje), True, BLANCO)
        self.display.blit(texto_puntaje, [0,0])
        pygame.display.flip()
    
    #Obtengo las coordenadas de la cabeza al momento y muevo la posicion el tamaño de un bloque hacia donde apunte el input del usuario
    def _mover_serpiente(self, direccion):
        x = self.cabeza_serpiente.x
        y = self.cabeza_serpiente.y
        if direccion == Direccion.DERECHA:
            x += bloque_size
        elif direccion == Direccion.IZQUIERDA:
            x -= bloque_size
        elif direccion == Direccion.ARRIBA:
            y -= bloque_size
        elif direccion == Direccion.ABAJO:
            y += bloque_size
        
        self.cabeza_serpiente = Coordenada(x,y)


    def _colision(self):
        #Choca con los bordes
        if self.cabeza_serpiente.x > (ancho_ventana - bloque_size) or self.cabeza_serpiente.x < 0 or 0 > self.cabeza_serpiente.y or self.cabeza_serpiente.y > (alto_ventana - bloque_size):
            return True
        #Choca con el cuerpo pero sin contar la cabeza
        if self.cabeza_serpiente in self.cuerpo_serpiente[1:]:
            return True

        return False



if __name__ == '__main__':
    juego = JuegoSerpiente(ancho_ventana,alto_ventana)
    #Loop del juego que actualiza la pantalla
    while True:
        perder, puntaje = juego.actualizar()
        #Si se da una colision se termina el loop
        if perder == True:
            break
            
    print("Su puntaje fue de: ", puntaje)
    pygame.quit()
    
