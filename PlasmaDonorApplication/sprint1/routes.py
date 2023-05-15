from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from main import mysql, flask_bcrypt

sprint1 = Blueprint('sprint1', __name__, template_folder='templates', static_folder='static', static_url_path='/sprint1/static')


@sprint1.route('/')
def home():
    return render_template('home.html')


# Login Verification
@sprint1.route('/login', methods=['POST', 'GET'])
def login():
    data = dict()
    if request.method == 'POST':
        loginform = request.json
        email = loginform['username']
        password = loginform['loginpassword']

        if loginform['title'] != 'Administrator Login':
            if loginform['loginAs'] == 'AsDonor':
                sql = 'SELECT PASSWORD FROM USER_TABLE WHERE email=%s and STATUS=\'Donor\''
            else:
                sql = 'SELECT PASSWORD FROM USER_TABLE WHERE email=%s and STATUS=\'Organisation\''
        else:
            sql = 'SELECT PASSWORD FROM USER_TABLE WHERE email=%s and STATUS=\'Administrator\''
        cursor = mysql.connection.cursor()
        cursor.execute(sql, (email,))
        userdata = cursor.fetchone()

        if userdata:
            if flask_bcrypt.check_password_hash(userdata['PASSWORD'], password):
                session.permanent = True
                if loginform['title'] == 'Administrator Login':
                    session['ADMINISTRATOR'] = 'active'
                    data['status'] = 'logged-in'
                    data['user'] = 'ADMIN'
                else:
                    if loginform['loginAs'] == 'AsDonor':
                        pd_sql = 'SELECT userid FROM user_table WHERE email=%s'
                        cursor.execute(pd_sql, (email,))
                        username = cursor.fetchone()

                        un_sql = 'select fname, lname from personaldetails where email=%s'
                        cursor.execute(un_sql, (email,))
                        name_of_the_donor = cursor.fetchone()
                        # Adding user to session
                        session['user'] = username['userid']
                        session['username'] = name_of_the_donor['fname'] + ' ' + name_of_the_donor['lname']
                        session['donor-email'] = email
                        data['user'] = 'Donor'
                        data['status'] = 'logged-in'
                    else:
                        session['Organisation'] = email
                        data['status'] = 'logged-in'
                        data['user'] = 'Org'
            else:
                data['status'] = 'Invalid-Password'
        else:
            data['status'] = 'Invalid-User'
        cursor.close()
        return jsonify(data)


@sprint1.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    session.pop('donor-email', None)
    return redirect(url_for('sprint1.home'))


@sprint1.route('/admin-logout')
def admin_logout():
    session.pop('ADMINISTRATOR', None)
    return redirect(url_for('sprint2.administrator_login'))


@sprint1.route('/org-logout')
def org_logout():
    session.pop('Organisation', None)
    return redirect(url_for('sprint1.home'))