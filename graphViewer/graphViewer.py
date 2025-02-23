import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import glm

from . import graph as G
from . import graphDrawer as GD
from . import graphPainter as GP
from .camera import Camera

class GraphViewer:
    def __init__(self, graph, parameters):
        self.displaySize = (1500, 900)
        self.displayFOV = 50.0
        self.displayNear = 0.1
        self.displayFar = 50.0
        self.data = G.Graph(graph, initialize=False)

        self.parameters = parameters
    
    def run(self):
        self.graphDrawer = GD.GraphDrawer(model=self.parameters.model, iterations=self.parameters.iterations)
        self.graphDrawer.initialize(self.data)

        if self.data.initialize:
            GP.GraphPainter.random(self.data)

        pygame.init()
        pygame.display.set_mode(self.displaySize, DOUBLEBUF | OPENGL)
        pygame.display.set_caption('Graph Viewer - Hemophilia data (full graph)')
        glEnable(GL_DEPTH_TEST)

        self.cam = Camera()

        #pygame.time.wait(1000)
        
        while True:
            curMousePos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    print('Quitting program...')
                    quit()

                if event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[1]: #Wheel click
                        pygame.event.set_grab(True)
                        oldMousePos = (curMousePos[0], curMousePos[1])
                        curMousePos = pygame.mouse.get_pos()
                        delta = tuple(map(lambda i, j: i - j, curMousePos, oldMousePos))
                        self.cam.dragOrbital(delta)
                    if not pygame.mouse.get_pressed()[1]: #Let go of wheel click
                        pygame.event.set_grab(False)

                    if pygame.mouse.get_pressed()[2]: #Right click
                        pygame.event.set_grab(True)
                        oldMousePos = (curMousePos[0], curMousePos[1])
                        curMousePos = pygame.mouse.get_pos()
                        delta = tuple(map(lambda i, j: i - j, curMousePos, oldMousePos))
                        self.cam.dragFly(delta)
                    if not pygame.mouse.get_pressed()[2]: #Let go of right click
                        pygame.event.set_grab(False)

                if event.type == pygame.MOUSEWHEEL:
                    if (event.y != 0):
                        self.cam.moveForwardBack(event.y)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, (self.displaySize[0] / self.displaySize[1]), 0.0001, 5000.0) # field of view, aspect ratio, near clipping plane, far clipping plane
            #glOrtho(0, self.displaySize[0], self.displaySize[1], 0, -1, 5000.0) # left, right, bottom, top, near, far

            glMatrixMode(GL_MODELVIEW)

            self.cam.activate()

            self.drawGraph()
            
            """if self.parameters.iterationsLeft > 0:
                self.graphDrawer.runLoop(self.data)
                self.parameters.iterationsLeft -= 1"""
            self.graphDrawer.runLoop(self.data)
            
            pygame.display.flip()
            pygame.time.wait(30)

    def drawGraph(self):
        for node in self.data.graph.nodes:
            self.drawNode(self.data.graph.nodes[node])
        
        for edge in self.data.graph.edges:
            self.drawEdge(edge)

        if self.parameters.renderCameraTarget:
            glPushMatrix()
            glTranslate(*(self.cam.target))
            q = gluNewQuadric()
            glColor3f(1.0, 1.0, 1.0)
            gluSphere(q, 0.15, 20, 20)
            glPopMatrix()

    def drawNode(self, node):
        glPushMatrix()
        glTranslatef(*(node['GV_position']))
        q = gluNewQuadric()
        glColor3f(*(node['GV_color']))
        gluSphere(q, 0.3, 20, 20)
        glPopMatrix()

    def drawEdge(self, edge):
        outPos = self.data.graph.nodes[edge[0]]['GV_position']
        inPos = self.data.graph.nodes[edge[1]]['GV_position']
        
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3f(1.0, 1.0, 1.0)
        #glColor3f(0.4, 0.5, 1.0)
        glVertex3f(*outPos)
        glVertex3f(*inPos)
        glEnd()
        glFlush()
        glPopMatrix()