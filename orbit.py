import numpy as np
import pygame
import pygame.gfxdraw

class PyGameApp():
    def __init__(self, x, y, appName="App"):
        self.size = (x,y)
        self.screen = False
        self.appName = appName
        
    def __enter__(self):
        pygame.init()
        size=[self.size[0],self.size[1]]
        self.screen=pygame.display.set_mode(size)
        pygame.display.set_caption(self.appName)
        return self
    
    def __exit__(self, _, __, ___):
        pygame.quit()

class Elipse():
    def __init__(self, a, e):
        assert e >= 0 and e <= 1
        self.a = a
        self.e = e

    def r(self, theta):
        return self.a * (1 - self.e) / (1 + self.e * np.cos(theta))
        
def go():
    # Define some colors
    black    = (   0,   0,   0)
    white    = ( 255, 255, 255)
    green    = (   0, 255,   0)
    red      = ( 255,   0,   0)
    yellow   = ( 255, 255,   0)

    fps     = 20
    dt      = 1.0 / fps
    angle   = 0.0
    radialSpeed = np.radians(90.0) # deg/s -> rad/s
    elipse  = Elipse(400, 0.6)

    sizeX, sizeY = (800, 600)
    with PyGameApp(sizeX, sizeY, "orbit") as pyg:
        print("%s %s" % (pyg, type(pyg).__name__))
        done=False
        clock=pygame.time.Clock()
     
        # -------- Main Program Loop -----------
        while done==False:
            for event in pygame.event.get(): 
                if (event.type == pygame.QUIT
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_q)):
                    done=True 

            # draw
            pyg.screen.fill(black)
            center = (int(sizeX * 0.6), int(sizeY * 0.5))
            pygame.gfxdraw.filled_circle(pyg.screen, center[0], center[1], 15, yellow)

            r = elipse.r(angle)
            x, y = (int(r * np.cos(angle) + center[0]), int(r * np.sin(angle)) + center[1])
            pygame.gfxdraw.filled_circle(pyg.screen, x, y, 5, white)
            angle = angle + radialSpeed * dt
            
            pygame.display.flip() # Go ahead and update the screen with what we've drawn.
            clock.tick(fps)
