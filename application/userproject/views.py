from application import app, db
from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for

from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from application.userproject.models import Userproject
from application.userproject.forms import UserProjectForm

@app.route("/userproject/add/")
@login_required
def userproject_form():
    return render_template("userproject/add.html", form = generate_form())

@login_required
def generate_form():
    stmt = text("SELECT Projekti.id, Projekti.name FROM Projekti")
    stmt2 = text("SELECT id, name FROM account")
    resusers = db.engine.execute(stmt2)
    res = db.engine.execute(stmt)
    form = UserProjectForm()
    form.project.choices = [(project.id, project.name) for project in res]
    form.users.choices = [(user.id, user.name) for user in resusers]
    return form

@login_required
def tarkista_paaprojekti_ja_vaihda(accountidparam):
    stmt = text("SELECT * FROM userproject WHERE account_id = :accountid AND paaprojekti = :projekti").params(accountid=accountidparam, projekti=True)
    res = db.engine.execute(stmt)
    if res != None:
        res.close()
        stmt2 = text("UPDATE userproject SET paaprojekti = 'False' WHERE account_id = :accountid AND paaprojekti = :projekti").params(accountid=accountidparam, projekti = True)
        result = db.engine.execute(stmt2)


@app.route("/userproject/linkuser/", methods=["POST"])
@login_required
def userproject_create():
    form = UserProjectForm(request.form)
    
    userproject = Userproject(form.asiakas.data)
    userproject.account_id = form.users.data
    userproject.project_id = form.project.data
    if(form.paaprojekti.data == True):
        tarkista_paaprojekti_ja_vaihda(form.users.data)
    userproject.paaprojekti = form.paaprojekti.data
    userproject.unique_id = int(str(form.users.data) + str(form.project.data))
    
    db.session().add(userproject)
    try:
        db.session().commit()
    except IntegrityError:
        db.session.rollback()
        return render_template("userproject/add.html", form = generate_form(), error = "Käyttäjä on jo liitetty projektiin")

    return redirect(url_for("index"))

