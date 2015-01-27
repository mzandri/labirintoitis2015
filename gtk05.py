########################################
# programma server labirinto
#   Grafica gtk
#   Socket tcp/ip
#
# Giulio Venturi 2014
#
# basato su idee iniziali prese da: 
#         https://git.gnome.org/browse/pygobject/tree/examples
#
# vedere anche: 
#         http://www.pygtk.org/pygtk2reference
#         http://python-gtk-3-tutorial.readthedocs.org/en/latest/label.html
#
# Questo programma dovrebbe avere poche modifiche
# serve solo come server per i client da sviluppare e testare
########################################


import cairo
from gi.repository import Gtk,  GObject

import math

#PER IL SERVER TCP IP
from socket import *
import thread
import time


#
# Dati di configurazione
#
#griglia =[[0 for i in range(50)] for i in range(50)]


#labirinto: lista di liste di punti in una griglia di 50x50 
labirinto=[
            [(15,5),(5,5),(5,45),(45,45),(45,5),(25,5)],
            [(15,12),(25,12),(25,25),(35,25),(35,20)],
            [(12,33),(37,31)],
            [(12,39),(37,38)],
            [(12,33),(12,17)]
          ]

#robots: lista di coordinate dei robots in campo
# per ogni robot: (x,y,a,v)
# x,y: posizione in pixel*SIZE
# a :  angolo DEG
# v :  pixel*SIZE/secondo
robots=[(20,5,0,0)]

#mattoncini che costituiscono i muri 
mattoncini=[]

SIZE = 11 #dimensione di un quadratino-modulo
d = 1
dt = 30.0 # tempo (ms) frequenza di aggiornamento video 


def sen(a):
    return math.sin(math.pi*a/180.0)
    
def cos(a):
    return math.cos(math.pi*a/180.0)
 
def drawmattoncino(ctx,x,y):
#disegna un mattoncino  
    ctx.translate(x*SIZE,y*SIZE)
    ctx.set_source_rgba(0, 1, 0,0.7)
    ctx.set_line_width(1) # spessore linea
    ctx.set_tolerance(0.1) #?
    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
    
    ctx.new_path() 
    ctx.move_to(1, 1)
    ctx.rel_line_to(SIZE-2, 0)
    ctx.rel_line_to(0,      SIZE-2)
    ctx.rel_line_to(2-SIZE, 0)
    ctx.close_path()

    ctx.stroke()
    ctx.translate(-x*SIZE,-y*SIZE)

   
   
   
def calcolamuro(xp,yp,x,y):
#calcola le coordinate dei mattoncini
#che si trovano nel segmento che unisce i punti (xp,yp) e (x,y)   
    dx = x - xp
    dy = y - yp
    d = max(abs(dx),abs(dy))
    if d > 0:
        i = 0.0
        while i<=d: 
            #genera un mattoncino e lo appende alla lista dei mattoncini
            mattoncini.append((xp+dx*i/d,yp+dy*i/d))
            i+=1.0

#
# Funzioni di supporto.
#  
  
#disegna un triangolo  
def tri(ctx,x,y):
    ctx.new_path() 
    ctx.move_to(SIZE, 0)
    ctx.rel_line_to(SIZE, 2 * SIZE)
    ctx.rel_line_to(-2 * SIZE, 0)
    ctx.close_path()
    
#disegna 
def triangle(ctx,x,y):
    ctx.translate(x,y)
    
    ctx.set_source_rgba(0, 1, 0,0.3)
    tri(ctx,x,y)
    ctx.fill()

    ctx.set_source_rgba(1, 0, 0,0.9)
    tri(ctx,x,y)
    ctx.stroke()
    ctx.translate(-x,-y)
    
def moltiplica2(m,v):
#moltiplicazione matrice quadr ord 2 per vettore dim 2
    return m[0][0]*v[0]+m[0][1]*v[1],   m[1][0]*v[0]+m[1][1]*v[1]
    
    
def linearel(ctx,matr,x0,y0):
    x1,y1=moltiplica2(matr,[x0,y0])    
    ctx.rel_line_to(x1,y1)
    #pass
    
def matricerot(a):
#matrice che moltiplicata per un vettore
#ne provoca la rotazione di un angolo a.
    return [[cos(a),sen(a)],[-sen(a),cos(a)]]  #-90 perche' la figura disegnata verso l'alto  
    
def drawrobot(ctx,x,y,a):
    matrice=matricerot(a)

    #triangle(ctx,x,y*SIZE)
    ctx.translate(x*SIZE,y*SIZE)
    ctx.set_source_rgba(0,0,0,1)
    
    ctx.new_path() 
    ctx.move_to(0, 0)
    #disegno della navicella
    linearel(ctx,matrice,6,0)
    linearel(ctx,matrice,0,12)
    linearel(ctx,matrice,6,0)
    linearel(ctx,matrice,0,-18)
    linearel(ctx,matrice,6,0)
    linearel(ctx,matrice,0,36)
    linearel(ctx,matrice,-12,12)
    linearel(ctx,matrice,-3,0)
    linearel(ctx,matrice,0,3)
    linearel(ctx,matrice,-6,0)
    linearel(ctx,matrice,0,-3)
    linearel(ctx,matrice,-3,0)            
    linearel(ctx,matrice,-12,-12)
    linearel(ctx,matrice,0,-36)
    linearel(ctx,matrice,6,0)
    linearel(ctx,matrice,0,18)
    linearel(ctx,matrice,6,0)
    linearel(ctx,matrice,0,-12)    
    linearel(ctx,matrice,6,0)    
    ctx.close_path()

    ctx.stroke()
    ctx.translate(-x*SIZE,-y*SIZE)
    
    
def compilalabirinto():
#legge la struttura dati labirinto
#e crea i muri di quadratini    
    for spezzata in labirinto :
        i = 0
        for (x,y) in spezzata:
            if i > 0 :
                calcolamuro(xp,yp,x,y)
            xp,yp = x,y
            i+=1
    #print "muro"
    #print mattoncini

def draw(da, ctx):
#disegna l'intero labirinto
    ctx.set_source_rgb(0, 0, 0) #colore

    ctx.set_line_width(SIZE / 4) # spessore linea
    ctx.set_tolerance(0.1) 
    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
    
    ctx.save()
    #quadratino(ctx,20,20)
            
    for (x,y) in mattoncini:
        drawmattoncino(ctx,x,y)
    
    for (x,y,a,v) in robots:
        drawrobot(ctx,x,y,a)  
        
    ctx.restore()    
    

######################################################################
# GESTIONE COMUNICAZIONE TCP IP
#
######################################################################
HOST = '127.0.0.1'# must be input parameter @TODO
PORT = 5556 # must be input parameter @TODO


def handler2(clientsock,addr):
    while 1:      
        data = clientsock.recv(30)
        print 'data:' + repr(data)
        if not data : 
            break
        #   if data == '': break
        a = f(1000) #solo per rallentare
        risposta="che?"
        if data[0] == 'a' : 
            print "avanti"
            robo.avanti(4)
            risposta = "ok"
        else:
            if data[0] == 'r' :
                robo.ruota(-1.57)
                risposta = "ok"
            else:
                if data[0] == 'l' :
                    robo.ruota(1.57)
                    risposta = "ok"
                else:
                    if data[0] == 's' and data[1] == '0' :
                        #sensore 0 : distanza avanti
                        # x e y temporanee
                        print "sensore"
                        tx=robo.x
                        ty=robo.y
                        mindist = 200
                        minpoint = (0,0)
                        while tx<100 and ty<100 :
                            for p in lista :
                                if distanza(p,(tx,ty))<20 :
                                    if mindist > distanza(p,(robo.x,robo.y)) :
                                        mindist = distanza(p,(robo.x,robo.y))
                                        minpoint = p
                            tx += robo.dx
                            ty += robo.dy
                        risposta = str(mindist)
                        print "rispondo a sensore: ", risposta
                        listaraggi = [ minpoint ]

        clientsock.send(risposta)
        time.sleep(0.6)
        print 'sent:' + repr(gen_response())
    clientsock.close()
    print "=== chiuso ===" 

dx = 0
da = 0

def handler(clientsock,addr):
    global dx
    global da

    while True:
        data = clientsock.recv(1024)
        print 'data:' + repr(data)
        if not data : 
            return
        
        if data[0] == 'a' : 
            dx = 1.0
        else: 
            if data[0] == 'r' :
                da = -90
            else:
                if data[0] == 'l' :
                    da = 90
        risposta='ok!!!!!!!\n'
        clientsock.send(risposta)
        print 'sent:' + repr("ok")
        time.sleep(0.6)

    clientsock.close()

def connetti():    
    if __name__=='__main__':
        ADDR = (HOST, PORT) #QUESTO SERVER
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind(ADDR)
        serversock.listen(2)
        #while 1:
        print 'waiting for connection...'
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        thread.start_new_thread(handler, (clientsock, addr))
        #robo.cli = clientsock
        #robo.addr= addr



######################################################################
# Gestione finestre GTK
#
######################################################################
class MyWindow(Gtk.Window):
    #angle = 25
    def __init__(self):
        Gtk.Window.__init__(self, title="Labirinto")

        self.set_default_size(650, 550)

        drawingarea = Gtk.DrawingArea()
        self.add(drawingarea)
        drawingarea.connect('draw', draw)
        
        compilalabirinto()

bConn = True #ancora da connettere al tcp/ip

#operazioni eseguite ogni dt millisecondi
def on_timeout(userdata):
    #global SIZE
    global bConn
    global robots
    global da
    global dx
    
    if bConn : 
        bConn = False
        connetti()
    
    l=len(robots)
    i=0
    while i<l:
        (x,y,a,v)=robots[i]
        #x1,y1=0,0
        x1,y1=moltiplica2(matricerot(a+da),[dx+v*dt/1000.0,0])
        robots = robots[:i] + [(x+x1,y+y1,a+da,v)] + robots[i+1:]
        i+=1

    #SIZE += d
    #if SIZE > 33 : d = -d
    #if SIZE < 27 : d = -d
    
    da = 0
    dx = 0
    win.queue_draw()
    return True # senza True il timer non ripete.


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
GObject.timeout_add(dt,on_timeout,None)


win.show_all()
Gtk.main()
