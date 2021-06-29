from source import app,db,admin,mail
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from source.models import user,score,pointTable,adminView
from source.forms import LoginForm,RegistrationForm,ScoreForm,UploadForm,FilterForm,addPlayerForm,PointTableForm,ForgotpwdForm, FVLScoreForm,FVLTeamFilter
from source.calculation import exceltoDB,updateScore
from datetime import datetime,date,timedelta
from dateutil import tz
from sqlalchemy import and_,or_,desc
from flask_mail import Message
import pandas as pd
from pandas import ExcelWriter,DataFrame,ExcelFile
import string

#EXCEL_PATH='uploads/'
EXCEL_PATH='/home/katytennisleague/mysite/KTL/source/uploads'
SEASON_NAME=''
#DOWNLOAD_PATH='downloads/'
DOWNLOAD_PATH='/home/katytennisleague/mysite/KTL/source/downloads/'
FVL_PlayedId=["Cross Creek Smashers","Gully Boyz","Katy Boyz","Katy Defenders","Katy Dragons","Katy Legends","Katy Sparks","Katy Whackers","Katy Whackers2","Wood Warriors","Katy Falcons","Katy Boyz2","Underdogs","Katy Bulls"]
FVL_fileName='/home/katytennisleague/mysite/KTL/uploads/FVL_spring2020.xlsx'
FVL_playerlist='/home/katytennisleague/mysite/KTL/uploads/FVL_playerlist.xlsx'
FVL_PoolA=["Katy Boyz","Katy Defenders","Katy Dragons","Katy Legends","Katy Whackers","Wood Warriors","Katy Falcons"]
FVL_PoolB=["Cross Creek Smashers","Gully Boyz","Katy Sparks","Katy Whackers2","Katy Boyz2","Underdogs","Katy Bulls"]
TeamDict={"Cross Creek Smashers":0,"Gully Boyz":1,"Katy Boyz":2,"Katy Defenders":3,"Katy Dragons":4,"Katy Legends":5,"Katy Sparks":6,"Katy Whackers":7,"Katy Whackers2":8,"Wood Warriors":9,"Katy Falcons":10,"Katy Boyz2":11,"Underdogs":12,"Katy Bulls":13}
@app.route('/')
@app.route('/index')
def index():
  print(current_user)
  if current_user.is_authenticated:
    return render_template("home.html",data=current_user,tabledata=score.query.filter((or_(score.player_id1==current_user.firstName,
                                                                                          score.player_id2==current_user.firstName))).order_by(score.deadline).all(),PTdata=pointTable.query.filter_by(player_id=current_user.firstName).first())
  else:
    return render_template("home.html",data=current_user)

# # @app.route('/admin')
# # def adminpage():
# #     admin.add_view(adminView(user,db.session))
# #     admin.add_view(adminView(score,db.session))

@app.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        userLogged = user.query.filter_by(username=form.username.data).first()
        print(form.username.data)
        if userLogged is None or not userLogged.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(userLogged, remember=form.remember_me.data)
        print(current_user)
        if(userLogged.firstName in FVL_PlayedId):
          return redirect(url_for('FVLindex'))
        else:
          print(current_user)
          return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/forgotpwd',methods=['GET', 'POST'])
def forgotpwd():

    form =  ForgotpwdForm()
    form.firstname.choices=[(u[0],u[0]) for u in user.query.with_entities(user.firstName).all()]

    if form.validate_on_submit():
      userData=user.query.filter_by(firstName=form.firstname.data).first()
      #print(userData.email)
      if userData.email != None:
        flash('link to change password has been sent to you email, check spam folder aswell')
        msg=Message("hello",sender="katytennisleague@gmail.com",recipients=[userData.email])
        msg.body="testing"
        mail.send(msg)
        return redirect('login')
      else:
        flash('your email is not registered or incorrect contact admin!!')
        return redirect('login')
    return render_template('forgotpwd.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    form.firstname.choices=[(u[0],u[0]) for u in user.query.with_entities(user.firstName).all()]


    if form.validate_on_submit():
#         userRegister = user(username=form.username.data, email=form.email.data,firstName=form.firstname.data,
#                            lastName=form.lastname.data,phone=form.phone.data)
        userRegister = user.query.filter_by(firstName=form.firstname.data).first()
        userRegister.username=form.username.data
        userRegister.email=form.email.data
        #userRegister.lastName=form.lastname.data
        userRegister.phone=form.phone.data

        userRegister.set_password(form.password.data)
        #db.session.add(userRegister)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/schedule',methods=['GET', 'POST'])
def schedule():

#     if not current_user.is_authenticated:
#         flash('Please login to view data')
#         return redirect(url_for('login'))
    print(current_user)
    form=FilterForm()
    form.playerFilter_feild.choices=[('','')]+[(u[0],u[0]) for u in user.query.with_entities(user.firstName).all()]

    form.deadlineFilter_feild.choices=[('','')]+[(str(u[0]),str(u[0])) for u in score.query.with_entities(score.deadline).distinct()]


    if form.validate_on_submit():
      player=form.playerFilter_feild.data
      _deadline=form.deadlineFilter_feild.data
      #print(player,_deadline)

      if(player):
        queryData=score.query.filter((or_(score.player_id1==player,score.player_id2==player))).order_by(score.deadline).all()
        return render_template("schedule.html",title=SEASON_NAME,data=queryData,form=form)
      if(_deadline):
        queryData=score.query.filter(score.deadline==_deadline).all()
        return render_template("schedule.html",title=SEASON_NAME,data=queryData,form=form)
    #print(form.errors)
    return render_template("schedule.html",title=SEASON_NAME,data=score.query.order_by(score.deadline).all(),form=form)

@app.route('/players')
#@login_required
def players():
    return render_template("players.html",title="Players",data=user.query.all())

@app.route('/PointTable',methods=['GET', 'POST'])
def PointTable():

#     if not current_user.is_authenticated:
#       flash('Please login to view data')
#       return redirect(url_for('login'))

#     form=PointTableForm()
#     form.divisionFilter_feild.choices=[('','')]+[(u[0],u[0]) for u in score.query.with_entities(score.division).distinct()]
#     form.levelFilter_feild.choices=[('','')]+[(str(u[0]),str(u[0])) for u in score.query.with_entities(score.level).distinct()]

#     if form.validate_on_submit():
#       _division=form.divisionFilter_feild.data
#       _level=form.levelFilter_feild.data

#       getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==_level,score.division==_division)).distinct()
#       getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==_level,score.division==_division)).distinct()
#       players=[]
#       #print(players)
#       #add data from both player list
#       for e in getPlayer1:
#         if(e[0]!='Bye'):
#           players.append(e[0])
#       for e in getPlayer2:
#         if(e[0]!='Bye'):
#           players.append(e[0])
#       #get unique values
#       players=list(set(players))

#       query=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()
#       return render_template("pointTable.html",title=SEASON_NAME,data=query,form=form)


    #print(form.errors)
    #return render_template("pointTable.html",title=SEASON_NAME,data=pointTable.query.order_by(desc(pointTable.points)).all(),form=form)

      #Level 4.5 Div A
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==4.5,score.division=='A')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==4.5,score.division=='A')).distinct()
      players=[]
#       print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_45A=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()


      #Level 4.5 Div B
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==4.5,score.division=='B')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==4.5,score.division=='B')).distinct()
      players=[]
      #print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_45B=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()


      #Level 4.0 Div A
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==4.0,score.division=='A')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==4.0,score.division=='A')).distinct()
      players=[]
      #print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_40A=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()


      #Level 4.0 Div B
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==4.0,score.division=='B')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==4.0,score.division=='B')).distinct()
      players=[]
      #print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_40B=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()

      #Level 3.5 Div A
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==3.5,score.division=='A')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==3.5,score.division=='A')).distinct()
      players=[]
      #print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_35A=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()


      #Level 3.5 Div B
      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==3.5,score.division=='B')).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==3.5,score.division=='B')).distinct()
      players=[]
      #print(players)
      #add data from both player list
      for e in getPlayer1:
        if(e[0]!='Bye'):
          players.append(e[0])
      for e in getPlayer2:
        if(e[0]!='Bye'):
          players.append(e[0])
      #get unique values
      players=list(set(players))

      query_35B=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()

      return render_template("pointTable.html",title=SEASON_NAME,data_45A=query_45A,data_45B=query_45B,data_40A=query_40A,data_40B=query_40B,data_35A=query_35A,data_35B=query_35B)

@app.route('/enterScore',methods=['GET', 'POST'])
def enterScore():

    if not current_user.is_authenticated:
      flash('Please login to enter data')
      return redirect(url_for('login'))

  #check to enter score againt player record and not other users
    if ((current_user.firstName!=request.args.get('player1') and current_user.firstName!=request.args.get('player2')) and current_user.username!="admin"):
      flash("Please enter score againt your record.")
      return redirect(url_for('schedule'))

    _matchDate=request.args.get('isExpired')
    _matchDate=datetime.strptime(_matchDate,'%Y-%m-%d').date()
    #print(datetime.now().date())
    #print(_matchDate,datetime.now().date(),central,central.date())
    #check if dealine exeecded
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Central')
    utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    print(central.date()+timedelta(days=7))
    tennis_forefeit=True


    if(central.date()>_matchDate+timedelta(days=7) and current_user.username!="admin"):
      flash("Cannot enter score, deadline and extension week exceeded contact admin!!")
      return redirect(url_for('schedule'))
    elif(central.date()>_matchDate and central.date()<_matchDate+timedelta(days=7) and current_user.username!="admin"):
      tennis_forefeit=False
      flash("Extension Week!!!")

    form=ScoreForm()
    if form.validate_on_submit():
      p1s1=form.player1_set1.data
      p1s2=form.player1_set2.data
      p1s3=form.player1_set3.data
      p2s1=form.player2_set1.data
      p2s2=form.player2_set2.data
      p2s3=form.player2_set3.data
      p1forefeit=form.player1_forefeit.data
      p2forefeit=form.player2_forefeit.data
#     Validate entered score

#       if(p1s1==p2s1 or p1s2==p2s2):
#         flash('Invalid Score!! please check')
#         return render_template("scoreForm.html",form=form,p1=request.args.get('player1'),
#                           p2=request.args.get('player2'))
#       elif((p1s1<6 and p2s1<6) or (p1s2<6 and p2s2<6)):
#         flash('Invalid Score!! please check')
#         return render_template("scoreForm.html",form=form,p1=request.args.get('player1'),
#                           p2=request.args.get('player2'))
#       else:
      update_Score=score.query.filter_by(id=request.args.get('id')).first()
      player1=request.args.get('player1')
      player2=request.args.get('player2')

      if(not tennis_forefeit and (p1forefeit or p2forefeit)):
        flash('Forefeit NOT Allowed')
        return redirect(url_for('schedule'))

      #print(update_Score.deadline,datetime.now().date())
      print(p1forefeit,p2forefeit)
      if(not p1forefeit and not p2forefeit):
        update_Score.score=p1s1+'-'+p2s1+','+p1s2+'-'+p2s2+','+p1s3+'-'+p2s3
      elif(p1forefeit):
        update_Score.score='Forefeit - '+player1
      elif(p2forefeit):
        update_Score.score='Forefeit - '+player2

#        update point table
      #print(p1s1,p1s2,p1s3,p2s1,p2s2,p2s3)
      _score=updateScore(p1s1,p1s2,p1s3,p2s1,p2s2,p2s3,p1forefeit,p2forefeit,player1,player2)
      winner=_score.updatePlayerScore()
      if(winner):
        if(winner=='TIE'):
          flash('Its a TIE')
        else:
          flash(winner + ' is the winner')
        db.session.commit()
      else:
        flash('Invalid Score!! Please check')
        return render_template("scoreForm.html",form=form,p1=request.args.get('player1'),
                          p2=request.args.get('player2'))

      return redirect(url_for('schedule'))



    return render_template("scoreForm.html",form=form,p1=request.args.get('player1'),
                          p2=request.args.get('player2'))

# ****** ADMIN STUFF *************

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    playerForm=addPlayerForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(EXCEL_PATH + filename)
        SEASON_NAME=form.seasonName.data
#      code for excel to score db --- upload schedule
        excelData=exceltoDB(EXCEL_PATH + filename)

        if(excelData.readExcel()=='error'):
          flash("Incorrect Excel")
          return render_template('upload.html', form=form,form1=playerForm)
        data=excelData.getScheduleData()

      #delete score table if uploading again for same season
        db.session.query(score).delete()
        db.session.commit()
        for elem in data:
          if(elem):
            if(elem[5]!=None):
              scoreDB=score(player_id1=elem[2],player_id2=elem[3],score=str(elem[5]),deadline=elem[4],level=elem[0],division=elem[1])
            else:
              scoreDB=score(player_id1=elem[2],player_id2=elem[3],score='',deadline=elem[4],level=elem[0],division=elem[1])
            db.session.add(scoreDB)
        db.session.commit()

      #code to upload player_id from excel to user table and point table
        data=excelData.getPlayerData()

      #clear user db for initial upload from excel and point table
        current_players=user.query.with_entities(user.firstName).all()
        player_list=[]
        for player in current_players:
          player_list.append(player[0])
        print(player_list)
        #db.session.query(user).delete()
        db.session.query(pointTable).delete()
        db.session.commit()
        for elem in data:
          if(elem):
            if(elem not in player_list): #new season user dont have to register again
              userDB=user(firstName=elem)
              db.session.add(userDB)
            ptRecords=pointTable(player_id=elem)
            db.session.add(ptRecords)
        db.session.commit()
        return redirect(url_for('schedule'))

    #add player form for admin
    if playerForm.validate_on_submit():
        userRegister = user(firstName=playerForm.playername.data)
        db.session.add(userRegister)
        db.session.commit()

        return redirect(url_for('players'))
    return render_template('upload.html', form=form,form1=playerForm)

@app.route('/deleteDB')
def deleteDB():
  excel_data=exceltoDB(DOWNLOAD_PATH)#/Users/harsha/Desktop/workspace/Desktop_KTL/downloads/tennis.xlsx')
  excel_data.writeExcel()
  return redirect(url_for('schedule'))

@app.route('/playerSchedule',methods=['GET', 'POST'])
def playerSchedule():
  var =request.args.get('playername')
#   print(var)
  userHome = user.query.filter_by(firstName=var).first()
  return render_template("home.html",data=userHome,tabledata=score.query.filter((or_(score.player_id1==var,
                                                                                          score.player_id2==var))).order_by(score.deadline).all(),PTdata=pointTable.query.filter_by(player_id=var).first())

@app.route('/about')
def about():
  return render_template("about.html")

@app.route('/playoffs')
def playoffs():
  return render_template("playoffnew.html")

@app.route('/FVLindex')
def FVLindex():
  return render_template("FVLHome.html")

@app.route('/FVLschedule',methods=['GET', 'POST'])
def FVLschedule():

  form=FVLTeamFilter()
  form.teamFilter_feild.choices=[('','')]+ [(u,u) for u in FVL_PlayedId]

  df=pd.read_excel(FVL_fileName,sheet_name='Schedule')
  data=[]

  if form.validate_on_submit():
      team=form.teamFilter_feild.data
      for index,row in df.iterrows():
        if(row['Home']==team or row['Away']==team):
          data.append([row['Home'],row['Away'],row['Deadline'].date(),row['Score'],row['Index']])
      return render_template("FVLschedule.html",data=data,form=form)

  for index,row in df.iterrows():
    print(row['Home'],row['Away'],row['Deadline'],row['Score'])
    data.append([row['Home'],row['Away'],row['Deadline'].date(),row['Score'],row['Index']])
  #data=[['a','b','11-9-10','10-15']]
  return render_template("FVLschedule.html",data=data,form=form)


@app.route('/FVLpointTable')
def FVLpointTable():



  df=pd.read_excel(FVL_fileName,sheet_name='PointTable')
  df.sort_values(by=['Points'], inplace =True,ascending=False)
  dataA=[]
  dataB=[]
  for index,row in df.iterrows():
    #print(row['Home'],row['Away'],row['Deadline'],row['Score'])
    if(row['Team'] in FVL_PoolA):
      dataA.append([row['Team'],row['Played'],row['Won'],row['Lost'],row['Bonus'],row['Points'],row['For'],row['Against'],row['NRR']])
    elif(row['Team'] in FVL_PoolB):
      dataB.append([row['Team'],row['Played'],row['Won'],row['Lost'],row['Bonus'],row['Points'],row['For'],row['Against'],row['NRR']])
  #data=[['a','b','11-9-10','10-15']]
  return render_template("FVLpointTable.html",dataA=dataA,dataB=dataB)

@app.route('/FVLabout')
def FVLabout():
  return render_template("FVLabout.html")

@app.route('/FVLteams')
def FVLteams():
  df=pd.read_excel(FVL_playerlist,sheet_name='Players List')
  data=[]

  for index,row in df.iterrows():
    data.append([row['Team Name'],row['Captain'],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row['Contact']])

#   print(data)
  return render_template("FVLTeams.html",data=data)

@app.route('/FVLscore',methods=['GET', 'POST'])
def FVLscore():


  if not current_user.is_authenticated:
    flash('Please login to enter data')
    return redirect(url_for('login'))

  #check to enter score againt player record and not other users
  if ((current_user.firstName!=request.args.get('home') and current_user.firstName!=request.args.get('away')) and current_user.username!="admin"):
    flash("Please enter score againt your record.")
    return redirect(url_for('FVLschedule'))

  home=request.args.get('home')
  away=request.args.get('away')
  ScheduleIndex=request.args.get('index')
  form=FVLScoreForm(csrf_enabled=False)
  score=''
  #TeamDict={"Cross Creek Smashers":0,"Gully Boyz":1,"Katy Boyz":2,"Katy Defenders":3,"Katy Dragons":4,"Katy Legends":5,"Katy Sparks":6,"Katy Whackers":7,"Katy Whackers2":8,"Wood Warriors":9,"Katy Falcons":10,"Katy Boyz2":11,"Underdogs":12,"Katy Bulls":13}
  bonus=0
  forefeitAllowed = True
  ######### Tme Calc ###########
  _matchDate=request.args.get('deadline')
  _matchDate=datetime.strptime(_matchDate,'%Y-%m-%d').date()

  from_zone = tz.gettz('UTC')
  to_zone = tz.gettz('US/Central')
  utc = datetime.utcnow()
  utc = utc.replace(tzinfo=from_zone)
  central = utc.astimezone(to_zone)

  if(central.date()>_matchDate+timedelta(days=7) and current_user.username!="admin"):
    flash("Cannot enter score, deadline and extension week exceeded contact admin!!")
    return redirect(url_for('FVLschedule'))
  elif(central.date()>_matchDate and central.date()<_matchDate+timedelta(days=7) and current_user.username!="admin"):
    forefeitAllowed=False
    flash("Extension Week!!! No Forefeit allowed")

  #############################

  if form.validate_on_submit():

    homeset1=form.home_set1.data
    homeset2=form.home_set2.data
    homeset3=form.home_set3.data
    awayset1=form.away_set1.data
    awayset2=form.away_set2.data
    awayset3=form.away_set3.data
    homeforefeit=form.home_forefeit.data
    awayforefeit=form.away_forefeit.data
    #print(homeset1,awayset1)
    if(homeforefeit or awayforefeit):
      if(homeset1 or homeset2 or awayset1 or awayset2):
        flash('invalid score')
        return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
      elif(not forefeitAllowed):
        flash('forefeit not allowed')
        return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
    if(not homeforefeit and not awayforefeit):
      if(homeset1 != 21 and awayset1 != 21):
        flash('invalid score')
        return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
      if(homeset2 != 21 and awayset2 != 21):
        flash('invalid score')
        return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
      if(homeset1 != 21 or homeset2 != 21):
        if((homeset3 != 0 or awayset3 != 0) and (homeset3 != 21 and awayset3 != 21)):
          flash('invalid score')
          return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
    elif(homeforefeit and awayforefeit):
      flash('invalid score')
      return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)

    winner=''
      #winner calc
    if(homeset1==21 and homeset2==21):
        winner=home
        bonus=1
#         score=homeset1+'-'+awayset1+' , ' + homeset2+'-'+awayset2
    elif(awayset1==21 and awayset2==21):
        winner=away
        bonus=1
#         score=homeset1+'-'+awayset1+' , ' + homeset2+'-'+awayset2
    else:
      if(homeset3==21):
          winner=home
          bonus=2
#           score=homeset1+'-'+awayset1+' , ' + homeset2+'-'+awayset2 + ' , ' + homeset3+'-'+awayset3
      elif(awayset3==21):
          winner=away
          bonus=2
#           score=homeset1+'-'+awayset1+' , ' + homeset2+'-'+awayset2 + ' , ' + homeset3+'-'+awayset3
      elif(homeforefeit):
          winner="homeforefeit"
          bonus=0
      elif(awayforefeit):
          winner="awayforefeit"
          bonus=0

    #invoke reader
    df_Schedule=pd.read_excel(FVL_fileName,sheet_name='Schedule')
    df_PointTable=pd.read_excel(FVL_fileName,sheet_name='PointTable')

    #set score in schedule sheet
    if(homeforefeit):
      df_Schedule.at[int(ScheduleIndex),'Score']='Forefeit- '+ home
    elif(awayforefeit):
      df_Schedule.at[int(ScheduleIndex),'Score']='Forefeit- '+ away
    else:
      df_Schedule.at[int(ScheduleIndex),'Score']=str(homeset1)+'-'+str(awayset1)+' , ' + str(homeset2)+'-'+str(awayset2) + ' , ' + str(homeset3)+'-'+str(awayset3)


    #update point table
    homeIndex=TeamDict[home]
    awayIndex=TeamDict[away]

    #mark played for both
#     temp1=df_PointTable.at[homeIndex,'Played']
#     temp2=df_PointTable.at[awayIndex,'Played']
    df_PointTable.at[homeIndex,'Played']=df_PointTable.at[homeIndex,'Played']+1
    df_PointTable.at[awayIndex,'Played']=df_PointTable.at[awayIndex,'Played']+1



    #mark won,points,lost,bonus,points
    if(winner==home):
      df_PointTable.at[homeIndex,'Won']=df_PointTable.at[homeIndex,'Won']+1
      df_PointTable.at[homeIndex,'Points']=df_PointTable.at[homeIndex,'Points']+4
      df_PointTable.at[awayIndex,'Lost']=df_PointTable.at[awayIndex,'Lost']+1
      df_PointTable.at[awayIndex,'Bonus']=df_PointTable.at[awayIndex,'Bonus']+bonus
      df_PointTable.at[awayIndex,'Points']=df_PointTable.at[awayIndex,'Points']+bonus
    elif(winner==away):
      df_PointTable.at[awayIndex,'Won']=df_PointTable.at[awayIndex,'Won']+1
      df_PointTable.at[awayIndex,'Points']=df_PointTable.at[awayIndex,'Points']+4
      df_PointTable.at[homeIndex,'Lost']=df_PointTable.at[homeIndex,'Lost']+1
      df_PointTable.at[homeIndex,'Bonus']=df_PointTable.at[homeIndex,'Bonus']+bonus
      df_PointTable.at[homeIndex,'Points']=df_PointTable.at[homeIndex,'Points']+bonus
    elif(winner=="homeforefeit"):
      df_PointTable.at[awayIndex,'Won']=df_PointTable.at[awayIndex,'Won']+1
      df_PointTable.at[awayIndex,'Points']=df_PointTable.at[awayIndex,'Points']+4
      df_PointTable.at[homeIndex,'Lost']=df_PointTable.at[homeIndex,'Lost']+1
      winner=away
    elif(winner=="awayforefeit"):
      df_PointTable.at[homeIndex,'Won']=df_PointTable.at[homeIndex,'Won']+1
      df_PointTable.at[homeIndex,'Points']=df_PointTable.at[homeIndex,'Points']+4
      df_PointTable.at[awayIndex,'Lost']=df_PointTable.at[awayIndex,'Lost']+1
      winner=home

#     #NRR calc
#     Total=homeset1+homeset2+homeset3+awayset1+awayset2+awayset3
#     ForHome=AgainstAway=(homeset1+homeset2+homeset3)/Total
#     ForAway=AgainstHome=(awayset1+awayset2+awayset3)/Total
#     print(ForHome,ForAway)
#     df_PointTable.at[homeIndex,'For']=df_PointTable.at[homeIndex,'For']+ForHome
#     df_PointTable.at[homeIndex,'Against']=df_PointTable.at[homeIndex,'Against']+AgainstHome
#     df_PointTable.at[awayIndex,'For']=df_PointTable.at[awayIndex,'For']+ForAway
#     df_PointTable.at[awayIndex,'For']=df_PointTable.at[awayIndex,'For']+AgainstAway

#     df_PointTable.at[homeIndex,'NRR']=df_PointTable.at[homeIndex,'For']-df_PointTable.at[homeIndex,'Against']
#     df_PointTable.at[awayIndex,'NRR']=df_PointTable.at[awayIndex,'For']-df_PointTable.at[awayIndex,'Against']

    #invoke writer
    with pd.ExcelWriter(FVL_fileName) as writer:
      df_Schedule.to_excel(writer,sheet_name='Schedule')
      df_PointTable.to_excel(writer,sheet_name='PointTable')

    flash(winner + ' is the winner')
    return redirect(url_for('FVLpointTable'))


  return render_template("FVLscoreForm.html",homeTeam=home,awayTeam=away,form=form)
