import pygame

from pygame import *

class GameRepresentation:
    def __init__(self, isolation):
        self.game = isolation
   
        pygame.init()

        size = width, height = 700, 700
        screen = pygame.display.set_mode(size)

        background_image = pygame.image.load("./images/board.jpg").convert()

        pygame.event.pump()

        screen.blit(background_image, (0, 0))
        
        pygame.display.flip()
        pygame.display.update()
    
    def draw(self):
        theSquares = []
        initXLoc = 150
        startX, startY, editable, number = 150, 150, "N", 0
        game_squares = [x for x in self.game.to_string().split('|') if x != ' ' and x != ' \n\r ']
        legal = self.game.get_legal_moves()

        for y in range(7):
            startY = (y * 47) + initXLoc
            for x in range(7):
                startX = (x * 47) + initXLoc
                sq = game_squares[x*7+y]               
                string_number = sq
                if (x,y) in legal:
                    string_number = '^{0}'.format(legal.index((x,y)))        
                theSquares.append(Square(string_number, startX, startY, x, y))       
        for num in theSquares:
            num.draw()
        
        pygame.display.flip()
        pygame.display.update()

    #leave game showing until closed by user
    def game_loop(self):
        self.draw()
        for event in pygame.event.get():
            self.pp(event)        
    
            if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
    
    def pp(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()    
            print(pos)

class GraphRepresentation:
    def __init__(self, isolation):
        self.game = isolation
   
        pygame.init()

        size = width, height = 700, 700
        screen = pygame.display.set_mode(size)

        background_image = pygame.image.load("./images/board.jpg").convert()

        pygame.event.pump()

        screen.blit(background_image, (0, 0))
        
        pygame.display.flip()
        pygame.display.update()
    
    def draw(self):
        theSquares = []
        initXLoc = 0
        startX, startY, editable, number = 150, 150, "N", 0
        
        visited = []
        visited.append((0,0))        

        while v in visited:
            v = visited.pop()
            theSquares.append()

        game_squares = [x for x in self.game.to_string().split('|') if x != ' ' and x != ' \n\r ']
        legal = self.game.get_legal_moves()

        for y in range(7):
            startY = (y * 47) + initXLoc
            for x in range(7):
                startX = (x * 47) + initXLoc
                sq = game_squares[x*7+y]               
                string_number = sq
                if (x,y) in legal:
                    string_number = 'l{0}'.format(legal.index((x,y)))        
                theSquares.append(Square(string_number, startX, startY, x, y))       
        for num in theSquares:
            num.draw()
        
        pygame.display.flip()
        pygame.display.update()

    #leave game showing until closed by user
    def game_loop(self):
        self.draw()
        for event in pygame.event.get():
            self.pp(event)        
    
            if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
    
    def pp(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()    
            print(pos)

class Square:
    """A square class."""
    def __init__(self, number=None, offsetX=0, offsetY=0, xLoc=0, yLoc=0):
        self.font = pygame.font.SysFont('opensans', 21)

        if number == '   ': 
            self.color = (210, 210, 210)  
            number = '{0},{1}'.format(xLoc, yLoc)
            self.font = pygame.font.SysFont('opensans', 15)
        elif '!' in number: 
            number = number.replace('!', '')
            self.color = (1, 50, 255)  
        elif '@' in number: 
            number = number.replace('@', '')
            self.color = (240, 50, 1)  
        elif '^' in number: 
            number = '{0},{1}({2})'.format(xLoc, yLoc, number.replace('l', ''))
            self.font = pygame.font.SysFont('opensans', 15)
            self.color = (205, 205, 255)  
        else: 
            number = ''
            self.color = (130, 130, 130)  

        # print("FONTS", pygame.font.get_fonts())
        
        self.text = self.font.render(number, 1, (255, 255, 255))
        self.textpos = self.text.get_rect()
        self.textpos = self.textpos.move(offsetX + 15, offsetY + 17)

        self.xLoc = xLoc
        self.yLoc = yLoc
        self.offsetX = offsetX
        self.offsetY = offsetY

    def draw(self):
        screen = pygame.display.get_surface()
        self.fill_rectangle(screen, (self.offsetX, self.offsetY, 45, 45), self.color)

        # screen.blit(self.collide, self.collideRect)
        screen.blit(self.text, self.textpos)
       
    def fill_rectangle(self, surface,rect,color):
        rect         = Rect(rect)
        color        = Color(*color)
        alpha        = color.a
        color.a      = 0
        pos          = rect.topleft
        rect.topleft = 0,0
        rectangle    = Surface(rect.size,SRCALPHA)

        rectangle.fill((0,0,0),rect.inflate(0,0))
        rectangle.fill((0,0,0),rect.inflate(0,0))

        rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
        rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)


        return surface.blit(rectangle,pos)

  