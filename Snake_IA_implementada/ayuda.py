import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(puntaje,media_puntajes):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Entrenando')
    plt.xlabel('Numero juegos')
    plt.ylabel('Puntaje')
    plt.plot(puntaje)
    plt.plot(media_puntajes)
    plt.ylim(ymin=0)
    plt.text(len(puntaje)-1, puntaje[-1], str(puntaje[-1]))
    plt.text(len(media_puntajes)-1, media_puntajes[-1], str(media_puntajes[-1]))
    plt.show(block= False)
    plt.pause(.1)
