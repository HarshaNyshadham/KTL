from __future__ import division
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import datetime
from source.models import pointTable


class exceltoDB:
  def __init__(self,filename):
    self.filename=filename
    self.scheduleData=[]
    self.playerData=[]


  def readExcel(self):
    #catch error coloumn name match
    df=pd.read_excel(self.filename,sheet_name='Sheet1',dtype={'Home': str, 'Away': str})
    for index,row in df.iterrows():
      self.scheduleData.append([row['Level'],row['Division'],row['Home'],row['Away'],row['Deadline'].date()])
    df=pd.read_excel(self.filename,sheet_name='Sheet2')
    for index,row in df.iterrows():
      self.playerData.append([row['Player Name']])

  def getScheduleData(self):
    return self.scheduleData

  def getPlayerData(self):
    return self.playerData

class updateScore:
  def __init__(self,p1s1,p1s2,p1s3,p2s1,p2s2,p2s3,player1,player2):
    self.played=1
    self.win=4
    self.loss=0
    self.tie=2
    self.bonus=1
    self.p1s1=p1s1
    self.p1s2=p1s2
    self.p1s3=p1s3
    self.p2s1=p2s1
    self.p2s2=p2s2
    self.p2s3=p2s3

    self.p1sum=float(p1s1)+float(p1s2)+float(p1s3)
    self.p2sum=float(p2s1)+float(p2s2)+float(p2s3)

    self.player1=player1
    self.player2=player2

  def updatePlayerScore(self):
    p1points=0
    p2points=0
    p1win=False
    p2win=False

    player1Record=pointTable.query.filter_by(player_id=self.player1).first()
    player2Record=pointTable.query.filter_by(player_id=self.player2).first()

    current_p1_xrating=player1Record.xrating
    current_p2_xrating=player2Record.xrating

    player1Record.played+=1
    player2Record.played+=1



    if((self.p1s1>self.p2s1 and self.p1s2>self.p2s2) or (self.p1s2>self.p2s2 and self.p1s3>self.p2s3) or (self.p1s1>self.p2s1 and self.p1s3>self.p2s3)):
      p1win=True
    else:
      p2win=True

    if(p1win):
      player1Record.points+=self.win
      player2Record.points+=self.bonus
      player1Record.win+=1
      player2Record.loss+=1
      player2Record.bonus+=1
    elif(p2win):
      player2Record.points+=self.win
      player1Record.points+=self.bonus
      player2Record.win+=1
      player1Record.loss+=1
      player1Record.bonus+=1


    #xrating calculation


    prob_p1_before=round(current_p1_xrating/(current_p1_xrating+current_p2_xrating),3)
    prob_p2_before=round(current_p2_xrating/(current_p1_xrating+current_p2_xrating),3)

    prob_p1_after=round(self.p1sum/(self.p1sum+self.p2sum),3)
    prob_p2_after=round(self.p2sum/(self.p1sum+self.p2sum),3)

    new_xrating_p1=current_p1_xrating+((prob_p1_after-prob_p1_before)*1000)
    new_xrating_p2=current_p2_xrating+((prob_p2_after-prob_p2_before)*1000)

    player1Record.xrating= new_xrating_p1
    player2Record.xrating= new_xrating_p2
    #print(current_p1_xrating,current_p2_xrating,self.p1sum,self.p2sum)
    #print(new_xrating_p1-current_p1_xrating,new_xrating_p2-current_p2_xrating)
















#     if(self.p1sum>self.p2sum):
#         p1points=self.win+self.bonus
#         p2points=self.bonus
#         player1Record.win+=1
#         player2Record.loss+=1
#     elif(self.p2sum>self.p1sum):
#         p1points=self.bonus
#         p2points=self.win+self.bonus
#         player2Record.win+=1
#         player1Record.loss+=1
#     elif(self.p1sum==self.p2sum):
#         p1points=self.tie
#         p2points=self.tie
#         player1Record.tie+=1
#         player2Record.tie+=1



#     player1Record.points+=p1points
#     player1Record.played+=self.played
#     player1Record.bonus+=self.bonus


#     player2Record.points+=p2points
#     player2Record.played+=self.played
#     player2Record.bonus+=self.bonus

#     #xratinf calculation
#     current_p1_xrating=player1Record.xrating
#     current_p2_xrating=player2Record.xrating

#     prob_p1_before=round(current_p1_xrating/(current_p1_xrating+current_p2_xrating),3)
#     prob_p2_before=round(current_p2_xrating/(current_p1_xrating+current_p2_xrating),3)

#     prob_p1_after=round(self.p1sum/(self.p1sum+self.p2sum),3)
#     prob_p2_after=round(self.p2sum/(self.p1sum+self.p2sum),3)

#     new_xrating_p1=current_p1_xrating+((prob_p1_after-prob_p1_before)*1000)
#     new_xrating_p2=current_p2_xrating+((prob_p2_after-prob_p2_before)*1000)

#     player1Record.xrating= new_xrating_p1
#     player2Record.xrating= new_xrating_p2
#     print(prob_p1_before,prob_p2_before,prob_p1_after,prob_p2_after,player1Record.xrating,player2Record.xrating)
#     print(round(1000/(1000+1000),3))
