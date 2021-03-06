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
        self.L  = L
        self.e  = e
        self.G  = 6.6742867e-11 # M m2 kg-2
        self.initialize()

    def initialize(self):
        self.M          = self.m1 + self.m2
        self.mu         = self.m1 * self.m2 / self.M
        self.perihelion = np.maximum(self.r1(0), self.r2(0))
        self.aphelion   = np.maximum(self.r1(np.pi), self.r2(np.pi))
        motionA         = (self.aphelion + self.perihelion) * 0.5
        self.P          = np.sqrt(4 * np.pi * np.pi * motionA * motionA * motionA / (self.G * (self.m1 + self.m2)))

    def r(self, theta):
        return np.power(self.L, 2) / (np.power(self.mu, 2) * self.G * self.M * (1 + self.e * np.cos(theta)))

    def r1(self, theta):
        r = self.r(theta)
        return -1 * self.mu / self.m1 * r

    def r2(self, theta):
        r = self.r(theta)
        return self.mu / self.m2 * r

def make_video(screen):
    image_num = 0
    while True:
        yield
        image_num += 1
        str_num = "000" + str(image_num)
        file_name = "images/image" + str_num[-4:] + ".jpg"
        pygame.image.save(screen, file_name)

def printLabel(font, screen, msg, x, y, color):
    fontSurface = font.render(msg, False, color)
    (labelW, labelH) = fontSurface.get_size()
    offset = (int(labelW * 0.5), int(labelH * 0.5))
    screen.blit(fontSurface, (int(x - offset[0]), int(y - offset[1])))

def computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio):
    center      = (int(sizeX * 0.5), int(sizeY * 0.5))
    aphelion    = binary.aphelion
    perihelion  = binary.perihelion
    sideHeight  = np.maximum(binary.r1(np.pi*0.5), binary.r2(np.pi*0.5))

    motionScreenSize        = sizeY if np.abs(sideHeight) > np.abs(aphelion) else sizeX
    halfMotionScreenSize    = motionScreenSize * motionScreenRatio * 0.5
    elipseHalfWidth         = (perihelion - aphelion) * 0.5
    elipseHalfWidthScreenSize = np.interp(elipseHalfWidth, [-aphelion, aphelion], [-halfMotionScreenSize,
                                                                                     halfMotionScreenSize])
    renderCenter = (center[0] - elipseHalfWidthScreenSize, center[1])

    return halfMotionScreenSize, renderCenter
    
def go():
    # Define some colors
    black    = (   0,   0,   0)
    white    = ( 255, 255, 255)
    green    = (   0, 255,   0)
    red      = ( 255,   0,   0)
    yellow   = ( 255, 255,   0)

    fps         = 20
    dt          = 1.0 / fps
    angle       = 0.0
    radialSpeed = np.radians(90.0) # deg/s -> rad/s
    
    # elipse  = Elipse(400, 0.6)

    # P                   = 365.25 * 24 * 60 * 60
    # SolarMass           = 1.9891e30 # kg
    # EarthMass           = 5.9736e24 # kg
    # EarthSunDistance    = 149.6e9   # m
    # EarthOrbitalSpeed   = 2 * np.pi * EarthSunDistance / P
    # L           = EarthOrbitalSpeed * EarthMass * EarthSunDistance # m/s
    # binary      = BinarySystem(SolarMass, EarthMass, L, 0.0167)
    # timeScale   = P / 5

    m1          = 2
    m2          = 1
    L           = 1
    eccentricity= 0.6
    binary      = BinarySystem(m1, m2, L, eccentricity)
    timeScale   = binary.P / 2

    sizeX, sizeY = (800, 600)
    motionScreenRatio = 0.5
    halfMotionScreenSize, renderCenter = computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio)

    lastPos = [False for i in range(50)]
    lastPosIndex = 0

    drawGhosts  = True
    drawInfos   = True
    renderVideo = True
    
    with PyGameApp(sizeX, sizeY, "orbit") as pyg:
        clock=pygame.time.Clock()

        fontSize = 14
        pygame.font.init()
        font = pygame.font.SysFont('Arial', fontSize)

        videoMaker = make_video(pyg.screen)
     
        # -------- Main Program Loop -----------
        done=False
        while not done:
            # event processing
            for event in pygame.event.get(): 
                if (event.type == pygame.QUIT
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_q)):
                    done=True
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_g):
                    drawGhosts = not drawGhosts

                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_i):
                    drawInfos = not drawInfos

                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_EQUALS):
                    lastPos = [False for i in range(50)]
                    lastPosIndex = 0
                    motionScreenRatio = min(motionScreenRatio + 0.1, 1)
                    halfMotionScreenSize, renderCenter = computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio)

                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS):
                    lastPos = [False for i in range(50)]
                    lastPosIndex = 0
                    motionScreenRatio = max(motionScreenRatio - 0.1, 0.1)
                    halfMotionScreenSize, renderCenter = computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio)

                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_v):
                    renderVideo = not renderVideo
                    print("renderVideo: %s" % renderVideo)

                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_r):
                    angle       = 0
                    m1          = 1
                    m2          = 1
                    L           = 10
                    eccentricity=0.01
                    binary      = BinarySystem(m1, m2, L, eccentricity)
                    motionScreenRatio = 0.5
                    halfMotionScreenSize, renderCenter = computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio)
                    lastPos = [False for i in range(50)]
                    lastPosIndex = 0

            # draw
            pyg.screen.fill(black)

            aphelion, perihelion = binary.aphelion, binary.perihelion
            r1, r2 = (binary.r1(angle), binary.r2(angle))
            relR1, relR2 = (np.interp(r1, [-aphelion, aphelion], [-halfMotionScreenSize, halfMotionScreenSize]),
                            np.interp(r2, [-aphelion, aphelion], [-halfMotionScreenSize, halfMotionScreenSize]))

            # print("ap: %.2e, pe: %.2e, r1: %.2e, r2: %.2e, angle: %.2f" % (aphelion, perihelion, r1, r2, angle))

            #print("relR1: %.2f, cos: %.2f" % (relR1, np.cos(angle)))
            x1, y1 = (int(relR1 * np.cos(angle) + renderCenter[0]), int(relR1 * np.sin(angle)) + renderCenter[1])
            x2, y2 = (int(relR2 * np.cos(angle) + renderCenter[0]), int(relR2 * np.sin(angle)) + renderCenter[1])

            pygame.gfxdraw.filled_circle(pyg.screen, x1, y1, 5, yellow)
            pygame.gfxdraw.filled_circle(pyg.screen, x2, y2, 5, white)

            # update data
            r       = binary.r(angle)
            scaledDT= dt * timeScale
            dAngle  = binary.L * scaledDT / (binary.mu * r * r)
            angle   = angle + dAngle
            # print("L: %.2e, r: %.2e, scaledDT: %.2e, mu: %.2e, dAngle: %.2e" % (binary.L, r, scaledDT, binary.mu, dAngle))

            # if binary.e < 0.9:
            #     binary.e = np.interp(angle, [0, np.pi*6], [0.01, 0.99])
            # else:
            #     done = True
            # else:
            # binary.m1 = np.interp(angle, [0, np.pi*2], [m1, 2*m1])
            # if angle > np.pi * 2:
            #     angle = 0
            #     m1 = binary.m1
            # binary.initialize()
            # halfMotionScreenSize, renderCenter = computeDrawVariables(binary, sizeX, sizeY, motionScreenRatio)

            # infos
            if drawInfos:
                fontSurface = font.render("m1", False, white)
                pyg.screen.blit(fontSurface, (x1, y1 + 5))

                fontSurface = font.render("m2", False, white)
                pyg.screen.blit(fontSurface, (x2, y2 + 5))

                infoLabel   = "Binary system motion"
                infoLabel2  = "m1: %.2eg, m2: %.2eg, L: %.2em/s, e: %.2f" % (binary.m1, binary.m2, binary.L, binary.e)
                infoLabel3  = ("Period: %.2es (%.2edays) time scale: %.2e, aphelion: %.2em, perihelion: %.2em"
                               % (binary.P, binary.P / (60.0*60.0*24), timeScale, binary.aphelion, binary.perihelion))

                printLabel(font, pyg.screen, infoLabel, sizeX * 0.5, sizeY * 0.9, white)
                printLabel(font, pyg.screen, infoLabel2, sizeX * 0.5, sizeY * 0.9 + (fontSize+2), white)
                printLabel(font, pyg.screen, infoLabel3, sizeX * 0.5, sizeY * 0.9 + (fontSize+2)*2, white)

            # save ghost in circular buffer
            lastPos[lastPosIndex] = (x1, x2, y1, y2)
            lastPosIndex = (lastPosIndex + 1) % len(lastPos)

            # replay ghost positions
            if drawGhosts:
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
                
            pygame.display.flip()
            clock.tick(fps)

            # save video
            if renderVideo:
                next(videoMaker)
