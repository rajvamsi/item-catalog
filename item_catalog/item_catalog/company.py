from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from company_database import Company, Base, Processor, User
from flask import session as login_session
import random
import string
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Company Processor item-catalog"
engine = create_engine(
    'sqlite:///companydata.db',
    connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    company = session.query(Company).all()
    processor = session.query(Processor).all()
    return render_template('login.html', STATE=state,
                           company=company, processor=processor)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                                 json.dumps(
                                            'Current user already connected'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<center><h2><font color="green">Welcome '
    output += login_session['username']
    output += '!</font></h2></center>'
    output += '<center><img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; -webkit-border-radius: 200px;" '
    output += ' " style = "height: 200px;border-radius: 200px;" '
    output += ' " style = "-moz-border-radius: 200px;"></center>" '
    flash("you are now logged in as %s" % login_session['username'])
    print("Done")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        return None


@app.route('/company/JSON')
def companyJSON():
    company = session.query(Company).all()
    return jsonify(company=[c.serialize for c in company])


@app.route('/company/<int:company_id>/main/<int:processor_id>/JSON')
def companyListJSON(company_id, processor_id):
    processor_list = session.query(Processor).filter_by(id=processor_id).one()
    return jsonify(Processor_List=processor_list.serialize)


@app.route('/company/<int:processor_id>/main/JSON')
def processorListJSON(processor_id):
    company = session.query(Company).filter_by(id=processor_id).one()
    processor = session.query(Processor).filter_by(
        processor_id=company.id).all()
    return jsonify(ProcessorList=[i.serialize for i in processor])


@app.route('/company/')
def showCompany():
    company = session.query(Company).all()
    return render_template('company.html', company=company)


@app.route('/company/new/', methods=['GET', 'POST'])
def newCompany():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCompany = Company(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newCompany)
        session.commit()
        return redirect(url_for('showCompany'))
    else:
        return render_template('newCompany.html')


@app.route('/company/<int:company_id>/edit/', methods=['GET', 'POST'])
def editCompany(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCompany = session.query(Company).filter_by(id=company_id).one()
    creater_id = getUserInfo(editedCompany.user_id)
    user_id = getUserInfo(login_session['user_id'])
    if creater_id.id != login_session['user_id']:
        flash("you cannot edit this company"
              "This is belongs to %s" % (creater_id.name))
        return redirect(url_for('showCompany'))
    if request.method == 'POST':
        if request.form['name']:
            editedCompany.name = request.form['name']
            flash("Company Successfully Edited %s" % (editedCompany.name))
            return redirect(url_for('showCompany'))
    else:
        return render_template('editCompany.html', company=editedCompany)


@app.route('/company/<int:company_id>/delete/', methods=['GET', 'POST'])
def deleteCompany(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    companyToDelete = session.query(Company).filter_by(id=company_id).one()
    creater_id = getUserInfo(companyToDelete.user_id)
    user_id = getUserInfo(login_session['user_id'])
    if creater_id.id != login_session['user_id']:
        flash("you cannot delete this company"
              "This is belongs to %s" % (creater_id.name))
        return redirect(url_for('showCompany'))
    if request.method == 'POST':
        session.delete(companyToDelete)
        flash("Successfully Deleted %s" % (companyToDelete.name))
        session.commit()
        return redirect(url_for('showCompany', company_id=company_id))
    else:
        return render_template('deleteCompany.html', company=companyToDelete)


@app.route('/company/<int:company_id>/processor/')
def showProcessors(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    processor = session.query(
        Processor).filter_by(processor_id=company_id).all()
    return render_template('main.html', company=company, processor=processor)


@app.route('/company/<int:processor_id>/new/', methods=['GET', 'POST'])
def newProcessorList(processor_id):
    if 'username' not in login_session:
        return redirect('login')
    company = session.query(Company).filter_by(id=processor_id).one()
    creater_id = getUserInfo(company.user_id)
    user_id = getUserInfo(login_session['user_id'])
    if creater_id.id != login_session['user_id']:
        flash("you cannot add this processor"
              "This is belongs to %s" % (creater_id.name))
        return redirect(url_for('showCompany', company_id=processor_id))
    if request.method == 'POST':
        newList = Processor(
            processor_name=request.form['processor_name'],
            Speciality=request.form['Speciality'],
            cores=request.form['cores'],
            threads=request.form['threads'],
            cache=request.form['cache'],
            processor_id=processor_id,
            user_id=login_session['user_id'])
        session.add(newList)
        session.commit()
        flash("New Processor List %s is created" % (newList))
        return redirect(url_for('showProcessors', company_id=processor_id))
    else:
        return render_template('newprocessor.html', processor_id=processor_id)


@app.route('/company/<int:company_id>/<int:b_id>/edit/',
           methods=['GET', 'POST'])
def editProcessorList(company_id, b_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedList = session.query(Processor).filter_by(id=b_id).one()
    company = session.query(Company).filter_by(id=company_id).one()
    creater_id = getUserInfo(editedList.user_id)
    user_id = getUserInfo(login_session['user_id'])
    if creater_id.id != login_session['user_id']:
        flash("you cannot edit this company"
              "This is belongs to %s" % (creater_id.name))
        return redirect(url_for('showProcessors', company_id=company_id))
    if request.method == 'POST':
        editedList.processor_name = request.form['processor_name']
        editedList.about = request.form['about']
        editedList.Speciality = request.form['Speciality']
        editedList.cores = request.form['cores']
        editedList.threads = request.form['threads']
        editedList.cache = request.form['cache']
        session.add(editedList)
        session.commit()
        flash("Processor List has been edited!!")
        return redirect(url_for('showProcessors', company_id=company_id))
    else:
        return render_template('editprocessor.html',
                               company=company, processor=editedList)


@app.route('/company/<int:processor_id>/<int:list_id>/delete/',
           methods=['GET', 'POST'])
def deleteProcessorList(processor_id, list_id):
    if 'username' not in login_session:
        return redirect('/login')
    company = session.query(Company).filter_by(id=processor_id).one()
    listToDelete = session.query(Processor).filter_by(id=list_id).one()
    creater_id = getUserInfo(listToDelete.user_id)
    user_id = getUserInfo(login_session['user_id'])
    if creater_id.id != login_session['user_id']:
        flash("you cannot edit this company"
              "This is belongs to %s" % (creater_id.name))
        return redirect(url_for('showProcessors', company_id=processor_id))
    if request.method == 'POST':
        session.delete(listToDelete)
        session.commit()
        flash("Processor list has been Deleted!!!")
        return redirect(url_for('showProcessors', company_id=processor_id))
    else:
        return render_template('deleteprocessor.html', lists=listToDelete)


@app.route('/disconnect')
def logout():
    access_token = login_session['access_token']
    print("In gdisconnect access_token is %s", access_token)
    print("User name is:")
    print(login_session['username'])

    if access_token is None:
        print("Access Token is None")
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(uri=url, method='POST', body=None,
                       headers={'Content-Type':
                                'application/x-www-form-urlencoded'})[0]
    print(result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully logged out")
        return redirect(url_for('showCompany'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

