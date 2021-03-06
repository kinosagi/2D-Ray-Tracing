from kivy.app import App
# from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
# from kivy.uix.behaviors import DragBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, ListProperty
# import numpy as np
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Line, Rectangle, Color, Ellipse, Mesh
from kivy.vector import Vector
from random import randint
from kivy.metrics import dp



class LineGeneral():
    def __init__(self, x1, y1, x2, y2, angle):
        self.Vi = Vector(x1,y1)
        self.Vf = Vector(x2,y2)
        self.angle = angle

class Obstacle(LineGeneral):
    def __init__(self, x1,y1,x2,y2,angle=0):
        super().__init__(x1,y1,x2,y2,angle)

class Ray(LineGeneral):
    def __init__(self, x1,y1,x2,y2,angle):
        super().__init__(x1,y1,x2,y2,angle)

class Particle(Widget):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Movable = BooleanProperty(False)

    
    pass

class TelaPrincipal(BoxLayout):

    particle = ObjectProperty(None)
    rayQty = NumericProperty(100)
    obstQty = NumericProperty(0)

    rayList = ListProperty()
    obstList = ListProperty()

    drawLine = ObjectProperty(None)
    drawingLine = BooleanProperty(False)
    newLine = [0,0,0,0]

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Clock.schedule_interval(self.Tick,1/60.0)

        # Add rays to Screen
        for i in range(0,self.rayQty):
            direction = dp(300)*Vector(0,1).rotate(i*360/self.rayQty)
            ray = Ray(Window.center[0],Window.center[1],Window.center[0]+direction[0],Window.center[1]+direction[1],i*360/self.rayQty)
            self.rayList.append(ray)
        
        # Add obstacles to Screen
        for i in range(0,self.obstQty):
            obst = Obstacle(randint(0,Window.width),randint(0,Window.height),randint(0,Window.width),randint(0,Window.height))
            self.obstList.append(obst)


    def on_touch_move(self, touch):
        if not self.drawLine.active:
            if not self.ids.menuRegion.collide_point(*touch.pos):
                self.particle.center = [touch.x, touch.y]
        else:
            self.newLine[2], self.newLine[3] = touch.x, touch.y
            self.canvas.after.clear()
            with self.canvas.after:
                Color(rgba=(0.5,0.5,0.5,0.5))
                Line(points=[*self.newLine], width=dp(2))  
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        
        if self.drawLine.active:
            self.newLine[0], self.newLine[1] = touch.x, touch.y
            self.newLine[2], self.newLine[3] = touch.x, touch.y
            
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.drawLine.active:
            #self.newLine[2], self.newLine[3] = touch.x, touch.y

            if not (self.newLine[0] == self.newLine[2] and self.newLine[1]==self.newLine[3]):
                obst = Obstacle(*self.newLine)
                self.obstList.append(obst)
            self.canvas.after.clear()
            
        return super().on_touch_up(touch)
        

    def Tick(self, dt):
        # Clean Canvas
        self.canvas.before.clear()

        meshVerticesList = []

        # Move and draw rays
        for ray in self.rayList:
            
            # if raycount>=self.tickCount: break
            # raycount +=1

            ray.Vi = Vector(self.particle.center_x, self.particle.center_y)
            ray.Vf = ray.Vi + dp(1000)*Vector(0,1).rotate(ray.angle)

            dist = dp(5000)
            
            # Check intersection with obstacles
            for obst in self.obstList:

                # Distance for each obstacle
                

                # Calculate intersection point
                interPoint, onLine1, onLine2 = self.LineIntersection([ray.Vi,ray.Vf],[obst.Vi, obst.Vf])
                if onLine2 == True and onLine1 == True:
                    if ray.Vi.distance(interPoint) < dist:
                        dist = ray.Vi.distance(interPoint)
                        ray.Vf.x, ray.Vf.y = Vector(interPoint[0], interPoint[1])

                    # Draw intersection points
                    # with self.canvas.before:
                    #     Color(1,0,0,1)
                    #     Ellipse(size=(2,2), pos=(interPoint[0]-1, interPoint[1]-1))

            # Draw end points
            with self.canvas.before:
                #Color(1,1,1,0.5)
                #Line(points=(ray.Vi, ray.Vf,), width = 1)
                Color(((1000-dist)/1000),(dist/200),0,1)
                Ellipse(size=(dp(4),dp(4)), pos=(ray.Vf.x-2, ray.Vf.y-2))

            meshVerticesList.extend([ray.Vf.x,ray.Vf.y,0,0])

        
        # Draw mesh
        meshIndList = list(range(len(meshVerticesList)//4))
        with self.canvas.before:
            Color(1,1,1,0.2)
            Mesh(mode='line_loop', vertices=meshVerticesList, indices=meshIndList)
        
        # Draw obstacles
        for obst in self.obstList:
            with self.canvas.before:
                Color(rgba=(0.5,0.5,0.5,1))
                Line(points=[obst.Vi, obst.Vf], width=dp(1))
                Color(rgba=(1,1,1,1))

    def LineIntersection(self, line1, line2):
        Vi1, Vf1 = line1
        Vi2, Vf2 = line2
        x1,y1 = Vi1
        x2,y2 = Vf1
        x3,y3 = Vi2
        x4,y4 = Vf2
        
        # Calculate intersection point
        t_num = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
        t_den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        t = t_num/t_den

        u_num = (x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)
        u_den = t_den
        u = -u_num/u_den
        
        Px = x1 + t*(x2-x1)
        Py = y1 + t*(y2-y1)
        interPoint = [Px,Py]

        # Check if intersection point is on line1 and/or on line2
        onLine1 = True if (t>=0 and t<=1) else False
        onLine2 = True if (u>=0 and u<=1) else False

        return [interPoint, onLine1, onLine2]
    

class RT2D_App(App):
    def build(self):
        tela = TelaPrincipal()
        #Clock.schedule_interval(tela.update,1.0/60.0)
        return tela

app = RT2D_App()
app.run()
        
    