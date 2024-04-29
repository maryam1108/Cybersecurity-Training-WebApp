from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions,Lessons,Topics
from app import db


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

@app.route('/')
def home():
    session['marks']=0

    return render_template('index.html', title='Home')

@app.route('/intro')
def intro():
    return render_template('intro.html', title='Intro')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['marks'] = 0
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    session['successStatus'] = False
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['marks'] = 0
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    session['successStatus'] = False

    return render_template('register.html', title='Register', form=form)

@app.route('/videoContent')
def videoContent():
     return render_template('video-content.html')

@app.route('/question_first/<int:id>/<int:topic_id>')
def question_first(id,topic_id):
    session['marks'] = 0
    
    total = Questions.query.filter_by(topic_id=topic_id).count()
    progress = (id / total) * 100
    return redirect(url_for('question',topic_id=topic_id, index=0, current=id, total=total, progress=progress))

@app.route('/question/<int:topic_id>/<int:index>', methods=['GET', 'POST'])
def question(topic_id,index):
    form = QuestionForm()
    ques = Questions.query.filter_by(topic_id=topic_id).all()
   
    total = Questions.query.filter_by(topic_id=topic_id).count()
    if index>=total:

        return redirect(url_for('score', topic_id=topic_id,total=total))
    q=ques[index] # because index
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        option = request.form['options']
        if option == q.ans:
            session['marks'] += 10
        return redirect(url_for('question',topic_id=topic_id, index=(index+1)))
    form.options.choices = [(q.a, q.a), (q.b, q.b), (q.c, q.c), (q.d, q.d)]
    
    
    progress = ((index+1) / total) * 100
    return render_template('question.html', form=form, q=q, title='Question {}'.format(id), current=index+1, total=total, progress=progress)

@app.route('/lesson/<int:id>/<int:index>', methods=['GET','POST'])
def lesson(id,index):
    form = QuestionForm()
    l = Lessons.query.filter_by(topic_id=id).all()
    total_lessons = Lessons.query.filter_by(topic_id=id).count()
    if not g.user:
        return redirect(url_for('login'))
    if not l or index>=total_lessons:
        return redirect(url_for('question',topic_id=id, index=0))
    if request.method == 'POST':
        return redirect(url_for('lesson', id=(id),index=index+1))
       # Get the total number of lessons
    
    
    # Calculate the progress
    progress = ((index+1) / total_lessons) * 100
    return render_template('lesson.html', form=form, l=l[index], title='Lessons {}'.format(index), progress=progress, current=(index+1), total=total_lessons)

@app.route('/score/<int:topic_id>/<int:total>')
def score(topic_id,total):
    status = True
    if not g.user:
        return redirect(url_for('login'))
    g.user.marks = session['marks']
    if session['marks']==0:
        g.user.failed_tries = g.user.failed_tries+1
        status = False
        session['successStatus'] = False
    elif ((session['marks']/(total*10))*100)<50:
        g.user.failed_tries = g.user.failed_tries+1
        status = False
        session['successStatus'] = False
    else:
        g.user.failed_tries = 0
        session['successStatus'] = True
    db.session.commit()
    if g.user.failed_tries>=2:

        return redirect(url_for('tryAgain'))

    return render_template('score.html', title='Final Score{}'.format(g.user.failed_tries), status=status,topic_id=topic_id)
@app.route('/tryAgain')
def tryAgain():
    return render_template('tryagain.html')

@app.route('/logout')
def logout():
    session['successStatus'] = False
    if not g.user:
        return redirect(url_for('login'))
    
    session.pop('user_id', None)
    session.pop('marks', None)
    return redirect(url_for('home'))

@app.route('/topics')
def topics():
    if not g.user:
        return redirect(url_for('login'))

    # Get all topics from the database
    topics = Topics.query.all()

    return render_template('topic.html', title='Topics', topics=topics)
