from application import db
from flask_login import login_required, current_user
from application.models import Base
from datetime import datetime, date

import os

from sqlalchemy.sql import text

def jako_minuuteiksi(minuutit):
    if minuutit is None:
        return 0
    else:
        return minuutit/60

class Kirjaus(Base):
    
    sisaankirjaus = db.Column(db.DateTime, default=db.func.current_timestamp())
    uloskirjaus = db.Column(db.DateTime, nullable=True)
    tehdytminuutit = db.Column(db.Integer, nullable=True)
    kertyma = db.Column(db.Integer, nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    userproject_id = db.Column(db.Integer, db.ForeignKey('userproject.id'), nullable=False)

    def __init__(self, sisaankirjaus):
        self.sisaankirjaus = sisaankirjaus
   
    # haetaan kirjaus jos on, missä uloskirjaus null, eli käytetty sisäänleimaa nappia
    @staticmethod
    @login_required
    def find_kirjaus_with_null():
        stmt = text("SELECT * FROM Kirjaus WHERE account_id = :accountid AND uloskirjaus IS NULL").params(accountid = current_user.id)
        res = db.engine.execute(stmt)
        palautus = []
        for row in res:
            palautus.append({"id":row[0], "sisaankirjaus":datetime.strftime(row[3] if os.environ.get("HEROKU") else datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f"), "%Y-%m-%d %H:%M:%S"), "uloskirjaus":row[4]})
        return palautus

    # haetaan saldo, eli kertymä summana
    @staticmethod
    @login_required
    def get_saldo(userprojektid):
        stmt = text("SELECT SUM(kertyma) FROM Kirjaus WHERE account_id = :accountid AND userproject_id = :userprojekti").params(accountid = current_user.id, userprojekti = userprojektid)
        res = db.engine.execute(stmt)
        for row in res:
            return row[0]


    # asiakkaan yhteenveto tehdyistä tunneista
    @staticmethod
    def asiakas_yhteenveto(projekti):
        stmt = text("SELECT SUM(Kirjaus.tehdytminuutit), Account.name, Projekti.name AS projektinimi FROM Kirjaus INNER JOIN Account ON Account.id = Kirjaus.account_id INNER JOIN Userproject ON Userproject.project_id = :projekti AND Userproject.account_id = Kirjaus.account_id AND Kirjaus.userproject_id = Userproject.id INNER JOIN Projekti ON Projekti.id = :projekti GROUP BY Account.name, Projekti.name ORDER BY Account.name ASC").params(projekti = projekti)
        res = db.engine.execute(stmt)
        response = []
        if res is None:
            return response
        else:
            for row in res:
                response.append({"tunnit":jako_minuuteiksi(row[0]), "name":row[1], "projekti":row[2]})
            return response

#lasketaan kertymä tehdystä päivästä sisaankirjaus-uloskirjaus minuuteiksi ja - vakiotyoaika
def laske_kertyma(minuutit, userprojekti):
    stmtfirst = text("SELECT project_id FROM userproject WHERE userproject.id = :userproject").params(userproject = userprojekti)
    res2 = db.session().execute(stmtfirst)
    row2 = res2.fetchone()
    stmt = text("SELECT vakiotyoaika FROM projekti WHERE id = :projekti_id").params(projekti_id=row2['project_id'])
    res = db.session().execute(stmt)
    row = res.fetchone()
    vakiotyoaika = row['vakiotyoaika']
    kertyma = minuutit-vakiotyoaika
    return kertyma

