import torch
import random
import numpy
from collections import deque #Estructura de datos que permite agregar elementos tanto al final como el principio de la misma
from Snake_con_IA import JuegoSerpienteIA, Coordenada , Direccion
from modelo import AprendizajeReforzado, EntrenadorQ
from ayuda import plot


MAXIMA_MEMORIA = 100_000
BATCH_tamaño = 1000  #Agrupacion de datos, concepto similar a cluster por ejemplo
RATIO_APRENDIZAJE = 0.001
bloque_size = 20


class Agente:
    def __init__(self):
        self.numero_juegos = 0
        self.epsilon = 0 #controla la aleatoriedad
        self.gamma = 0.9  #ratio descuento -> tiene que ser menor que 1
        self.memoria = deque(maxlen=MAXIMA_MEMORIA) #llama a popleft() si se supera la memoria max
        self.modelo = AprendizajeReforzado(11, 256, 3) # 11 estados , el escondido lo podemos cambiar y el ultimo es la direccion(seguir,derecha,izquierda)
        self.entrenador = EntrenadorQ(self.modelo, lr= RATIO_APRENDIZAJE, gamma= self.gamma)


    #ESTADOS VAN A SER 11
    # [PELIGRO_ADELANTE , PELIGRO_DERECHA, PELIGRO_IZQUIERDA, 4 DIRECCIONES SERPIENTE, 4 DIRECCIONES DE PARA LA COMIDA]
    # SE VA A USAR UN ARRAY CON 11 VALORES ENTRE 0(NEGACION) Y 1(AFIRMACION) 
    def obtener_estado(self, juego):
        #Obtengo la coordenada de la cabeza de la serpiente
        cabeza = juego.cuerpo_serpiente[0]

        #OBTENGO LOS PUNTOS SIGUIENTES EN CADA DIRECCION
        siguiente_derecha = Coordenada(cabeza.x + bloque_size , cabeza.y)
        siguiente_izquierda = Coordenada(cabeza.x - bloque_size , cabeza.y)
        siguiente_arriba = Coordenada(cabeza.x, cabeza.y - bloque_size )
        siguiente_abajo = Coordenada(cabeza.x, cabeza.y + bloque_size)

        #Obtengo cual de las direcciones es la actual para la serpiente
        dir_izq = juego.direccion == Direccion.IZQUIERDA
        dir_der = juego.direccion == Direccion.DERECHA
        dir_up = juego.direccion == Direccion.ARRIBA
        dir_down = juego.direccion == Direccion.ABAJO

        # Inicializo el ARRAY DE ESTADOS

        estado = [
            #Peligro siguiendo la misma direccion
            (dir_der and juego.colision(siguiente_derecha))  or  (dir_izq and juego.colision(siguiente_izquierda))
            or (dir_up and juego.colision(siguiente_arriba)) or (dir_down and juego.colision(siguiente_abajo)),
            
            #Peligro a la derecha
            (dir_der and juego.colision(siguiente_abajo)) or (dir_down and juego.colision(siguiente_izquierda))or
            (dir_izq and juego.colision(siguiente_arriba)) or (dir_up and juego.colision(siguiente_derecha)),

            #Peligro a la izquierda
            (dir_der and juego.colision(siguiente_arriba)) or (dir_down and juego.colision(siguiente_derecha))or
            (dir_izq and juego.colision(siguiente_abajo)) or (dir_up and juego.colision(siguiente_izquierda)),

            #Direccion movimiento actual
            dir_izq,
            dir_der,
            dir_up,
            dir_down,

            #Direcciones donde se encuentra la comida
            juego.comida.x < juego.cabeza_serpiente.x,
            juego.comida.x > juego.cabeza_serpiente.x,
            juego.comida.y < juego.cabeza_serpiente.y,
            juego.comida.y > juego.cabeza_serpiente.y
        ]
        return numpy.array(estado,dtype=int)


        

    def guardar_en_memoria(self,estado,accion,recompensa,estado_siguiente, perder):
        self.memoria.append((estado,accion,recompensa,estado_siguiente, perder)) #popleft() if max_memory, doble apendice para poder agregarlo como una tupla

    def entrenar_memoria_total(self):
        if len(self.memoria) > BATCH_tamaño:
            mini_prueba = random.sample(self.memoria, BATCH_tamaño) # devuelve una lista de tuplas
        else:
            mini_prueba = self.memoria

        estados,acciones,recompensas,estados_siguientes, perdidas = zip(*mini_prueba) #Desempaquetar la lista de tuplas para que los datos se agrupen con su mismo tipo
        self.entrenador.paso_entrenamiento(estados,acciones,recompensas,estados_siguientes, perdidas)

    def entrenar_memoria_corta(self,estado,accion,recompensa,estado_siguiente, perder):
        self.entrenador.paso_entrenamiento(estado,accion,recompensa,estado_siguiente, perder)

    def obtener_accion(self,estado):
        #Movimientos aleatorios para definir el intercambio entre explotacion(cuando ya aprendio pasamos a explotar) y exploracion(primeras veces) del modelo
        #A medida que aumentan los juegos epsilon se hara mas pequeña por lo q sera menos probable que se hagan movimientos aleatorios
        self.epsilon = 80 - self.numero_juegos
        movimiento_final = [0,0,0]
        #Exploracion
        if random.randint(0, 200) < self.epsilon:
            movimiento = random.randint(0, 2)
            movimiento_final[movimiento] = 1
        #Explotacion
        else:
            estado_0 = torch.tensor(estado , dtype=torch.float)
            prediccion = self.modelo(estado_0)
            movimiento = torch.argmax(prediccion).item()
            movimiento_final[movimiento] = 1
        
        return movimiento_final
        

def entrenar():
    puntajes = []
    media_puntajes = []
    puntaje_total = 0
    mejor_puntaje = 0
    agente = Agente()
    juego = JuegoSerpienteIA(ancho_ventana=640,alto_ventana=480)

    while True:
        #Obtener estado viejo
        estado_anterior = agente.obtener_estado(juego)
        #Obtener movimiento basado en el estado anterior
        movimiento_final = agente.obtener_accion(estado_anterior)
        #realizar el movimiento y obtener el nuevo estado
        recompensa , perder, puntaje = juego.actualizar(movimiento_final) 
        nuevo_estado = agente.obtener_estado(juego)

        #Entrenar la memoria unitaria
        agente.entrenar_memoria_corta(estado_anterior,movimiento_final,recompensa,nuevo_estado,perder)

        #guardar en memoria
        agente.guardar_en_memoria(estado_anterior,movimiento_final,recompensa,nuevo_estado,perder)

        if perder:
            #entrenar la memoria total o actualizar la experiencia del agente
            juego.resetear()
            agente.numero_juegos += 1
            agente.entrenar_memoria_total()
            
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                agente.modelo.guardar()
            print('Juego',agente.numero_juegos,'Puntaje',puntaje,'Mejor puntaje',mejor_puntaje)
            
            puntajes.append(puntaje)
            puntaje_total += puntaje
            puntaje_promedio = puntaje_total // agente.numero_juegos
            media_puntajes.append(puntaje_promedio)
            plot(puntajes, media_puntajes)
            




if __name__ == '__main__':
    entrenar()
