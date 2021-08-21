import pygame
class SpriteSheet:
    def __init__(self, file, rows, collums):
        self.sheet = pygame.image.load(file)
        self.rows, self.collums, self.total = rows, collums, rows*collums
        self.rect = self.sheet.get_rect()
        
        self.cellWidth, self.cellHeight = self.rect.width/collums, self.rect.height/rows
        self.cells = list([(int(index%collums*self.cellWidth), int(index//collums*self.cellHeight),
                            self.cellWidth,self.cellHeight)for index in range(self.total)])
        h,w = -self.cellHeight/2, -self.cellWidth/2
        self.offset = [(0,0),(w,0),(2*w,0),(0,h),(w,h),(2*w,h),(0,2*h),(w,2*h),(2*w,2*h),(w/2,h)]
    def draw(self,surface, cellIndex, x,y, offset = 0, scale = 64):
        if scale != self.sheet.get_rect()[2]/self.collums:
            image = pygame.transform.scale(self.sheet, (scale*self.collums, scale*self.rows))
            scalar = scale/(self.sheet.get_rect()[2]/self.collums)
            cell = self.cells[cellIndex][0]*scalar, self.cells[cellIndex][1]*scalar,\
                   self.cells[cellIndex][2]*scalar, self.cells[cellIndex][3]*scalar
            return surface.blit(image,(x+scalar*self.offset[offset][0],y+self.offset[offset][1]*scalar), cell)
        else:
            return surface.blit(self.sheet,(x+self.offset[offset][0],y+self.offset[offset][1]),self.cells[cellIndex])
    def remake(self, scale):
        self.sheet = pygame.transform.scale(self.sheet, (int(scale*self.collums), int(scale*self.rows)))
        self.rect = self.sheet.get_rect()
        
        self.cellWidth, self.cellHeight = self.rect.width/self.collums, self.rect.height/self.rows
        self.cells = list([(int(index%self.collums*self.cellWidth), int(index//self.collums*self.cellHeight),
                            self.cellWidth,self.cellHeight)for index in range(self.total)])
        h,w = -self.cellHeight/2, -self.cellWidth/2
        self.offset = [(0,0),(w,0),(2*w,0),(0,h),(w,h),(2*w,h),(0,2*h),(w,2*h),(2*w,2*h),(w/2,h)]