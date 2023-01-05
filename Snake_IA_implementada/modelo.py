import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class AprendizajeReforzado(nn.Module):
    def __init__(self, input_tamaño, input_escondido, salida_tamaño):
        super().__init__()
        self.linear1 = nn.Linear(input_tamaño, input_escondido)
        self.linear2 = nn.Linear(input_escondido, salida_tamaño)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    def guardar(self, nombre_archivo='modelo.pth'):
        modelo_carpeta_ruta = './modelo'
        if not os.path.exists(modelo_carpeta_ruta):
            os.mkdir(modelo_carpeta_ruta)
        
        nombre_archivo = os.path.join(modelo_carpeta_ruta,nombre_archivo)
        torch.save(self.state_dict(), nombre_archivo)

class EntrenadorQ:
    def __init__(self, modelo, lr , gamma):
        self.modelo = modelo
        self.lr = lr
        self.gamma = gamma
        self.optimizador = optim.Adam(modelo.parameters(), lr = self.lr)
        self.criterio = nn.MSELoss()

    def paso_entrenamiento(self,estado,accion,recompensa,estado_siguiente, perder):
        
        estado = torch.tensor(estado, dtype=torch.float)
        estado_siguiente = torch.tensor(estado_siguiente,dtype=torch.float)
        accion = torch.tensor(accion,dtype=torch.float)
        recompensa = torch.tensor(recompensa,dtype=torch.float)
        # (n, x)

        if len(estado.shape) == 1:
            #(1, x)
            estado = torch.unsqueeze(estado, 0)
            estado_siguiente = torch.unsqueeze(estado_siguiente, 0)
            accion = torch.unsqueeze(accion, 0)
            recompensa = torch.unsqueeze(recompensa, 0)
            perder = (perder, )

        #Predecir valor Q con los valores actuales
        pred = self.modelo(estado)
        objetivo = pred.clone()
        for index in range(len(perder)):
            nuevo_Q = recompensa[index]
            if not perder[index]:
                nuevo_Q = recompensa[index] + self.gamma * torch.max(self.modelo(estado_siguiente[index]))

            objetivo[index][torch.argmax(accion[index]).item()] = nuevo_Q 

        # recompensa + gamma * maximo de la (prediccion Q) 
        #clonamos la pred para tener los 3 valores
        #predicciones [argmax(accion)] = nuevo_Q
        self.optimizador.zero_grad() #funcion pytorch
        perdida = self.criterio(objetivo,pred)
        perdida.backward()
        self.optimizador.step()


