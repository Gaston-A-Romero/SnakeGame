import pygame 
import random 
from enum import Enum
from collections import namedtuple
import numpy 
pygame.init()

#Cosas que cambian del proyecto para poder utilizar la IA
"""
1-Funcion de resetear el juego automaticamente al perder
2-Agregar la recompensa para que podamos entrenar la IA
3-Se cambia la funcion actualizar() a una actualizar(accion) ---> devuelve una direccion 
4-Tenemos que guardar las iteraciones del juego
5- Cambiar la funcion colisiones

"""




#Variables constantes

ancho_ventana = 800
alto_ventana = 800
#cada cuadricula sera de un tamaño de 10 por lo que se podran dar 80*60 
bloque_size = 40
velocidad_clock = 30


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

class JuegoSerpienteIA:
    def __init__(self,ancho_ventana,alto_ventana):
        self.ancho_ventana = ancho_ventana
        self.alto_ventana = alto_ventana

        #Iniciar la ventana
        self.display = pygame.display.set_mode((self.ancho_ventana,self.alto_ventana))
        pygame.display.set_caption("Juego de la Serpiente")
        self.clock = pygame.time.Clock()
        self.resetear()
        self.iteraciones_pantalla = 0

        


    def resetear(self):
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

    def _poner_comida(self):
        #Hay que poner comida en una posicion al azar que este dentro de los límites de la pantalla
        x = random.randint(0, (self.ancho_ventana-bloque_size)//bloque_size)*bloque_size
        y = random.randint(0, (self.alto_ventana-bloque_size)//bloque_size)*bloque_size
        self.comida = Coordenada(x,y)
        #Controlo que la comida no se ponga en alguna coordenada donde se encuentra la serpiente, si lo hace vuelvo a llamar a la funcion con recursion
        if self.comida in self.cuerpo_serpiente:
            self._poner_comida()

    def actualizar(self,accion):
        self.iteraciones_pantalla += 1
        #Mirar los inputs del usuario
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                perder = True
                    
        #Mover la serpiente con dichos inputs y cambiar la direccion de la cabeza
        self._mover_serpiente(accion) # ----> Actualiza la serpiente 
        self.cuerpo_serpiente.insert(0, self.cabeza_serpiente)

        #Ver si hay colisiones 
        recompensa = 0
        perder = False
        if self.colision() or self.iteraciones_pantalla > 100*len(self.cuerpo_serpiente):
            perder = True
            recompensa = -10
            return recompensa, perder, self.puntaje

        #Poner nueva comida si la serpiente colisiono con la coordenada de la comida y en el caso de no hacerlo le saco el ultimo elemento del cuerpo ya que muevo la cabeza
        if self.cabeza_serpiente == self.comida:
            self.puntaje += 1
            recompensa = 10
            self._poner_comida()
        else:
            self.cuerpo_serpiente.pop()

        #actualizar pantalla y el reloj del juego
        self._actualizar_pantalla()
        self.clock.tick(velocidad_clock)

        return recompensa, perder , self.puntaje
        
        
        
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
    
    #Dependiendo de la accion pasada por parametro tomaremos la nueva direccion
    def _mover_serpiente(self, accion):
        #        [SEGUIR_DIRECCION_ACTUAL , Girar_DERECHA , Girar_IZQUIERDA]
        # ACCION         [1,0,0]          ,    [0,1,0]    ,     [0,0,1]

        sentido_horario = [Direccion.DERECHA , Direccion.ABAJO , Direccion.IZQUIERDA , Direccion.ARRIBA]
        #Obtengo la direccion actual
        indice_direccion_actual = sentido_horario.index(self.direccion)
        if numpy.array_equal(accion,[1,0,0]):
            nueva_direccion = sentido_horario[indice_direccion_actual] #no cambia la direccion

        elif numpy.array_equal(accion,[0,1,0]): # giro derecha yendo a la derecha -> abajo -> izquierda -> arriba
            nuevo_indice = (indice_direccion_actual + 1) % 4 #Usas cuatro para que al sumar uno se vuelve a 0
            nueva_direccion = sentido_horario[nuevo_indice]

        else: # [0,0,1]  giro izquierda yendo a la derecha -> arriba -> izquierda -> abajo
            nuevo_indice = (indice_direccion_actual - 1) % 4 #Usas cuatro para que al sumar uno se vuelve a 0
            nueva_direccion = sentido_horario[nuevo_indice]

        self.direccion = nueva_direccion

        x = self.cabeza_serpiente.x
        y = self.cabeza_serpiente.y
        if self.direccion == Direccion.DERECHA:
            x += bloque_size
        elif self.direccion == Direccion.IZQUIERDA:
            x -= bloque_size
        elif self.direccion == Direccion.ARRIBA:
            y -= bloque_size
        elif self.direccion == Direccion.ABAJO: # se suma porque arranca la ventana desde arriba con valor 0 y a medida que bajas se hace > 0
            y += bloque_size
        
        self.cabeza_serpiente = Coordenada(x,y)


    def colision(self, punto = None):
        #Cambiamos la cabeza por un punto que arranca en la cabeza
        if punto == None:
            punto = self.cabeza_serpiente
        #Choca con los bordes
        if punto.x > (ancho_ventana - bloque_size) or punto.x < 0 or 0 > punto.y or punto.y > (alto_ventana - bloque_size):
            return True
        #Choca con el cuerpo pero sin contar la cabeza
        if punto in self.cuerpo_serpiente[1:]:
            return True

        return False


