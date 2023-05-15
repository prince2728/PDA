from main import mysql
import datetime


def donor_req_count(donor_email):
    sql = 'select count(DONOR_EMAIL) from DONATE_REQUESTS where DONOR_EMAIL=%s'
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (donor_email, ))
    res = cursor.fetchone()
    cursor.close()
    return res['count(DONOR_EMAIL)']


def donate_req(donor_email, org_email, org_name, b_group, donor_name, donor_contact):
    date_format = "%Y-%m-%d %H:%M:%S"

    sql = 'insert into DONATE_REQUESTS values (%s, %s, %s, %s, %s, %s, %s, %s)'
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (donor_email, org_email, 'PENDING', datetime.datetime.strftime(datetime.datetime.now(), date_format), org_name, b_group, donor_name, donor_contact))
    cursor.connection.commit()
    cursor.close()


def donors_info(email):
    sql = 'select * from PERSONALDETAILS where EMAIL=%s'
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (email,))
    fetch = cursor.fetchone()
    d = {'B_group': fetch['bloodgroup'], 'Name': fetch['fname']+' '+fetch['lname'], 'Contact': fetch['phonenumber']}
    return d