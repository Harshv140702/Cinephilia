from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
import base64
import math
from datetime import date
from flask_login import login_required, current_user, LoginManager

today = date.today()

flag = 0
show_count = 0

# # Configure application
app = Flask(__name__)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('user') is None:
            flash(u"You need to login first")
            return redirect("/login")
        else:
            return f(*args, **kwargs)
    return wrap

def convertToBinaryData(filename):
        #Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configuring session to use filesystem (no cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///project.db")

@app.route("/")
def route():
    return redirect("/logo")

@app.route("/logo")
def logo():
    return render_template("logo.html")

@app.route("/admin")
#  
def admin():
    if session['user'] is not None:
        row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

        return render_template("dashboard.html", admin = row[0]["username"], email = row[0]["email"], db="active")

@app.route("/login", methods=["GET", "POST"])
def index():
    """User log in"""
    session.clear()

    if request.method == "GET":
        return render_template("signin.html")

    else:
        row = db.execute(
            "SELECT * FROM users WHERE username=:username",
            username=request.form.get("username"),
        )

        if len(row) != 1 or not check_password_hash(
            row[0]["password"], request.form.get("password")
        ):
            flag = 1
            return render_template("signin.html", alert=1)

        else:
            session["user-id"] = row[0]["id"]
            if row[0]["category"] == 1:
                session["user"] = "admin"
                return redirect("/admin")
            else:
                session["user"]="user"
                return redirect("/home")


@app.route("/register", methods=["GET", "POST"])
def reg():
    """User Register"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        contact = request.form.get("contact")

        prim_key = db.execute(
            "INSERT INTO users (username, password, email, contact, category) VALUES(:username, :password, :email, :contact, :category)",
            username=name,
            password=generate_password_hash(password),
            email=email,
            contact=contact,
            category=0,
        )
        # Check it out
        session["user-id"] = prim_key

        return redirect("/home")


@app.route("/db")
@login_required
def dashb():
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    flash(u"admin")
    return render_template("dashboard.html", admin = row[0]["username"], email = row[0]["email"], db="active")

@app.route("/addmovie", methods=['GET', 'POST'])
def add_movie ():

    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    if request.method == "GET":
        #flash(u"admin reg")
        return render_template("newmovie.html",  admin = row[0]["username"], email = row[0]["email"], anm = "active")
    else:
        name = request.form.get("name")
        lang = request.form.get("lang")
        length = request.form.get("len")
        genre = request.form.get("genre")
        poster = "static/movies/"+request.form.get("poster")
        start = request.form.get("start")
        end = request.form.get("end")
        url = request.form.get("trailer")
        movie_show = request.form.get("pref")
        ticket= request.form.get("tic")
        direc = request.form.get("dir")
        rating = request.form.get("rat")
        about = request.form['about']
        cast = request.form['cast']

        prim_key = db.execute("INSERT INTO movies (name, Language,  poster, length, genre, show_start, show_end, issue, movie_show, Trailer, Cast, Director, Rating, About) VALUES(:name, :language,  :poster, :length, :genre, :start, :end, :issue, :movie_show, :Trailer, :Cast, :Director, :Rating, :About )",
                           name = name,
                           language = lang,
                           poster = convertToBinaryData(poster),
                           length = length,
                           genre = genre,
                           start=start,
                           end=end,
                           issue = ticket,
                           movie_show = movie_show,
                           Trailer = url,
                           Cast = cast,
                           Director = direc,
                           Rating = rating,
                           About = about)

        if prim_key is not None:
            flash(u"Record is added to database")

        else:
            flash(u"Record is not added to database")

        return render_template("newmovie.html", admin = row[0]["username"], email = row[0]["email"], anm= "active")



@app.route("/delmovie", methods=['GET', 'POST'])
 
def del_movie ():

    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    if request.method == "GET":
        #flash(u"admin reg")
        return render_template("delmovie.html",  admin = row[0]["username"], email = row[0]["email"], dm = "active")

    else:
        name = request.form.get("name")
        lang = request.form.get("lang")


        db.execute("DELETE FROM movies WHERE name LIKE '"+name+"%' AND Language = :language COLLATE nocase",language = lang)

        flash(u"Record Deleted")
        return render_template("delmovie.html", admin = row[0]["username"], email = row[0]["email"], dm= "active")



@app.route("/upd", methods=['GET', 'POST'])
def upd():
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    if request.method == "GET":
        return render_template("upd.html",  admin = row[0]["username"], email = row[0]["email"], umd = "active")

    else:
        name = request.form.get("name")
        lang = request.form.get("lang")
        
        length = request.form.get("len")
        genre = request.form.get("genre")
        start = request.form.get("start")
        end = request.form.get("end")
        url = request.form.get("trailer")
        movie_show = request.form.get("pref")
        ticket= request.form.get("tic")
        direc = request.form.get("dir")
        rating = request.form.get("rat")
        about = request.form['about']
        cast = request.form['cast']



        db.execute("UPDATE movies SET length=:length,genre =:genre,show_start=:start,show_end=:end,issue=:issue,movie_show=:movie_show,Trailer=:Trailer,Cast=:Cast,Director=:Director,Rating=:Rating,About=:About WHERE name=:name AND Language=:lang",
                               name = name,
                               lang = lang,
                               length = length,
                               genre = genre,
                               start=start,
                               end=end,
                               issue = ticket,
                               movie_show = movie_show,
                               Trailer = url,
                               Cast = cast,
                               Director = direc,
                               Rating = rating,
                               About = about)

        flash(u"Record Updated")
        return render_template("upd.html", admin = row[0]["username"], email = row[0]["email"], umd= "active")

@app.route("/showma")
def showmoviesad():
    movie = request.args.get("name")
    #pref = request.args.get("pref")
    lang = request.args.get("lang")
    date = request.args.get("date")

    if date:
        row = db.execute("SELECT * FROM movies WHERE show_start <= :start AND show_start<>''",
                            start=today)

        names = []
        lang=[]

        text = "<movies>"
        for movie in row:
            names.append(movie["name"])
            lang.append(movie["Language"])
            text +="<movie><id>"+str(movie["id"])+"</id><name>"+movie["name"]+"</name><lang>"+movie["Language"]+"</lang><len>"+str(math.ceil(movie["length"]))+"</len></movie>"

        text+="</movies>"

        return text

    else:
        row = db.execute("Select * from movies WHERE name LIKE '"+movie+"%' AND Language=:lang COLLATE nocase",lang = lang)

        text = ""

        for movie in row:
            text +="<movie><name>"+movie["name"]+"</name><lang>"+movie["Language"]+"</lang><len>"+str(math.ceil(movie["length"]))+"</len><genre>"+movie["genre"]+"</genre><start>"+str(movie["show_start"])+"</start><end>"+str(movie["show_end"])+"</end><tic>"+str(movie["issue"])+"</tic><pref>"+str(movie["movie_show"])+"</pref><url>"+movie["Trailer"]+"</url><cast>"+movie["Cast"]+"</cast><dir>"+movie["Director"]+"</dir><rating>"+movie["Rating"]+"</rating><about>"+movie["About"]+"</about></movie>"

        return text

@app.route("/addscr", methods=["GET", "POST"])
 
def addscr():
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])
    if request.method == "GET":
        return render_template("addsc.html",admin = row[0]["username"], email = row[0]["email"], newSc= "active")
    else:
        screen_no = request.form.get("screen_no")
        seats= request.form.get("seats")

        db.execute("INSERT INTO Screen (Scid, No_of_seats) VALUES(:screen, :seats)",
                    screen = screen_no,
                    seats = seats)

        flash(u"Screen Added")
        return render_template("addsc.html", admin = row[0]["username"], email = row[0]["email"], newSc= "active")




@app.route("/updmovie", methods=['POST'])
 
def upd_movie ():
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    name = request.form.get("name")
    lang = request.form.get("lang")

    length = request.form.get("len")
    genre = request.form.get("genre")
    start = request.form.get("start")
    end = request.form.get("end")
    url = request.form.get("trailer")
    movie_show = request.form.get("pref")
    ticket= request.form.get("tic")
    direc = request.form.get("dir")
    rating = request.form.get("rat")
    about = request.form['about']
    cast = request.form['cast']


    db.execute("UPDATE employees SET length =:length, genre =:genre, show_start =:start, show_end =:end, issue=:issue, movie_show=:movie_show, Trailer=:Trailer, Cast=:Cast, Director=:Director, Rating=:Rating, About=:About WHERE name =:name AND Language = :lang",
                           name = name,
                           language = lang,
                           length = length,
                           genre = genre,
                           start=start,
                           end=end,
                           issue = ticket,
                           movie_show = movie_show,
                           Trailer = url,
                           Cast = cast,
                           Director = direc,
                           Rating = rating,
                           About = about)

    flash(u"Record Updated")


    return render_template("updmovie.html", admin = row[0]["username"], email = row[0]["email"], umd= "active")

@app.route("/addshow", methods=["GET", "POST"])
def add_show():
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    if request.method == "GET":
        #flash(u"admin reg")
        return render_template("addshow.html",  admin = row[0]["username"], email = row[0]["email"], updst = "active", today = today)


    else:
        show_date = request.form.get("sd")
        show_time = request.form.get("time")
        show = request.form.get("show")
        movie = request.form.get("movie")

        db.execute("INSERT INTO Shows (scid,mid,show_date,show_time) VALUES (:scid, :mid, :sd, :st)",
                          sd = show_date,
                          scid = show,
                          mid = movie,
                          st = show_time)

        flash(u"Show Added")
        return render_template("addshow.html",admin = row[0]["username"], email = row[0]["email"], updst = "active", today = today)



@app.route("/regadmin", methods=['GET', 'POST'])
def reg_admin(): 
    row = db.execute("SELECT username, email from users where id=:id",
                          id = session['user-id'])

    if request.method == "GET":
        #flash(u"admin reg")
        return render_template("regadmin.html",  admin = row[0]["username"], email = row[0]["email"], regadmin = "active")

    else:
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        contact = request.form.get("contact")

        prim_key = db.execute("INSERT INTO users (username, password, email, contact, category) VALUES(:username, :password, :email, :contact, :category)",
                                username = name,
                                password = generate_password_hash(password),
                                email = email,
                                contact = contact,
                                category = 1)

        if prim_key is not None:
            flash(u"Record is added to database")

        else:
            flash(u"Record is not added to database")

        return render_template("regadmin.html", admin = row[0]["username"], email = row[0]["email"], regadmin= "active")
    
@app.route("/home")
@login_required
def log():
    if request.method == "GET":

        row = db.execute("SELECT poster, name, Language FROM movies WHERE show_start <= :start AND show_start<>''",
                            start=today)

        posters =[]
        names = []
        lang=[]

        for movie in row:
            posters.append(base64.b64encode(movie["poster"]).decode("utf-8"))
            names.append(movie["name"])
            lang.append(movie["Language"])

        return render_template("movie.html", moviePosters=zip(posters,names, lang))    

@app.route("/detail")
@login_required
def det():
    row = db.execute("Select * from users where id = :uid", uid = session['user-id'])
    ex = db.execute("Select seat_no,Ticket_id,name,show_date,show_time from Booked_Tickets INNER JOIN Shows ON Booked_Tickets.show_id = Shows.show_id INNER JOIN movies ON Shows.mid = movies.id WHERE Booked_Tickets.user_id = :uid", uid = session['user-id'])
    return render_template("detail.html", name = row[0]["username"], email = row[0]["email"], contact = row[0]["contact"],list=ex)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/cs")
@login_required
def comingsoon():

    row = db.execute("SELECT poster,name,Language FROM movies WHERE show_start > :start OR show_start=''",
                        start=today)

    posters =[]
    names = []
    lang = []

    for movie in row:
        posters.append(base64.b64encode(movie["poster"]).decode("utf-8"))
        names.append(movie["name"])
        lang.append(movie["Language"])

    return render_template("cs.html", moviePosters = zip(posters,names,lang))


@app.route("/showm")
@login_required
def showmovies():
    movie = request.args.get("name")
    pref = request.args.get("pref")
    lang = request.args.get("lang")

    if pref :
        row = db.execute("Select name,Language,length,genre,Trailer,\"Cast\",Director,Rating,About from movies WHERE name LIKE '"+movie+"%' AND movie_show=:pref AND Language=:lang COLLATE nocase",
                      pref = pref,
                      lang = lang)
    #cast = db.execute("Select \"Cast\" from movies WHERE name LIKE '"+movie+"%'")
    else:
         row = db.execute("Select name,Language,length,genre,Trailer,\"Cast\",Director,Rating,About from movies WHERE name LIKE '"+movie+"%' AND Language=:lang COLLATE nocase",lang = lang)

    text = ""
    for movie in row:
        text +="<movie><name>"+movie["name"]+"</name><lang>"+movie["Language"]+"</lang><len>"+str(math.ceil(movie["length"]))+"</len><genre>"+movie["genre"]+"</genre><url>"+movie["Trailer"]+"</url><cast>"+movie["Cast"]+"</cast><dir>"+movie["Director"]+"</dir><rating>"+movie["Rating"]+"</rating><about>"+movie["About"]+"</about></movie>"

    return text


@app.route("/showasc")
@login_required
def screen():
    row = db.execute("Select Scid From Screen")
    text="<screens>"
    for screen in row:
        text += "<screen><scid>"+str(screen["Scid"])+"</scid></screen>"
    text+="</screens>"
    return text

@app.route("/booktickets", methods=["GET", "POST"])
def booktickets():
    if request.method=="GET":
        ex = db.execute("SELECT name from movies")
        listmovie = []
        for i in ex:
            listmovie.append(i["name"])
        return render_template("bookinit.html", list= listmovie)
    else:
        date = request.form.get("date")
        movie = request.form.get("movie")
        print(date)
        print(movie)
        return redirect("/book/"+date+"/"+movie)

@app.route("/book/<date>/<movie>", methods=["GET", "POST"])      
def book(date, movie):
    ex = db.execute("SELECT show_time FROM shows WHERE mid=(SELECT id FROM movies WHERE name=?) AND show_date=date(?)", movie, date)
    datebook = date
    moviebook = movie
    if request.method=="GET":
        listex = []
        for i in ex:
            listex.append(i["show_time"])
        return render_template("book.html", date=datebook, movie=moviebook, list=listex)
    else:
        time = request.form.get("time")
        return redirect("/book2/"+date+"/"+movie+"/"+time)
@app.route("/book2/<date>/<movie>/<time>", methods=["GET", "POST"])
def book2(date, movie, time):
    datebook = date
    timebook = time
    if request.method=="GET":
        return render_template("book2.html", date=date, movie=movie, time=time)
    else:
        # seats = request.form.get("seats")
        usid = session['user-id']
        show = db.execute("SELECT show_id FROM shows where show_date = ? AND show_time = ?", datebook, timebook)
        showid = show[0]["show_id"]
        # print(seats)
        data = request.json
        if(data is not None):
           print(data)
           print(type(data))
           data = str(data)
           print(type(data))
           db.execute("INSERT INTO booked_tickets (user_id, show_id, seat_no) VALUES (?,?,?)",usid,showid, data)
        
        return redirect("/home")


@app.route("/ns")
@login_required
def nowshow():

    row = db.execute("SELECT poster,name,Language FROM movies WHERE show_start <= :start AND show_start<>''",
                        start=today)

    posters =[]
    names = []
    lang = []

    for movie in row:
        posters.append(base64.b64encode(movie["poster"]).decode("utf-8"))
        names.append(movie["name"])
        lang.append(movie["Language"])

    return render_template("nowshow.html", moviePosters = zip(posters,names,lang))


@app.route("/csm")
@login_required
def soonmovies():
    movie = request.args.get("name")
    #pref = request.args.get("pref")
    lang = request.args.get("lang")

    #if pref :
     #   row = db.execute("Select name,Language,length,genre,Trailer,\"Cast\",Director,Rating,About from movies WHERE name LIKE '"+movie+"%' AND movie_show=:pref AND Language=:lang COLLATE nocase",
        #pref = pref,
        #lang = lang)
    #cast = db.execute("Select \"Cast\" from movies WHERE name LIKE '"+movie+"%'")
    #else:
    row = db.execute("Select name,Language,length,genre,Trailer,\"Cast\",Director,Rating,About,show_start,poster from movies WHERE name LIKE '"+movie+"%' AND Language=:lang COLLATE nocase",lang = lang)

    text = ""
    for movie in row:
        text +="<movie><name>"+movie["name"]+"</name><lang>"+movie["Language"]+"</lang>"
        if movie["length"]:
            text +="<len>"+str(math.ceil(movie["length"]))+"</len>"

        else:
             text +="<len>"+"TBA"+"</len>"

        if movie["genre"]:
            text += "<genre>"+movie["genre"]+"</genre>"

        else:
            text += "<genre>"+"TBA"+"</genre>"

        if movie["Trailer"]:
            text += "<url>"+movie["Trailer"]+"</url><cast>"+movie["Cast"]+"</cast><dir>"+movie["Director"]+"</dir>"

        else:
            text += "<url>"+"None"+"</url><poster>"+base64.b64encode(movie["poster"]).decode("utf-8")+"</poster><cast>"+movie["Cast"]+"</cast><dir>"+movie["Director"]+"</dir>"

        if movie["show_start"]:
            text += "<start>"+movie["show_start"]+"</start>"
        else:
            text += "<start>TBA</start>"

        if movie["Rating"] is None:
            text += "<rating>"+movie["Rating"]+"</rating><about>"+movie["About"]+"</about></movie>"
        else:
            text += "<rating>"+"TBD"+"</rating><about>"+movie["About"]+"</about></movie>"

    return text





if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
