from flask import Flask, render_template, request, redirect, flash, abort, url_for
from classes import Citizen, Building, cities
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from passlib.hash import pbkdf2_sha256 as hasher
import os


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

adictionary = {}

@lm.user_loader
def load_user(ttt):
    return adictionary.get(ttt)


app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
app.config['MYSQL_USER'] = 'b219e0031eeaa1'
app.config['MYSQL_PASSWORD'] = '92733fef'
app.config['MYSQL_DB'] = 'heroku_62f82a549b59a6c'
db = MySQL(app)


@app.route('/')
def home_page():
    own = []
    resides = None
    if current_user.is_authenticated:
        if not current_user.is_official:
            cur = db.connection.cursor()
            cur.execute("SELECT * FROM apartment INNER JOIN building ON apartment.BuildingId=building.BuildingId WHERE OwnerId=%s;", (current_user.citizen_id, ))
            owned = cur.fetchall()
            cur.execute("SELECT * FROM resident WHERE CitizenshipID=%s;", (current_user.citizen_id,))
            reside = cur.fetchone()
            if reside is not None:
                cur.execute("SELECT * FROM apartment INNER JOIN building ON apartment.BuildingId=building.BuildingId WHERE ApartmentId=%s;", (reside[1],))
                resides = cur.fetchone()
            if len(owned) != 0:
                for x in owned:
                    for city in cities:
                        if city["id"] == str(x[7]):
                            break
                    own.append([x[0], x[2], city["name"], x[10], x[8], x[9]])
            cur.close()
            return render_template("homepage.html", owned=own, resides=resides, name=current_user.name)
    return render_template("homepage.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Already logged in")
        return redirect("/")

    if request.method == 'POST':
        cid = request.form["citizenship_id"]
        pw = request.form["password"]
        official = 'is_official' in request.form
        cur = db.connection.cursor()
        if official:
            cur.execute("SELECT * FROM offical WHERE OfficalId=%s;", (cid, ))
        else:
            cur.execute("SELECT * FROM citizen WHERE CitizenshipId=%s;", (cid, ))
        user = cur.fetchone()
        cur.close()
        if user is not None:
            if hasher.verify(pw, user[2]):
                this_user = Citizen(user[0], user[1], user[2], official)
                adictionary[user[0]] = this_user
                login_user(this_user)
                flash("you logged in")
                return redirect("/")
            else:
                flash("Password isn't correct")
        else:
            flash("Id isn't correct")
    return render_template("login.html")


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        cid = request.form["citizenship_id"]
        fname = request.form["full_name"]
        pw = request.form["password"]
        rpw = request.form["rpassword"]
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM citizen WHERE CitizenshipId=%s;", (cid,))
        neuer_benutzer = cur.fetchone()
        if neuer_benutzer is not None:
            flash("You already have an account")
            cur.close()
            return redirect('/signup')
        if pw==rpw:
            pw = hasher.hash(pw)
            cur.execute("insert into citizen (Name_Surname, CitizenshipID, Passkey) values (%s, %s, %s);", (fname, cid, pw))
            db.connection.commit()
            cur.close()
            flash("Successfully Signed Up")
            return redirect("/")
        else:
            flash("Re-entered password doesn't match with the original password")
            cur.close()
            return redirect("/signup")
    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    adictionary.pop(current_user.get_id())
    logout_user()
    return redirect("/")


@app.route('/buildings')
def buildings():
    bs = []
    cit = set()
    cur = db.connection.cursor()
    cur.execute("SELECT COUNT(BuildingId),City FROM building WHERE Torn_Down=0 GROUP BY City ORDER BY Count(BuildingId) DESC;")
    data = cur.fetchall()
    cur.close()
    for stuff in data:
        for x in cities:
            if x["id"] == str(stuff[1]):
                break
        cit.add(x["name"])
        bs.append([stuff[0], x["name"]])
    return render_template("buildings.html", bs=bs, cit=sorted(cit))


@app.route('/buildings/<city>')
def buildings_c(city):
    bs = []
    dis = set()
    cur = db.connection.cursor()
    for x in cities:
        if x["name"] == city:
            break
    cur.execute("SELECT * FROM building WHERE Torn_Down=0 AND City=%s;", (x["id"],))
    data = cur.fetchall()
    cur.close()
    if len(data) == 0:
        abort(404)
    for stuff in data:
        for x in cities:
            if x["id"] == str(stuff[4]):
                break
        dis.add(stuff[7])
        bs.append(Building(stuff[0], stuff[1], stuff[2], stuff[3], x["name"], stuff[5], stuff[6], stuff[7], stuff[8], stuff[9], stuff[10], stuff[11]))
    return render_template("buildings.html", bs=bs, dis=dis, City=city)


@app.route('/buildings/<city>/<district>')
def buildings_cd(city, district):
    bs = []
    nh = set()
    cur = db.connection.cursor()
    for x in cities:
        if x["name"] == city:
            break
    cur.execute("SELECT * FROM building WHERE Torn_Down=0 AND City=%s AND District=%s;", (x["id"], district))
    data = cur.fetchall()
    cur.close()
    if len(data) == 0:
        abort(404)
    for stuff in data:
        for x in cities:
            if x["id"] == str(stuff[4]):
                break
        nh.add(stuff[5])
        bs.append(Building(stuff[0], stuff[1], stuff[2], stuff[3], x["name"], stuff[5], stuff[6], stuff[7], stuff[8], stuff[9], stuff[10], stuff[11]))
    return render_template("buildings.html", bs=bs, nh=nh, City=city, District=district)


@app.route('/buildings/<city>/<district>/<neighborhood>')
def buildings_cdn(city, district, neighborhood):
    bs = []
    st = set()
    cur = db.connection.cursor()
    for x in cities:
        if x["name"] == city:
            break
    cur.execute("SELECT * FROM building WHERE Torn_Down=0 AND City=%s AND District=%s AND Neighborhood=%s;", (x["id"], district, neighborhood))
    data = cur.fetchall()
    cur.close()
    if len(data) == 0:
        abort(404)
    for stuff in data:
        for x in cities:
            if x["id"] == str(stuff[4]):
                break
        st.add(stuff[6])
        bs.append(Building(stuff[0], stuff[1], stuff[2], stuff[3], x["name"], stuff[5], stuff[6], stuff[7], stuff[8], stuff[9], stuff[10], stuff[11]))
    return render_template("buildings.html", bs=bs, City=city, District=district, Neighborhood=neighborhood, st=st)


@app.route('/buildings/<city>/<district>/<neighborhood>/<street>')
def buildings_cdns(city, district, neighborhood, street):
    bs = []
    cur = db.connection.cursor()
    for x in cities:
        if x["name"] == city:
            break
    cur.execute("SELECT * FROM building WHERE Torn_Down=0 AND City=%s AND District=%s AND Neighborhood=%s AND Street=%s;", (x["id"], district, neighborhood, street))
    data = cur.fetchall()
    cur.close()
    if len(data) == 0:
        abort(404)
    for stuff in data:
        for x in cities:
            if x["id"] == str(stuff[4]):
                break
        bs.append(Building(stuff[0], stuff[1], stuff[2], stuff[3], x["name"], stuff[5], stuff[6], stuff[7], stuff[8], stuff[9], stuff[10], stuff[11]))
    return render_template("buildings.html", bs=bs, City=city, District=district, Neighborhood=neighborhood, Street=street)


@app.route('/buildings/<int:buildingid>')
def building(buildingid):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM building WHERE BuildingId=%s;", (buildingid,))
    data = cur.fetchone()
    if data is not None:
        for x in cities:
            if x["id"] == str(data[4]):
                break
        cur.execute("SELECT Name_Surname FROM citizen WHERE CitizenshipID=%s;", (data[2],))
        name = cur.fetchone()
        cur.close()
        bing = Building(data[0],data[1],name[0],data[3],x["name"],data[5],data[6],data[7],data[8],data[9],data[10],data[11])
        return render_template("building.html", building=bing)
    else:
        cur.close()
        abort(404)


@app.route('/buildings/<int:buildingid>/reports')
def reports(buildingid):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM report WHERE BuildingId=%s", (buildingid, ))
    report = cur.fetchall()
    cur.close()
    return render_template("reports.html", report=report)

@app.route('/add_complaint/<int:building_id>/<int:apartment_id>', methods=['GET', 'POST'])
@login_required
def add_complaint(building_id, apartment_id):
    if current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("SELECT OwnerId FROM apartment INNER JOIN building ON apartment.BuildingId=building.BuildingId WHERE ApartmentId=%s;",(apartment_id,))
    owner = cur.fetchone()
    if owner is None:
        abort(404)
    if owner[0] != current_user.citizen_id:
        cur.execute("SELECT ApartmentId FROM resident WHERE CitizenshipID=%s;", (current_user.citizen_id, ))
        resides = cur.fetchone()
        if resides is None:
            cur.close()
            abort(403)
        if resides[0] != apartment_id:
            cur.close()
            abort(403)
    if request.method == 'POST':
        reason = request.form.get("Reason")
        cur.execute("insert into complaint (WriterId,Reason,BuildingId) values (%s, %s, %s);", (current_user.citizen_id, reason, building_id))
        cur.execute("SELECT Complaint FROM building WHERE BuildingId=%s;", (building_id,))
        nc = cur.fetchone()
        print(nc[0])
        n = nc[0]+1
        cur.execute("UPDATE building SET Complaint = %s WHERE BuildingId=%s;", (n, building_id))
        db.connection.commit()
        cur.close()
        flash("Complaint added successfully")
        return redirect('/')
    return render_template("add_complaint.html", bid=building_id)


@app.route('/your_complaints')
@login_required
def your_complaints():
    if current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM complaint WHERE WriterId=%s;", (current_user.citizen_id,))
    complaints = cur.fetchall()
    cur.close()
    return render_template("your_complaints.html", complaints=complaints)


@app.route('/update_complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def update_complaint(complaint_id):
    if current_user.is_official:
        abort(403)
    date = datetime.now()
    utc_to_local(date)
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM complaint WHERE ComplaintId=%s;", (complaint_id,))
    complaint = cur.fetchone()
    if complaint[1] != current_user.citizen_id:
        cur.close()
        abort(403)
    if request.method == 'POST':
        reason = request.form.get("Reason")
        cur.execute("UPDATE complaint SET Reason=%s, IssueDate=%s WHERE ComplaintId=%s", (reason, date, complaint_id))
        db.connection.commit()
        cur.close()
        flash("Complaint successfully updated")
        return redirect('/')
    return render_template("add_complaint.html", complaint=complaint)


@app.route('/delete_complaint/<int:complaint_id>')
@login_required
def delete_complaint(complaint_id):
    if current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM complaint INNER JOIN building ON complaint.BuildingId=building.BuildingId WHERE ComplaintId=%s;", (complaint_id,))
    complaint = cur.fetchone()
    if complaint[1] != current_user.citizen_id:
        cur.close()
        abort(403)
    com = complaint[16]-1
    cur.execute("UPDATE building SET Complaint=%s WHERE BuildingId=%s", (com, complaint[3]))
    cur.execute("DELETE FROM complaint WHERE ComplaintId=%s", (complaint_id,))
    db.connection.commit()
    cur.close()
    flash("Complaint successfully deleted")
    return redirect('/')



@app.route('/constructors', methods=['GET', 'POST'])
def constructor():
    fname = ""
    cl = []
    if request.method == 'POST':
        fname = request.form.get("name")
    cur = db.connection.cursor()
    cur.execute("SELECT Name_Surname, Buildings_Built, SUM(Torn_Down) FROM citizen INNER JOIN constructor ON constructor.ConstructorID=citizen.CitizenshipID INNER JOIN building ON constructor.ConstructorID=building.ConstructorID WHERE Name_Surname LIKE '%%%s%%' GROUP BY building.ConstructorID"  % (fname,))
    constructor = cur.fetchall()
    for c in constructor:
        cl.append([c[0], c[1], c[2]])
    print(constructor)
    return render_template("constructor.html", cl=cl)


@app.route("/add_report", methods=['GET', 'POST'])
@login_required
def add_report():
    if not current_user.is_official:
        abort(403)
    if request.method == 'POST':
        bid = request.form.get("building_id")
        safety = request.form.get("safety")
        date = datetime.now()
        utc_to_local(date)
        cur = db.connection.cursor()
        cur.execute("insert into report (SafetyRewiev,WriterId,BuildingId) values (%s, %s, %s);", (safety, current_user.citizen_id, bid))
        cur.execute("UPDATE building SET Complaint=0,LastRewieved=%s,Safety=%s  WHERE BuildingId=%s", (date, safety ,bid))
        cur.execute("DELETE FROM complaint WHERE BuildingId=%s;", (bid, ))
        db.connection.commit()
        cur.close()
        flash("Report added for building")
        return redirect(url_for('building', buildingid=bid))
    return render_template("add_report.html")


@app.route('/add_constructor', methods=['GET', 'POST'])
@login_required
def add_constructor():
    if not current_user.is_official:
        abort(403)
    citizenn = []
    cur = db.connection.cursor()
    cur.execute("SELECT CitizenshipID FROM citizen;")
    citizens = cur.fetchall()
    cur.execute("SELECT ConstructorID FROM constructor;")
    constructors = cur.fetchall()
    for cit in citizens:
        check = True
        for con in constructors:
            if con[0]==cit[0]:
                check = False
                break
        if check:
            citizenn.append(cit[0])
    if request.method == 'POST':
        cid = request.form.get('citizenship_id')
        print(cid)
        cur.execute("INSERT INTO constructor (ConstructorID) values (%s);", (cid, ))
        db.connection.commit()
        cur.close()
        flash("Constructor added")
        return redirect('/')
    cur.close()
    return render_template("add_constructor.html", citizens=citizenn)


@app.route('/new_building', methods=['GET', 'POST'])
@login_required
def add_building():
    cur = db.connection.cursor()
    cur.execute("SELECT ConstructorID FROM constructor;")
    con = cur.fetchall()
    if not current_user.is_official:
        abort(403)
    if request.method=='POST':
        city = request.form.get("city")
        district = request.form.get("district")
        nh = request.form.get("neighborhood")
        street = request.form.get("street")
        cons = request.form.get("constructor_id")
        aps = request.form.get("number_of_apartments")
        bc = request.form.get("building_control")
        cur.execute("INSERT INTO building (BuildingControl, ConstructorID, City, Neighborhood, Street, District) values (%s, %s, %s, %s, %s, %s)", (bc, cons, city, nh, street, district))
        db.connection.commit()
        cur.execute("SELECT Buildings_Built FROM constructor WHERE ConstructorID=%s;", (cons, ))
        bb = cur.fetchone()
        bbb = bb[0]+1
        cur.execute("UPDATE constructor SET Buildings_Built=%s WHERE ConstructorID=%s;", (bbb ,cons))
        db.connection.commit()
        cur.execute("SELECT MAX(BuildingId) FROM Building;")
        bid = cur.fetchone()
        for i in range(int(aps)):
            cur.execute("insert into apartment (OwnerId, BuildingId) values (%s, %s);", (cons, bid[0]))
        db.connection.commit()
        cur.close()
        flash("building added successfully")
        return redirect('/')
    cur.close()
    return render_template("add_building.html", cities=cities, con=con)


@app.route('/buildings/<int:buildingid>/delete_building')
@login_required
def delete_building(buildingid):
    if not current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("DELETE FROM building WHERE BuildingId=%s;", (buildingid,))
    db.connection.commit()
    flash("Building deleted")
    return redirect('/')


@app.route('/buildings/<int:buildingid>/torn_building')
@login_required
def torn_building(buildingid):
    if not current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("UPDATE building SET Torn_Down=1 WHERE BuildingId=%s;", (buildingid,))
    cur.execute("DELETE FROM apartment WHERE BuildingId=%s", (buildingid, ))
    cur.execute("DELETE FROM complaint WHERE BuildingId=%s", (buildingid, ))
    cur.execute("DELETE FROM report WHERE BuildingId=%s", (buildingid, ))
    db.connection.commit()
    cur.close()
    flash("Building marked as torn down")
    return redirect('/')


@app.route('/set_residence', methods=['GET', 'POST'])
@login_required
def set_residence():
    if not current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("SELECT CitizenshipId FROM citizen;")
    cit = cur.fetchall()
    cur.execute("SELECT ApartmentId FROM apartment;")
    aps = cur.fetchall()
    if request.method == 'POST':
        apartment = request.form.get("apartment_id")
        citizen = request.form.get("citizen_id")
        cur.execute("SELECT * FROM resident WHERE CitizenshipID=%s;", (citizen, ))
        check = cur.fetchone()
        if check is not None:
            cur.execute("UPDATE resident SET ApartmentId=%s WHERE CitizenshipID=%s;", (apartment, citizen))
        else:
            cur.execute("INSERT INTO resident (ApartmentId, CitizenshipId) values (%s, %s);", (apartment ,citizen))
        db.connection.commit()
        cur.close()
        flash("Residency Updated successfully")
        return redirect('/')
    cur.close()
    return render_template("set_residence.html", citizen=cit, aps=aps )


@app.route('/set_ownership', methods=['GET', 'POST'])
@login_required
def set_ownership():
    if not current_user.is_official:
        abort(403)
    cur = db.connection.cursor()
    cur.execute("SELECT CitizenshipId FROM citizen;")
    cit = cur.fetchall()
    cur.execute("SELECT ApartmentId FROM apartment;")
    aps = cur.fetchall()
    if request.method == 'POST':
        apartment = request.form.get("apartment_id")
        citizen = request.form.get("citizen_id")
        cur.execute("UPDATE apartment SET OwnerId=%s WHERE ApartmentId=%s;", (citizen, apartment))
        db.connection.commit()
        cur.close()
        flash("Ownership Updated successfully")
        return redirect('/')
    cur.close()
    return render_template("set_residence.html", citizen=cit, aps=aps )


@app.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    if current_user.is_official:
        abort(403)
    if request.method=='POST':
        pw = request.form["password"]
        rpw = request.form["rpassword"]
        if pw == rpw:
            cur = db.connection.cursor()
            pw = hasher.hash(pw)
            cur.execute("UPDATE citizen SET Passkey=%s WHERE CitizenshipId=%s;", (pw, current_user.citizen_id))
            db.connection.commit()
            cur.close()
            flash("Successfully Updated Your Password")
            return redirect("/")
        else:
            flash("Re-entered password doesn't match with the original password")
    return render_template("signup.html")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
