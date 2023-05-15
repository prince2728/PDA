import os.path

from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from main import mysql, mail, flask_bcrypt, app
from flask_mail import Message
from sprint2.utils import token_generator, verify_token, generate_random_password
import jwt
from werkzeug.utils import secure_filename

sprint2 = Blueprint('sprint2', __name__, template_folder='templates', static_folder='static', static_url_path='/sprint2/static')


# Registration-Form Template Render
@sprint2.route('/register-as-donor')
def register():
    return render_template('registrations/user_registration.html')


# User Exist Validation
@sprint2.route('/user-exist', methods=['POST'])
def userexist():
    if request.method == 'POST':
        d = dict()
        form = request.json
        email = form['email']

        sql = 'SELECT * FROM USER_TABLE WHERE email=%s'
        cursor = mysql.connection.cursor()
        cursor.execute(sql, (email,))
        flag = cursor.fetchall()

        if flag:
            d['status'] = 'Exist'
        else:
            d['status'] = 'New User'
        return jsonify(d)


# SignUp-Form Submission
@sprint2.route('/form-submission', methods=['GET', 'POST'])
def formsubmission():
    if request.method == 'POST':
        d = request.json
        # Form-1 Data
        email = d['email']
        pwd = d['password']
        # Password Hashing
        password = flask_bcrypt.generate_password_hash(pwd, rounds=12)

        # Form-2 Data
        fname = d['fname']
        lname = d['lname']
        phonenumber = d['phonenumber']
        dob = d['dateofbirth']
        age = int(d['age'])
        bloodgroup = d['bloodgroup']
        address = d['address']
        pincode = d['pincode']
        city = d['city']
        state = d['state']

        bg_image = d['bgimage']
        bgimg = bg_image.filename

        # Form-1 Submission
        insert_sql1 = 'INSERT INTO USER_TABLE VALUES (default, %s, %s, null, %s)'
        cursor = mysql.connection.cursor()
        cursor.execute(insert_sql1, (email, password, 'Donor'))
        cursor.connection.commit()

        # Form-2 Submission
        filename = secure_filename(bgimg)
        bg_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        insert_sql2 = 'INSERT INTO PERSONALDETAILS VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(insert_sql2, (fname, lname, email, dob, age, phonenumber, bloodgroup, address, pincode, city, state, bgimg))
        cursor.connection.commit()
        cursor.close()

        data = dict()
        data['status'] = 'success'
        return jsonify(data)


# Request Reset Form
@sprint2.route('/request-reset', methods=['GET', 'POST'])
def request_reset_form():
    if request.method == 'POST':
        d = dict()
        data = request.json
        email = data['email']

        sql = 'SELECT EMAIL FROM USER_TABLE WHERE email=%s'
        cursor = mysql.connection.cursor()
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        if user:
            d['status'] = 'Exist'
            token = token_generator(user['EMAIL'])
            msg = Message('Password Reset Link', sender='noreplyplasmadonor@gmail.com', recipients=[user['EMAIL']])
            msg.body = f'''Password reset link 
{url_for('sprint2.password_reset', token=token, _external=True)}'''
            mail.send(msg)
        else:
            d['status'] = 'Invalid'
        cursor.close()
        return jsonify(d)
    else:
        return render_template('registrations/request_reset_form.html')


@sprint2.route('/reset-password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    d = dict()
    if request.method == 'POST':
        data = request.json
        new_pwd = data['new_password']
        email = session['email']
        if email:
            new_password = flask_bcrypt.generate_password_hash(new_pwd, rounds=12)
            update_sql = 'UPDATE USER_TABLE SET PASSWORD=%s WHERE email=%s'
            cursor = mysql.connection.cursor()
            cursor.execute(update_sql, (new_password, email))
            cursor.connection.commit()
            # Deleting link to make token invalid
            delete_link = 'UPDATE USER_TABLE SET RESET_LINK=NULL WHERE  EMAIL=%s'
            cursor.execute(delete_link, (email,))
            cursor.connection.commit()
            cursor.close()
            d['status'] = 'PasswordUpdated'
            return jsonify(d)
    else:
        try:
            user = verify_token(token)
            if user:
                email = user["EMAIL"]

                sql = 'SELECT RESET_LINK, STATUS FROM USER_TABLE WHERE EMAIL=%s'
                cursor = mysql.connection.cursor()
                cursor.execute(sql, (email,))
                reset_link = cursor.fetchone()
                cursor.close()

                if reset_link['RESET_LINK'] == token:
                    session['email'] = email
                    return render_template('registrations/password_reset.html', BtnTyp=reset_link['STATUS'])
                else:
                    return redirect(url_for('sprint2.request_reset_form'))

        except jwt.exceptions.ExpiredSignatureError:
            return redirect(url_for('sprint2.request_reset_form'))


@sprint2.route('/register-as-org', methods=['GET', 'POST'])
def sign_up_as_org():
    if request.method == 'POST':
        response = dict()
        data = request.json

        sql = 'select * from USER_TABLE where EMAIL=%s'
        cursor = mysql.connection.cursor()
        cursor.execute(sql, (data['org_email'],))
        user = cursor.fetchone()
        cursor.close()
        print(user)

        if user:
            response['status'] = 'Org-Exist'
        else:
            sql = 'select * from ORGANISATION_DETAILS where EMAIL=%s'
            cursor = mysql.connection.cursor()
            cursor.execute(sql, (data['org_email'],))
            user = cursor.fetchone()
            cursor.close()

            if user:
                response['status'] = 'PENDING'
                return jsonify(response)

            sql2 = 'insert into ORGANISATION_DETAILS values (default, %s, %s, %s, %s, %s, %s, %s, %s, NULL)'
            cursor = mysql.connection.cursor()
            cursor.execute(sql2, (data['org_name'], data['org_email'], data['org_contact'], data['org_address'], data['org_locality'], data['org_city'], data['org_state'], int(data['org_pincode'])))
            cursor.connection.commit()
            cursor.close()
            response['status'] = 'New-user'
        return jsonify(response)
    else:
        return render_template('registrations/organisation_registration.html')


@sprint2.route('/Administrator', methods=['GET', 'POST'])
def administrator():
    if 'ADMINISTRATOR' in session:
        if request.method == 'POST':
            data = request.json
            if 'email' in data and 'action' in data:
                response = dict()
                if data['action'] == 'approve':
                    pwd = generate_random_password()

                    sql = 'insert into USER_TABLE values (default, %s, %s, NULL, %s)'
                    cursor = mysql.connection.cursor()
                    cursor.execute(sql, (data['email'], (flask_bcrypt.generate_password_hash(pwd, rounds=12)), 'Organisation'))
                    cursor.connection.commit()
                    cursor.close()

                    msg = Message('Verification Status', sender='noreplyplasmadonor@gmail.com', recipients=[data['email']])
                    msg.body = f'''We have approved your organisation. Find your login credentials below,
Username: { data['email'] }
Password: { pwd }'''
                    mail.send(msg)
                    sql2 = 'update ORGANISATION_DETAILS set APPROVED=%s where EMAIL=%s'
                    cursor = mysql.connection.cursor()
                    cursor.execute(sql2, ('YES', data['email']))
                    cursor.connection.commit()
                    cursor.close()

                    response['action'] = 'Approved'
                else:
                    sql2 = 'update ORGANISATION_DETAILS set APPROVED=%s where EMAIL=%s'
                    cursor = mysql.connection.cursor()
                    cursor.execute(sql2, ('NO', data['email']))
                    cursor.connection.commit()
                    cursor.close()
                    response['action'] = 'Declined'
                return response
        else:
            sql = 'select * from ORGANISATION_DETAILS'
            cursor = mysql.connection.cursor()
            cursor.execute(sql)
            fetch = cursor.fetchone()

            res = []
            res1 = []
            res2 = []
            while fetch:
                if fetch['approved'] is None:
                    res.append(fetch)
                elif fetch['approved'] == 'YES':
                    res1.append(fetch)
                else:
                    res2.append(fetch)
                fetch = cursor.fetchone()

            cursor.close()
            return render_template('administrator.html', res=res, approved=res1, declined=res2)
    else:
        return redirect(url_for('sprint2.administrator_login'))


@sprint2.route('/administrator-login')
def administrator_login():
    return render_template('registrations/administrator_login.html')


def converttobinarydata(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


@sprint2.route('/demo', methods=['GET', 'POST'])
def demo1():
    if request.method == "POST":
        temp = request.files['img-demo']
        if temp:
            filename = secure_filename(temp.filename)
            temp.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('static', filename='uploads/' + filename))
        else:
            print('no')
    return render_template('sample.html')