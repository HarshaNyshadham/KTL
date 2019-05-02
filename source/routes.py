from source import app,db,admin
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from source.models import user,score,pointTable,adminView
from source.forms import LoginForm,RegistrationForm,ScoreForm,UploadForm,FilterForm,addPlayerForm,PointTableForm
from source.calculation import exceltoDB,updateScore
from datetime import datetime,date
from sqlalchemy import and_,or_,desc
import string

#EXCEL_PATH='uploads/'
EXCEL_PATH='/home/Harshanand/mysite/uploads/'

@app.route('/')
@app.route('/index')
def index():
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
        if userLogged is None or not userLogged.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(userLogged, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

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
        userRegister.lastName=form.lastname.data
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

    if not current_user.is_authenticated:
        flash('Please login to view data')
        return redirect(url_for('login'))

    form=FilterForm()
    form.playerFilter_feild.choices=[('','')]+[(u[0],u[0]) for u in user.query.with_entities(user.firstName).all()]

    form.deadlineFilter_feild.choices=[('','')]+[(str(u[0]),str(u[0])) for u in score.query.with_entities(score.deadline).distinct()]


    if form.validate_on_submit():
      player=form.playerFilter_feild.data
      _deadline=form.deadlineFilter_feild.data
      #print(player,_deadline)

      if(player):
        queryData=score.query.filter((or_(score.player_id1==player,score.player_id2==player))).order_by(score.deadline).all()
        return render_template("schedule.html",title="Spring Schedule",data=queryData,form=form)
      if(_deadline):
        queryData=score.query.filter(score.deadline==_deadline).all()
        return render_template("schedule.html",title="Spring Schedule",data=queryData,form=form)
    #print(form.errors)
    return render_template("schedule.html",title="Spring Schedule",data=score.query.all(),form=form)

@app.route('/players')
#@login_required
def players():
    return render_template("players.html",title="Players",data=user.query.all())

@app.route('/PointTable',methods=['GET', 'POST'])
def PointTable():

    if not current_user.is_authenticated:
      flash('Please login to view data')
      return redirect(url_for('login'))

    form=PointTableForm()
    form.divisionFilter_feild.choices=[('','')]+[(u[0],u[0]) for u in score.query.with_entities(score.division).distinct()]
    form.levelFilter_feild.choices=[('','')]+[(str(u[0]),str(u[0])) for u in score.query.with_entities(score.level).distinct()]

    if form.validate_on_submit():
      _division=form.divisionFilter_feild.data
      _level=form.levelFilter_feild.data

      getPlayer1=score.query.with_entities(score.player_id1).filter(and_(score.level==_level,score.division==_division)).distinct()
      getPlayer2=score.query.with_entities(score.player_id2).filter(and_(score.level==_level,score.division==_division)).distinct()
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

      query=pointTable.query.filter(pointTable.player_id.in_(players)).order_by(desc(pointTable.points)).all()
      return render_template("pointTable.html",title="Points Table",data=query,form=form)


    #print(form.errors)
    return render_template("pointTable.html",title="Points Table",data=pointTable.query.order_by(desc(pointTable.points)).all(),form=form)

@app.route('/enterScore',methods=['GET', 'POST'])
def enterScore():
    if ((current_user.firstName!=request.args.get('player1') and current_user.firstName!=request.args.get('player2')) and current_user.username!="admin"):
      flash("Please enter score againt your record.")
      return redirect(url_for('schedule'))
    form=ScoreForm()
    if form.validate_on_submit():
      p1s1=form.player1_set1.data
      p1s2=form.player1_set2.data
      p1s3=form.player1_set3.data
      p2s1=form.player2_set1.data
      p2s2=form.player2_set2.data
      p2s3=form.player2_set3.data

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
      update_Score.score=p1s1+'-'+p2s1+','+p1s2+'-'+p2s2+','+p1s3+'-'+p2s3

#        update point table
      print(p1s1,p1s2,p1s3,p2s1,p2s2,p2s3)
      _score=updateScore(p1s1,p1s2,p1s3,p2s1,p2s2,p2s3,player1=request.args.get('player1'),player2=request.args.get('player2'))
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
#      code for excel to score db --- upload schedule
        excelData=exceltoDB(EXCEL_PATH + filename)
        excelData.readExcel()
        data=excelData.getScheduleData()
      #delete score table if uploading again for same season
        db.session.query(score).delete()
        db.session.commit()
        for elem in data:
          if(elem):
            scoreDB=score(player_id1=elem[2],player_id2=elem[3],score='',deadline=elem[4],level=elem[0],division=elem[1])
            db.session.add(scoreDB)
        db.session.commit()

      #code to upload player_id from excel to user table and point table
        data=excelData.getPlayerData()
      #clear user db for initial upload from excel and point table
        db.session.query(user).delete()
        db.session.query(pointTable).delete()
        db.session.commit()
        for elem in data:
          if(elem):
            userDB=user(firstName=elem[0])
            ptRecords=pointTable(player_id=elem[0],tie=0)
            db.session.add(userDB)
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
  db.session.query(score).delete()
  db.session.commit()

  return redirect(url_for('schedule'))
