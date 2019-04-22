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

class BinarySystem():
    def __init__(self, m1, m2, L, e):
        self.m1 = m1
        self.m2 = m2
        self.M  = m1 + m2
        self.mu = m1*m2 / self.M
        self.L  = L
        self.e  = e
        self.G  = 6.6742867e-11 # M m2 kg-2

    def r(self, theta):
        return np.power(self.L, 2) / (np.power(self.mu, 2) * self.G * self.M * (1 + self.e * np.cos(theta)))

    def r1(self, theta):
        r = self.r(theta)
        return -1 * self.mu / self.m1 * r

    def r2(self, theta):
        r = self.r(theta)
        return self.mu / self.m2 * r
        
def go():
    # Define some colors
    black    = (   0,   0,   0)
    white    = ( 255, 255, 255)
    green    = (   0, 255,   0)
    red      = ( 255,   0,   0)
    yellow   = ( 255, 255,   0)

    sizeX, sizeY = (800, 600)
    center = (int(sizeX * 0.5), int(sizeY * 0.5))

    fps     = 20
    dt      = 1.0 / fps
    angle   = 0.0
    radialSpeed = np.radians(90.0) # deg/s -> rad/s
    elipse  = Elipse(400, 0.6)

    motionScreenRatio = 0.3

    SolarMass   = 1.9891e30 # kg
    EarthMass   = 5.9736e24 # kg
    L = 29800 * EarthMass # 29.8 km/s
    binary  = BinarySystem(SolarMass, EarthMass, L, 0.9)
    # binary  = BinarySystem(5, 1, 10, 0.6)
    aphelion = np.maximum(binary.r1(np.pi), binary.r2(np.pi))
    aphelionScreenSize = sizeX * motionScreenRatio

    perihelion = np.maximum(binary.r1(0), binary.r2(0))
    perihelionScreenSize = sizeX * motionScreenRatio

    renderCenter = (center[0] + aphelionScreenSize - perihelionScreenSize, center[1])

    lastPos = [False for i in range(50)]
    lastPosIndex = 0
    
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

            r1, r2 = (binary.r1(angle), binary.r2(angle))
            relR1, relR2 = (np.interp(r1, [-aphelion, aphelion], [-aphelionScreenSize, aphelionScreenSize]),
                            np.interp(r2, [-aphelion, aphelion], [-aphelionScreenSize, aphelionScreenSize]))

            # print("p: %.2f, r1: %.2f, r2: %.2f, angle: %.2f" % (aphelion, r1, r2, angle))

            x1, y1 = (int(relR1 * np.cos(angle) + renderCenter[0]), int(relR1 * np.sin(angle)) + renderCenter[1])
            x2, y2 = (int(relR2 * np.cos(angle) + renderCenter[0]), int(relR2 * np.sin(angle)) + renderCenter[1])

            pygame.gfxdraw.filled_circle(pyg.screen, x1, y1, 5, yellow)
            pygame.gfxdraw.filled_circle(pyg.screen, x2, y2, 5, white)

            # save ghost
            lastPos[lastPosIndex] = (x1, x2, y1, y2)
            lastPosIndex = (lastPosIndex + 1) % len(lastPos)

            # replay ghost positions
            for i in range(1, len(lastPos)):
                index = (lastPosIndex - i) % len(lastPos)
                if not lastPos[index]:
                    break
                else:
                    alpha           = np.interp(i, [0, len(lastPos)], [255, 0])
                    whiteColor      = white + (alpha,)
                    yellowColor     = yellow + (alpha,)
                    x1, x2, y1, y2 = lastPos[index]
                    pygame.gfxdraw.filled_circle(pyg.screen, x1, y1, 5, yellowColor)
                    pygame.gfxdraw.filled_circle(pyg.screen, x2, y2, 5, whiteColor)
            
            pygame.display.flip() # Go ahead and update the screen with what we've drawn.
            clock.tick(fps)

            angle = angle + radialSpeed * dt
