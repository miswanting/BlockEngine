# coding=utf8
import configparser
import ctypes
import logging
import math
import os
import sys
import threading
import time

import pygame
from pygame.locals import *


def getResource(relative_path):
    if hasattr(sys, '_MEIPASS'):
        print('_MEIPASS', sys._MEIPASS, relative_path)
        base_path = sys._MEIPASS
    elif hasattr(sys, '_MEIPASS2'):
        print('_MEIPASS2', sys._MEIPASS2, relative_path)
        base_path = sys._MEIPASS2
    else:
        print('.', os.path.abspath("."), relative_path)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Game():
    """
    游戏的主干，涵盖了除了显示模块以外的所有数据处理模块。
    """
    
    def __init__(self):
        """
        必须载入
        """
        # self.hideCmdWindow()
        # self.showCmdWindow()
        self.isRunning = True
        fmt = '{0:^8}'
        logging.basicConfig(filename='Game.log', level=logging.DEBUG, filemode='w',
                            format='%(relativeCreated)6d[%(levelname).4s][%(threadName)-.10s]%(message)s',
                            datefmt='%I:%M:%S')
        self.init()
        pass
    
    def init(self):
        """
        初始化。载入config.conf；
        """
        self.startInputStar()
        config = configparser.ConfigParser()
        config.read(getResource('config.conf'))
        self.display = Display(config['init'])
        self.display.createWindow()
        self.display.startLoop()
    
    def startInputStar(self):
        def inputStar():
            while self.isRunning:
                cmd = input()
                print(cmd)
                if cmd == 'exit':
                    self.isRunning = False
                    self.display.isRunning = False
        
        star = threading.Thread(name='inputStar', target=inputStar)
        # star.start()
    
    def hideCmdWindow(self):
        """
        隐藏命令行窗口
        """
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd:
            ctypes.windll.user32.ShowWindow(hWnd, 0)
    
    def showCmdWindow(self):
        """
        显示已隐藏的命令行窗口
        """
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd:
            ctypes.windll.user32.ShowWindow(hWnd, 1)


class Display():
    """
    显示模块。负责图像处理、数据到图像的转换以及用户输入的捕获及提交。
    """
    
    def __init__(self, config):
        """
        初始化。
        """
        self.isRunning = True
        # Initialise screen
        pygame.init()
        self.config = {}
        self.config['squareSize'] = int(config['squareSize'])
        self.config['windowWidth'] = int(config['windowWidth'])
        self.config['windowHeight'] = int(config['windowHeight'])
        logging.info('屏幕分辨率：{}x{}'.format(
            self.config['windowWidth'], self.config['windowHeight']))
        self.config['screenMoveSpeed'] = int(config['screenMoveSpeed'])
        self.config['screenMoveArea'] = int(config['screenMoveArea'])
        self.config['windowMode'] = config['windowMode']
        self.config['windowTitle'] = config['windowTitle']
        self.SWMouse = (0, 0)
        self.map = Map(self.config)
        self.ui = UI(self.config)
        self.camera = Camera(self.config)
        # self.screen = pygame.display.set_mode((150, 50))
        # pygame.display.set_caption('Basic Pygame program')
        #
        # # Fill background
        # background = pygame.Surface(self.screen.get_size())
        # background = background.convert()
        # background.fill((250, 250, 250))
        #
        # # Display some text
        # font = pygame.font.Font(None, 36)
        # text = font.render("Hello There", 1, (10, 10, 10))
        # textpos = text.get_rect()
        # textpos.centerx = background.get_rect().centerx
        # background.blit(text, textpos)
        #
        # # Blit everything to the screen
        # self.screen.blit(background, (0, 0))
        # pygame.display.flip()
        #
        # # Event loop
        # while 1:
        #     for event in pygame.event.get():
        #         if event.type == QUIT:
        #             return
        #
        #     self.screen.blit(background, (0, 0))
        #     pygame.display.flip()
    
    def createWindow(self):
        """
        创建游戏显示主窗口。
        """
        logging.info('窗口模式：{}'.format(self.config['windowMode']))
        if self.config['windowMode'] == 'windowed':
            self.screen = pygame.display.set_mode((int(self.config['windowWidth']), int(self.config['windowHeight'])))
        elif self.config['windowMode'] == 'fullscreen':
            self.screen = pygame.display.set_mode((int(self.config['windowWidth']), int(self.config['windowHeight'])),
                                                  FULLSCREEN | DOUBLEBUF | HWSURFACE)
        pygame.display.set_caption(self.config['windowTitle'])
        self.screen.fill((255, 255, 255))
        newSurface = pygame.Surface((50, 50))
        newSurface.fill((255, 255, 255))
        pygame.draw.rect(newSurface, (0, 0, 0), (0, 0, 50, 50), 1)
        pygame.Surface.blit(self.screen, newSurface, (0, 0))
        pygame.Surface.blit(self.screen, newSurface, (50, 0))
        self.camera.setHWCamera((0, 0))
        pygame.display.flip()
    
    def moveSWMouse(self, pos):
        self.SWMouse = (int(self.SWMouse[0] + pos[0]), int(self.SWMouse[1] + pos[1]))
        # 控制不出界
        if self.SWMouse[0] > self.config['windowWidth']:
            self.SWMouse = (self.config['windowWidth'], self.SWMouse[1])
        if self.SWMouse[0] < 0:
            self.SWMouse = (0, self.SWMouse[1])
        if self.SWMouse[1] > self.config['windowHeight']:
            self.SWMouse = (self.SWMouse[0], self.config['windowHeight'])
        if self.SWMouse[1] < 0:
            self.SWMouse = (self.SWMouse[0], 0)
            # if self.SWMouse[0] > self.config['windowWidth']:
            #     self.camera.setSWCamera((self.camera.getSWCamera()[
            #                             0] + self.SWMouse[0] - self.config['windowWidth'], self.camera.getSWCamera()[1]))
            #     self.SWMouse = (self.config['windowWidth'], self.SWMouse[1])
            # if self.SWMouse[0] < 0:
            #     self.camera.setSWCamera(
            #         (self.camera.getSWCamera()[0] + self.SWMouse[0], self.camera.getSWCamera()[1]))
            #     self.SWMouse = (0, self.SWMouse[1])
            # if self.SWMouse[1] > self.config['windowHeight']:
            #     self.camera.setSWCamera((self.camera.getSWCamera()[0], self.camera.getSWCamera()[
            #                             1] + self.SWMouse[1] - self.config['windowHeight']))
            #     self.SWMouse = (self.SWMouse[0], self.config['windowHeight'])
            # if self.SWMouse[1] < 0:
            #     self.camera.setSWCamera(
            #         (self.camera.getSWCamera()[0], self.camera.getSWCamera()[1] + self.SWMouse[1]))
            #     self.SWMouse = (self.SWMouse[0], 0)
    
    def clickBlock(self, blockPos):
        logging.debug('clickAt {}'.format(blockPos))
        self.blockisSelected = True
        self.selectedBlock = blockPos
        self.ui.showBuildPanel()
        # newSurface = pygame.Surface(
        #     (self.config['squareSize'], self.config['squareSize']))
        # newSurface.fill((0, 255, 0))
        # self.map.setMapBlock(blockPos, newSurface)
    def startLoop(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == QUIT:
                    # print('QUIT')
                    logging.debug('QUIT')
                    self.isRunning = False
                elif event.type == KEYDOWN:
                    # print('KEYDOWN', event.key)
                    logging.debug('KEYDOWN {}'.format(event.key))
                    if event.key == 119:  # w
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0], pos[1] - 1))
                    elif event.key == 115:  # s
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0], pos[1] + 1))
                    elif event.key == 97:  # a
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0] - 1, pos[1]))
                    elif event.key == 100:  # d
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0] + 1, pos[1]))
                    elif event.key == 27:  # Esc
                        # print('QUIT')
                        logging.debug('QUIT')
                        self.isRunning = False
                        print(threading.active_count())
                        print(threading.enumerate())
                elif event.type == KEYUP:
                    # print('KEYUP', event.key)
                    logging.debug('KEYUP {}'.format(event.key))
                elif event.type == MOUSEMOTION:
                    # print('MOUSEMOTION', event.pos)
                    logging.debug('MOUSEMOTION {}'.format(event.pos))
                    self.moveSWMouse(
                        (event.pos[0] - self.config['windowWidth'] / 2, event.pos[1] - self.config['windowHeight'] / 2))
                    pygame.mouse.set_pos((self.config['windowWidth'] / 2, self.config['windowHeight'] / 2))
                    # print('SWMOUSEMOTION', self.SWMouse)
                    logging.debug('SWMOUSEMOTION {}'.format(self.SWMouse))
                elif event.type == MOUSEBUTTONDOWN:
                    # print('MOUSEBUTTONDOWN', event.button)
                    logging.debug('MOUSEBUTTONDOWN {}'.format(event.button))
                    if pygame.Rect(self.ui.upPanel.get_abs_offset(),
                                   (self.ui.upPanel.get_rect()[2], self.ui.upPanel.get_rect()[3])).collidepoint(
                        self.SWMouse):
                        pass
                    elif self.ui.isBuildPanelVisible:
                        if pygame.Rect(self.ui.buildPanel.get_abs_offset(), (
                                self.ui.buildPanel.get_rect()[2], self.ui.buildPanel.get_rect()[3])).collidepoint(
                            self.SWMouse):
                            pass
                        if pygame.Rect(self.ui.buildPanel.get_abs_offset(), (
                                self.ui.buildPanel.get_rect()[2], self.ui.buildPanel.get_rect()[3])).collidepoint(
                            self.SWMouse):
                            pass
                        else:
                            self.ui.isBuildPanelVisible = not self.ui.isBuildPanelVisible
                    else:
                        x = self.camera.getSWCamera()[0] - self.config['windowWidth'] / 2 + self.SWMouse[0]
                        y = self.camera.getSWCamera()[1] - self.config['windowHeight'] / 2 + self.SWMouse[1]
                        x = math.floor((x + self.config['squareSize'] / 2) / self.config['squareSize'])
                        y = math.floor((y + self.config['squareSize'] / 2) / self.config['squareSize'])
                        self.clickBlock((x, y))
                elif event.type == MOUSEBUTTONUP:
                    # print('MOUSEBUTTONUP', event.button)
                    logging.debug('MOUSEBUTTONUP {}'.format(event.button))
                elif event.type == ACTIVEEVENT:
                    # print('ACTIVEEVENT', event.gain)
                    logging.debug('ACTIVEEVENT {}'.format(event.gain))
                    if event.gain == 1:
                        pygame.mouse.set_visible(False)
                    elif event.gain == 0:
                        pygame.mouse.set_visible(True)
                    else:
                        pass
            # 屏幕滚动
            if self.SWMouse[0] > self.config['windowWidth'] - self.config['screenMoveArea']:
                self.camera.setSWCamera(
                    (self.camera.getSWCamera()[0] + self.config['screenMoveSpeed'], self.camera.getSWCamera()[1]))
            if self.SWMouse[0] < self.config['screenMoveArea']:
                self.camera.setSWCamera(
                    (self.camera.getSWCamera()[0] - self.config['screenMoveSpeed'], self.camera.getSWCamera()[1]))
            if self.SWMouse[1] > self.config['windowHeight'] - self.config['screenMoveArea']:
                self.camera.setSWCamera(
                    (self.camera.getSWCamera()[0], self.camera.getSWCamera()[1] + self.config['screenMoveSpeed']))
            if self.SWMouse[1] < self.config['screenMoveArea']:
                self.camera.setSWCamera(
                    (self.camera.getSWCamera()[0], self.camera.getSWCamera()[1] - self.config['screenMoveSpeed']))
            #
            pygame.Surface.blit(self.screen, self.map.renderMap(self.camera), (0, 0))
            self.camera.update()
            self.ui.update()
            pygame.Surface.blit(self.screen, self.ui.surface, (0, 0))
            #
            pygame.draw.circle(self.screen, (0, 0, 255), self.SWMouse, 10, 0)
            pygame.display.flip()
            # pygame.time.wait(20)
            time.sleep(0.02)


class Map():
    """
    地图管理类。注重数据储存与管理。
    """
    
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.map = {}
        self.defaultFont = pygame.font.Font(getResource('msyh.ttc'), 12)
    
    def setMapBlock(self, position, data):
        positionStr = '%s|%s' % (position[0], position[1])
        self.map[positionStr] = data
    
    def getMapBlock(self, position):
        positionStr = '%s|%s' % (position[0], position[1])
        # return self.map[positionStr]
        if positionStr in self.map.keys():
            return self.map[positionStr]
        else:
            newSurface = pygame.Surface((self.config['squareSize'], self.config['squareSize']))
            if position[0] == 0 or position[1] == 0:
                newSurface.fill((255, 0, 0))
            else:
                newSurface.fill((255, 255, 255))
            pygame.draw.rect(newSurface, (0, 0, 0), (0, 0, 50, 50), 1)
            text = self.defaultFont.render('(%s,%s)' % (position[0], position[1]), 1, (10, 10, 10))
            pygame.Surface.blit(newSurface, text, (0, 0))
            self.setMapBlock(position, newSurface)
            return self.map[positionStr]
    
    def renderMap(self, camera):
        # TODO(miswanting):Use subsurface
        """
        返回一个已渲染的地图Surface
        """
        # BUG(miswanting):优化
        renderSurfaceW = int(self.config['windowWidth'] / self.config['squareSize'] + 1) * self.config[
            'squareSize']  # 需要渲染的总大小
        renderSurfaceH = int(self.config['windowHeight'] / self.config['squareSize'] + 1) * self.config['squareSize']
        logging.info('地图渲染区域大小：{}x{}'.format(renderSurfaceW, renderSurfaceH))
        renderSurface = pygame.Surface((renderSurfaceW, renderSurfaceH))  # 未裁剪的渲染图
        blockList = self.getMapBlockPositionInSight(camera.SWCamera['TPosition'])  # 获取需要渲染的位置元组列表
        # 未裁剪的渲染Surface左上角方块所代表的TX
        renderSurfaceTX = math.floor((camera.SWCamera['TPosition'][0] - self.config['windowWidth'] / 2 + self.config[
            'squareSize'] / 2) / self.config['squareSize']) * self.config['squareSize']
        renderSurfaceTY = math.floor((camera.SWCamera['TPosition'][1] - self.config['windowHeight'] / 2 + self.config[
            'squareSize'] / 2) / self.config['squareSize']) * self.config['squareSize']
        for each in blockList:
            tPositionX = each[0] * self.config['squareSize']  # 每个Block的绝对TX
            # print('tPositionX', renderSurfaceTX)
            tPositionY = each[1] * self.config['squareSize']
            # 每个Block在未裁剪的渲染Surface上的相对TX
            renderPositionTX = tPositionX - renderSurfaceTX
            # print('renderPositionTX', renderPositionTX)
            renderPositionTY = tPositionY - renderSurfaceTY
            renderPositionHX = renderPositionTX + self.config['squareSize'] / 2
            renderPositionHY = renderPositionTY + self.config['squareSize'] / 2
            blockSurface = self.getMapBlock(each)
            pygame.Surface.blit(renderSurface, blockSurface, (renderPositionTX, renderPositionTY))
        dx = -(camera.SWCamera['TPosition'][0] - renderSurfaceTX -
               self.config['windowWidth'] / 2 + self.config['squareSize'] / 2)
        dy = -(camera.SWCamera['TPosition'][1] - renderSurfaceTY -
               self.config['windowHeight'] / 2 + self.config['squareSize'] / 2)
        screenSurface = pygame.Surface((self.config['windowWidth'], self.config['windowHeight']))
        renderSurface.convert()
        pygame.Surface.blit(screenSurface, renderSurface, (dx, dy))
        # pygame.image.save(renderSurface, 'a.bmp')
        # pygame.image.save(screenSurface, 'b.bmp')
        # print(renderSurfaceTX)
        return screenSurface
    
    def getMapBlockPositionInSight(self, TPosition):
        """
        获取需要被渲染的方块的位置（positiion）列表
        """
        TPositionLeft = TPosition[0] - self.config['windowWidth'] / 2
        TPositionRight = TPosition[0] + self.config['windowWidth'] / 2
        TPositionTop = TPosition[1] - self.config['windowHeight'] / 2
        TPositionBottom = TPosition[1] + self.config['windowHeight'] / 2
        
        positionXLeft = math.floor((TPositionLeft + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionXRight = math.floor((TPositionRight + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionYTop = math.floor((TPositionTop + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionYBottom = math.floor((TPositionBottom + self.config['squareSize'] / 2) / self.config['squareSize'])
        
        newList = []
        for x in range(positionXLeft, positionXRight + 1):
            for y in range(positionYTop, positionYBottom + 1):
                newList.append((x, y))
        # print(len(newList))
        logging.info('地图渲染方块区域：{}x{}'.format(positionXRight - positionXLeft + 1, positionYBottom - positionYTop + 1))
        logging.info('地图渲染方块数目：{}'.format(len(newList)))
        return newList
    
    def mapGenerate(self, size):
        pass
    
    def getMapBlockPositionListByDistance(self, position, distance):
        """
        获取与给定位置相距给定距离的所有的块距离列表
        """
        newList = []
        
        def tmp(a, b):
            if (a, b) in newList:
                pass
            else:
                newList.append((a, b))
        
        for each in range(0, distance):
            tmp(each, distance - each)
            tmp(each, each - distance)
            tmp(- each, distance - each)
            tmp(- each, each - distance)
        return newList


class Camera():
    """
    控制摄像机。
    """
    
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.HWCamera = {}
        self.HWCamera['position'] = (0, 0)
        self.SWCamera = {}
        self.SWCamera['TPosition'] = (0, 0)
    
    def setHWCamera(self, position):
        """
        HWCamera是Camera的Block坐标
        """
        self.HWCamera['position'] = position
    
    def getHWCamera(self):
        return self.HWCamera['position']
    
    def setSWCamera(self, position):
        self.SWCamera['TPosition'] = position
    
    def getSWCamera(self):
        """
        SWCamera是Camera的实际坐标
        """
        return self.SWCamera['TPosition']
    
    def update(self):
        # x = self.HWCamera['position'][0] * self.config['squareSize']
        # y = self.HWCamera['position'][1] * self.config['squareSize']
        # dx = x - self.SWCamera['TPosition'][0]
        # dy = y - self.SWCamera['TPosition'][1]
        # ndx = dx * 0.8
        # ndy = dy * 0.8
        # nx = x - ndx
        # ny = y - ndy
        # self.SWCamera['TPosition'] = (nx, ny)
        pass


class UI(object):
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.building = Building(config)
        self.isBuildPanelVisible = False
        self.defaultFont = pygame.font.Font(getResource('msyh.ttc'), 20)
        self.surface = pygame.Surface(
            (self.config['windowWidth'], self.config['windowHeight']), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.upPanel = self.surface.subsurface(self.config['squareSize'], 0,
                                               self.config['windowWidth'] - 2 * self.config['squareSize'],
                                               self.config['squareSize'])
        self.buildPanel = self.surface.subsurface(self.config['windowWidth'] - 2 * self.config['squareSize'],
                                                  self.config['squareSize'], 2 * self.config['squareSize'],
                                                  self.config['windowHeight'] - 2 * self.config['squareSize'])
        # self.upPanel = pygame.Surface(
        #     (self.config['windowWidth'] - 2 * self.config['squareSize'], self.config['squareSize']))
        # self.buildPanelRect =
        self.BuildingUnitList = []
    
    def showBuildPanel(self):
        self.buildPanel.fill((255, 255, 255))
        pygame.draw.rect(self.buildPanel, (0, 0, 0), (
            0, 0, 2 * self.config['squareSize'], self.config['windowHeight'] - 2 * self.config['squareSize']), 1)
        self.isBuildPanelVisible = True
        newBuildingUnit = self.buildPanel.subsurface(0, 0, self.config['squareSize'], self.config['squareSize'])
        self.BuildingUnitList.append(newBuildingUnit)
        pygame.Surface.blit(newBuildingUnit, self.building.getNewBuilding('青楼')['surface'], (0, 0, 0, 0))
    
    def update(self):
        #
        self.upPanel.fill((255, 255, 255))
        pygame.draw.rect(self.upPanel, (0, 0, 0),
                         (0, 0, self.config['windowWidth'] - 2 * self.config['squareSize'], self.config['squareSize']),
                         1)
        text = self.defaultFont.render('金币：%s' % 100, 1, (0, 0, 0))
        pygame.Surface.blit(self.upPanel, text, (
            self.config['squareSize'] / 2 - text.get_height() / 2,
            self.config['squareSize'] / 2 - text.get_height() / 2))
        #
        if self.isBuildPanelVisible:
            pass
        else:
            self.buildPanel.fill((0, 0, 0, 0))
            # pygame.Surface.blit(self.surface, self.upPanel,
            #                     (self.config['squareSize'], 0))


class Building(object):
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.defaultFont = pygame.font.Font(getResource('msyh.ttc'), 20)
    
    def getNewBuilding(self, name):
        newBuilding = {}
        newBuilding['name'] = name
        newBuilding['surface'] = pygame.Surface((self.config['squareSize'], self.config['squareSize']))
        newBuilding['surface'].fill((255, 255, 255))
        pygame.draw.rect(newBuilding['surface'], (0, 0, 0),
                         (0, 0, self.config['squareSize'], self.config['squareSize']), 1)
        text = self.defaultFont.render('%s' % name, 1, (0, 0, 0))
        pygame.Surface.blit(newBuilding['surface'], text, (
            self.config['squareSize'] / 2 - text.get_width() / 2,
            self.config['squareSize'] / 2 - text.get_height() / 2))
        return newBuilding


if __name__ == '__main__':
    game = Game()
