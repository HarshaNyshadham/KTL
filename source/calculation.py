from __future__ import division
import pandas as pd
from pandas import ExcelWriter,DataFrame
from pandas import ExcelFile
from datetime import datetime
from source.models import pointTable,score,user
from datetime import datetime,date


class exceltoDB:
  def __init__(self,filename):
    self.filename=filename
    self.scheduleData=[]
    self.playerData=['super']


  def readExcel(self):
    #catch error coloumn name match
    try:

      df=pd.read_excel(self.filename,sheet_name='Sheet1')#dtype={'Home': str, 'Away': str})
      for index,row in df.iterrows():
        self.scheduleData.append([row['Level'],row['Division'],row['Home'],row['Away'],row['Deadline'].date(),row['Score']])
        self.playerData.append(row['Home'])
        self.playerData.append(row['Away'])





#       df=pd.read_excel(self.filename,sheet_name='Sheet2')
#       for index,row in df.iterrows():
#         self.playerData.append([row['Player Name']])
    except:
      return 'error'

  def getScheduleData(self):
    return self.scheduleData

  def getPlayerData(self):
    tempset=set(self.playerData)
    self.playerData=list(tempset)
    return self.playerData

  def writeExcel(self):
    PTdata=pointTable.query.all()
    scoredata=score.query.all()
    userdata=user.query.all()

    sheet1data={'Home':[],'Away':[],'Deadline':[],'Score':[],'Division':[],'Level':[]}
    sheet2data={'Player':[],'Played':[],'Win':[],'Loss':[],'Tie':[],'Bonus':[],'Points':[],'Xrating':[],'Gamesplayed':[],'Gameswon':[],'Set1Played':[],'Set1Won':[],
                'Set2Played':[],'Set2Won':[],'Set3Played':[],'Set3Won':[]}
    sheet3data={'Username':[],'PlayerID':[],'Email':[],'Phone':[],'Password':[]}

    for elem in scoredata:
      sheet1data['Home'].append(elem.player_id1)
      sheet1data['Away'].append(elem.player_id2)
      sheet1data['Deadline'].append(elem.deadline)
      sheet1data['Score'].append(elem.score)
      sheet1data['Division'].append(elem.division)
      sheet1data['Level'].append(elem.level)
    for elem in PTdata:
      sheet2data['Player'].append(elem.player_id)
      sheet2data['Played'].append(elem.played)
      sheet2data['Win'].append(elem.win)
      sheet2data['Loss'].append(elem.loss)
      sheet2data['Tie'].append(elem.tie)
      sheet2data['Bonus'].append(elem.bonus)
      sheet2data['Points'].append(elem.xrating)
      sheet2data['Xrating'].append(elem.points)
      sheet2data['Gamesplayed'].append(elem.gamesplayed)
      sheet2data['Gameswon'].append(elem.gameswon)
      sheet2data['Set1Played'].append(elem.set1played)
      sheet2data['Set1Won'].append(elem.set1won)
      sheet2data['Set2Played'].append(elem.set2played)
      sheet2data['Set2Won'].append(elem.set2won)
      sheet2data['Set3Played'].append(elem.set3played)
      sheet2data['Set3Won'].append(elem.set3won)

    for elem in userdata:
      sheet3data['Username'].append(elem.username)
      sheet3data['PlayerID'].append(elem.firstName)
      sheet3data['Email'].append(elem.email)
      sheet3data['Phone'].append(elem.phone)
      sheet3data['Password'].append(elem.password_hash)

    df=DataFrame(sheet1data,columns=['Home','Away','Deadline','Score','Division','Level'])
    df1=DataFrame(sheet2data,columns=['Player','Played','Win','Loss','Tie','Bonus','Points','Xrating','Gamesplayed','Gameswon','Set1Played','Set1Won','Set2Played','Set2Won','Set3Played','Set3Won'])
    df2=DataFrame(sheet3data,columns=['Username','PlayerID','Email','Phone','Password'])

    EXCEL_NAME=str(datetime.now().date())+'.xlsx'

    with ExcelWriter(self.filename+EXCEL_NAME) as writer:
      df.to_excel(writer,sheet_name='Score')
      df1.to_excel(writer,sheet_name='Point Table')
      df2.to_excel(writer,sheet_name='Users')
    print(str(datetime.now().date()))
    #print(df)

class updateScore:
  def __init__(self,p1s1,p1s2,p1s3,p2s1,p2s2,p2s3,p1forefeit,p2forefeit,player1,player2):

    # ******* set point system here *********
    self.played=1
    self.win=4
    self.loss=0
    self.tie=2
    self.bonus=1
    self.setbonus=1
    # ****************************************
    self.Xchange_p1=0;
    self.Xchange_p2=0;

    self.p1s1=p1s1
    self.p1s2=p1s2
    self.p1s3=p1s3
    self.p2s1=p2s1
    self.p2s2=p2s2
    self.p2s3=p2s3

    self.p1sum=float(p1s1)+float(p1s2)+float(p1s3)
    self.p2sum=float(p2s1)+float(p2s2)+float(p2s3)

    self.p1forefeit=p1forefeit
    self.p2forefeit=p2forefeit

    self.player1_name=player1
    self.player2_name=player2

    self.player1Record=pointTable.query.filter_by(player_id=player1).first()
    self.player2Record=pointTable.query.filter_by(player_id=player2).first()

  def getP1_Xchange(self):
    return self.Xchange_p1

  def getP2_Xchange(self):
    return self.Xchange_p2

  def updatePlayerScore(self):
    p1points=0
    p2points=0
    p1win=False
    p2win=False







#     if((self.p1s1>self.p2s1 and self.p1s2>self.p2s2) or (self.p1s2>self.p2s2 and self.p1s3>self.p2s3) or (self.p1s1>self.p2s1 and self.p1s3>self.p2s3)):
#       p1win=True
#     else:
#       p2win=True
#   code for forefeit returns from here
    if(self.p1s1=='0' and self.p2s1=='0' and self.p1s2=='0' and self.p2s2=='0' and self.p1s3=='0' and self.p2s3=='0'):
      if(self.p1forefeit and self.p2forefeit):
        return False
      elif(self.p1forefeit):
        self.player2Record.points+=self.win
        self.player2Record.win+=1
        self.player1Record.loss+=1
        self.player2Record.played+=1
        self.player1Record.played+=1
        return self.player2_name
      elif(self.p2forefeit):
        self.player1Record.points+=self.win
        self.player1Record.win+=1
        self.player2Record.loss+=1
        self.player1Record.played+=1
        self.player2Record.played+=1
        return self.player1_name
    elif(not self.p1forefeit and  not self.p2forefeit):
      if(self.p1s1>self.p2s1 and self.p1s2>self.p2s2):
        p1win=True
      elif(self.p1s1<self.p2s1 and self.p1s2<self.p2s2):
          p2win=True
      elif(self.p1s3>self.p2s3):
        p1win=True
        self.player2Record.points+=self.setbonus
        self.player2Record.bonus+=1
      elif(self.p1s3<self.p2s3):
        p2win=True
        self.player1Record.points+=self.setbonus
        self.player1Record.bonus+=1
      elif(self.p1s1=='1' and self.p2s1=='1' and self.p1s2=='1' and self.p2s2=='1' and self.p1s3=='1' and self.p2s3=='1'):
        self.player1Record.points+=self.tie
        self.player1Record.tie+=1
        self.player2Record.points+=self.tie
        self.player2Record.tie+=1
        return 'TIE'
      elif((self.p1s1<=5 and self.p2s1<=5) or (self.p1s2<=5 and self.p2s2<=5) or (self.p1s3<=5 and self.p2s3<=5)):
        return False
      else:
        return False
    else:
      return False

    current_p1_xrating=self.player1Record.xrating
    current_p2_xrating=self.player2Record.xrating


    #xrating calculation


    prob_p1_before=round(current_p1_xrating/(current_p1_xrating+current_p2_xrating),3)
    prob_p2_before=round(current_p2_xrating/(current_p1_xrating+current_p2_xrating),3)

    prob_p1_after=round(self.p1sum/(self.p1sum+self.p2sum),3)
    prob_p2_after=round(self.p2sum/(self.p1sum+self.p2sum),3)

    new_xrating_p1=current_p1_xrating+((prob_p1_after-prob_p1_before)*1000)
    new_xrating_p2=current_p2_xrating+((prob_p2_after-prob_p2_before)*1000)

    self.Xchange_p1=new_xrating_p1-current_p1_xrating
    self.Xchange_p2=new_xrating_p2-current_p2_xrating

    self.player1Record.xrating= new_xrating_p1
    self.player2Record.xrating= new_xrating_p2
    #print(current_p1_xrating,current_p2_xrating,self.p1sum,self.p2sum)
    #print(new_xrating_p1-current_p1_xrating,new_xrating_p2-current_p2_xrating)

    #******* point calculation ******

    self.player1Record.played+=1
    self.player2Record.played+=1

    #**** games *****
    self.player1Record.gamesplayed+=int(self.p1sum+self.p2sum)
    self.player2Record.gamesplayed+=int(self.p1sum+self.p2sum)

    self.player1Record.gameswon+=int(self.p1sum)
    self.player2Record.gameswon+=int(self.p2sum)

    #**** set1 *****
    self.player1Record.set1played+=int(self.p1s1)+int(self.p2s1)
    self.player2Record.set1played+=int(self.p1s1)+int(self.p2s1)

    self.player1Record.set1won+=int(self.p1s1)
    self.player2Record.set1won+=int(self.p2s1)

    #**** set2 *****
    self.player1Record.set2played+=int(self.p1s2)+int(self.p2s2)
    self.player2Record.set2played+=int(self.p1s2)+int(self.p2s2)

    self.player1Record.set2won+=int(self.p1s2)
    self.player2Record.set2won+=int(self.p2s2)

    #**** set3 *****
    self.player1Record.set3played+=int(self.p1s3)+int(self.p2s3)
    self.player2Record.set3played+=int(self.p1s3)+int(self.p2s3)

    self.player1Record.set3won+=int(self.p1s3)
    self.player2Record.set3won+=int(self.p2s3)

    if(p1win):
      self.player1Record.points+=self.win
      self.player2Record.points+=self.bonus
      self.player1Record.win+=1
      self.player2Record.loss+=1
      self.player2Record.bonus+=1
      return self.player1_name
    elif(p2win):
      self.player2Record.points+=self.win
      self.player1Record.points+=self.bonus
      self.player2Record.win+=1
      self.player1Record.loss+=1
      self.player1Record.bonus+=1
      return self.player2_name

















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
