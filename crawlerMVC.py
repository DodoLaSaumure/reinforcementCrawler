from copy import deepcopy
import math
import random
import sys
import sys
import time
import time
import wx
import numpy as np

alpha =0.8
gamma = 0.95
DZETA= 0.3
dictActions = {0:"a-",1:"a+",2:"b-",3:"b+"}
class Crawler():
    def __init__(self,model):
        self.model = model
        self.cumulatedRewards = 0.
        self.Q = np.zeros(5*5*4)
        self.Q = self.Q.reshape(5,5,4)
        self.Rewards= np.ones(5*5*4)
        self.Rewards*=-1.
        self.Rewards = self.Rewards.reshape(5,5,4)
        self.stateA = self.model.stateA
        self.stateB = self.model.stateB
    def printFile(self,fichier,parray):
        fichier.write("a/b;;0; ; ;;1;;;;2;;;;3;;;;4;;;;")
        fichier.write("\n\n")
        for stateA in range(5):
            fichier.write(str(stateA))
            fichier.write(";;")
            for stateB in range(5):
                fichier.write(";")
                fichier.write("%.2f"%parray[stateA][stateB][0])#a-
                fichier.write(";")
                fichier.write(";")
                fichier.write(";")
            fichier.write("\n;")
            for stateB in range(5):
                fichier.write(";")
                fichier.write("%.2f"%parray[stateA][stateB][2])#b-
                fichier.write(";")
                fichier.write(self.maxAllowedAction(stateA,stateB,parray))
                fichier.write(";")
                fichier.write("%.2f"%parray[stateA][stateB][3])#b+
                fichier.write(";")
            fichier.write("\n;")
            for stateB in range(5):
                fichier.write(";")
                fichier.write(";")
                fichier.write("%.2f"%parray[stateA][stateB][1])#a+
                fichier.write(";")
                fichier.write(";")
            fichier.write("\n")
            fichier.write("\n")
    def prints(self,filename):
        fichier = open(filename,"w")
        parray = self.Rewards
        self.printFile(fichier, parray)
        parray = self.Q
        self.printFile(fichier, parray)
        fichier.close()
    
    def parsefile(self):
        fichier = open("tischReward.csv","r")
        header = fichier.readline().replace("\n","").split(",")
        print(header)
        datas =fichier.readlines()
        fichier.close()
        for data in datas :
            line = data.replace("\n","").split(",")
            stateA = int(line[0])-1
            stateB=int(line[1])-1
            [amoins,aplus,bmoins,bplus]= line[2:]
            self.Rewards[stateA][stateB]=[float(amoins),float(aplus),float(bmoins),float(bplus)]
#             print (data.replace("\n","").split(","))
    def getAvailableActionsList(self,stateA,stateB):
        available_actionsIndexes= [0,1,2,3]
        if stateA == 0 :
            available_actionsIndexes.remove(0)
        if stateA == 4 :
            available_actionsIndexes.remove(1)
        if stateB == 0 :
            available_actionsIndexes.remove(2)
        if stateB == 4 :
            available_actionsIndexes.remove(3)
        return available_actionsIndexes
#         self.transforActionIndexListToActionKeysList(available_actionsIndexes)
        
    def transforActionIndexListToActionKeysList(self,actions):
        newlist = []
        for indexAction in actions:
            newlist.append(dictActions.get(indexAction))
        return newlist
    def chooseRandomAction(self,actionList):
        index = int (random.random()*float(len(actionList)))
        print ("random Action",dictActions.get(actionList[index]))
        return actionList[index]#,self.Q[self.stateA][self.stateB][actionList[index]]]
    def chooseBestAction(self,actionList,curStateA,curStateB):
        listQs = []
        for action in actionList :
            listQs.append(self.Q[curStateA][curStateB][action])
#         listQs = self.Q[self.stateA][self.stateB] #Q0 Q1 Q2 Q3
        max_value =np.max(listQs)
        max_index = np.where(np.array(listQs) == max_value)[0]
        if max_index.shape[0] > 1:
            max_index = int(np.random.choice(max_index, size = 1))
        else:
            max_index = int(max_index)
        action =actionList[max_index]
        print ("best Action",dictActions.get(action),"max value = ",max_value,"max valueb = ",self.Q[self.stateA][self.stateB][action])
        return action#,max_value]

    def getReward(self,action,stateA,stateB):
        return self.Rewards[stateA][stateB][action]

    def getNewState(self,action,stateA,stateB):
        newStateA = stateA
        newStateB = stateB
        if action == 0: #a-
            newStateA -=1
        if action == 1:
            newStateA +=1
        if action == 2 :
            newStateB -=1
        if action == 3 :
            newStateB+=1
        if newStateA <0 or newStateB<0 or newStateA > 4 or newStateB> 4:
            print ("ERRRRORRRRR")
            sys.exit()
        return [newStateA,newStateB]
    def setState(self,stateA,stateB):
        self.stateA = stateA
        self.stateB = stateB
    def maxAllowedAction(self,stateA,stateB,table,verbose = False):
        available_Actions = self.getAvailableActionsList(stateA, stateB)
        listVals = []
        for action in available_Actions :
            listVals.append(table[stateA][stateB][action])
        max_value =np.max(listVals)
        if verbose :
            print("available_Actions",available_Actions)
            print("listVals",listVals)
            print("max_value",max_value)
        max_index = np.where(np.array(listVals) == max_value)[0][0]
        action =available_Actions[max_index]
        return dictActions.get(action)#,max_value]
        
    def maxQ(self,stateA,stateB):
        allowedActions = self.getAvailableActionsList(stateA, stateB)
        listQs =  []
        for action in allowedActions:
            listQs.append(self.Q[stateA][stateB][action])
        max_value =np.max(listQs)
        return max_value
    def updateQ(self,reward,curStateA,curStateB,newStateA,newStateB,action):
        newMaxQ = self.maxQ(newStateA,newStateB)
        curQ = self.Q[curStateA][curStateB][action]
        self.Q[curStateA][curStateB][action]+=alpha*(reward+gamma*(newMaxQ-curQ))#-self.Q[self.stateA][self.stateB][action]))
    def updateFullQ(self):
        copyQ = deepcopy(self.Q)
        for stateA in range(5):
            for stateB in range(5):
                available_actions= self.getAvailableActionsList(stateA, stateB)
                for action in available_actions :
                    [newStateA,newStateB]= self.getNewState(action, stateA, stateB)
                    newMaxQ = self.maxQ(newStateA,newStateB)
                    curQ = copyQ[stateA][stateB][action]
                    newMaxQ=self.maxQ(newStateA,newStateB)
                    copyQ[stateA][stateB][action]+= alpha*(self.Rewards[stateA][stateB][action]+gamma*(newMaxQ-curQ))
        self.Q = copyQ
    def crawl(self,dzeta):
        curStateA = self.stateA
        curStateB = self.stateB
        available_Actions = self.getAvailableActionsList(curStateA, curStateB)
        epsilon = random.random()
        if epsilon <dzeta:
            action = self.chooseRandomAction(available_Actions)
        else :
            action = self.chooseBestAction(available_Actions,curStateA,curStateB)
        [newStateA,newStateB] = self.getNewState(action,curStateA,curStateB)
        [reward,newpos] = self.model.applyMoveAndGetRewardPos(newStateA,newStateB)
        self.Rewards[curStateA][curStateB][action]=reward
        self.updateFullQ()
        maxi = np.max(abs(self.Q))
        if maxi > 1000.:
            self.Q = 0.01*self.Q
        self.setState(newStateA,newStateB)
        self.cumulatedRewards+=reward
        return [reward,newpos]
        
class Model():
    def __init__(self):
        self.la = 100 #cm
        self.lb= 50 #cm
        self.stateA = 2
        self.stateB = 2
    def _setState(self,newState):
        self.stateA = newState[0]
        self.stateB = newState[1]
    def _getAngles(self,stateA,stateB):
        angleA = int(2-int(stateA))*15.#degres par rapport a l'horizontale
        angleB=int(int(stateB)-2)*15.#degres par rapport a la verticale
        return [angleA,angleB]
    def _getABpos(self,stateA,stateB):
        [angleA,angleB] = self._getAngles(stateA, stateB)
        Ax = self.la*math.cos(angleA*math.pi/180.)
        Ay = self.lb+self.la*math.sin(angleA*math.pi/180.)
        Bx = Ax + self.lb* math.sin(angleB*math.pi/180.)
        By = Ay -self.lb* math.cos(angleB*math.pi/180.)
        return [int(Ax),int(Ay),int(Bx),int(By)]
    def applyMoveAndGetRewardPos(self,newStateA,newStateB):
        lastPos = self._getABpos(self.stateA, self.stateB)
        [lastAx,lastAy,lastBx,lastBy]=lastPos
        newPos = self._getABpos(newStateA, newStateB)
        [newAx,newAy,newBx,newBy]=newPos
        reward = 0.
        if lastAy < self.lb :
            reward = lastBx-newBx
        self._setState([newStateA,newStateB])
        return [reward,newPos]
        
class Controler():
    def __init__(self,parent):
        self.cumulatedRewards = 0.
        self.parent = parent
        self.model = Model()
        self.model.applyMoveAndGetRewardPos(0, 0)
        self.crawler = Crawler(self.model)
    def crawl(self):
        index = 0
#         while True :
        while index <2000:
            dzeta = DZETA
            [reward,newPos]=self.crawler.crawl(dzeta)
            self.cumulatedRewards +=reward
            self.parent.draw(newPos,self.cumulatedRewards)
            index +=1
            print("INDEX",index)
        self.crawler.prints("crawlerMVC.csv")

class CrawlerFrame(wx.Frame):
    def __init__(self, parent=None):
        super(CrawlerFrame, self).__init__(parent, title="Crawler", 
            size=(800,600), 
            style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        view = View(self)
class View(wx.Window): 
    def __init__(self, parent): 
        self.parent = parent
        super(View, self).__init__(parent, 
            style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.initDrawing()
        self.initBuffer()
        self.bindEvents()
    def bindEvents(self):
        self.Bind(wx.EVT_LEFT_DOWN,                      self.control)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_SIZE, self.onSize)          # Prepare for redraw
    def control(self,event):
        self.controler.crawl()
    def initDrawing(self):
        self.SetBackgroundColour('BLACK')
        self.controler = Controler(self)
    def initBuffer(self):
        ''' Initialize the bitmap used for buffering the display. '''
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(width=size.width, height=size.height)
#         self.buffer = wx.EmptyBitmap(size.width, size.height)#deprecated
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.reInitBuffer = False
    def onSize(self, event):
        ''' Called when the window is resized. We set a flag so the idle
            handler will resize the buffer. '''
        self.reInitBuffer = True

    def onIdle(self, event):
        ''' If the size was changed then resize the bitmap used for double
            buffering to match the window size.  We do it in Idle time so
            there is only one refresh after resizing is done, not lots while
            it is happening. '''
        if self.reInitBuffer:
            self.initBuffer()
            self.Refresh(False)
    def onPaint(self, event):
        ''' Called when the window is exposed. '''
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer)
    # Other methods
    def draw(self,pos,cumulatedRewards):
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
#         dc = wx.BufferedDC(None, self.buffer)
        [Ax,Ay,Bx,By] = pos
        [Ax,Ay,Bx,By]=[100+Ax,100-Ay,100+Bx,100-By]
        dc.Clear()
        pen = wx.Pen(wx.Colour(255,0,0),width=3) 
        dc.SetPen(pen) 
        dc.DrawLine(0,50,Ax,Ay) 
        pen = wx.Pen(wx.Colour(0,0,255),width=3) 
        dc.SetPen(pen) 
        dc.DrawLine(Ax,Ay,Bx,By) 
        self.drawCumulatedRewards(cumulatedRewards,dc)
        print( "cumulatedRewards",cumulatedRewards)
#         print(Ax,Ay,Bx,By)
        time.sleep(0.1)
    def drawCumulatedRewards(self,cumulatedRewards,dc):
        lines = [[0,0,1000,0]]
        for i in range(5):
            lines.append([i*200,0,i*200,10])
        pen = wx.Pen(wx.Colour(0,255,0),width=2) 
        dc.SetPen(pen) 
        for line in lines :
            x1,y1,x2,y2 = line
            dc.DrawLine(x1-cumulatedRewards,y1+105,x2-cumulatedRewards,y2+105)

if __name__ == '__main__':
    app = wx.App() 
    frame = CrawlerFrame()
    frame.Show()
    app.MainLoop()
    sys.exit()



