from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from sprint3.utils import *
from sprint4.utils import donor_req_count, donate_req, donors_info
import datetime
from main import mysql

sprint4 = Blueprint('sprint4', __name__, template_folder='templates', static_folder='static', static_url_path='/sprint4/static')


@sprint4.route('/donate-plasma', methods=['POST', 'GET'])
def donate():
    if 'user' in session:
        if request.method == 'POST':
            response = dict()
            select = request.json
            print(select)
            if 'state' in select and 'city' in select and 'locality' in select:
                if select['state'] != 'all' and select['city'] == 'all' and select['locality'] == 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s order by NAME'
                    response['filter'] = filter_by_one_param(sql, select['state'])
                    temp = filter_by_one(select['state'], None, None)
                    response['filterCity'] = temp['res1']
                    response['filterLocality'] = temp['res2']
                    response['filter_city_select'] = 'YES'
                    response['filter_locality_select'] = 'YES'
                    return jsonify(response)

                elif select['state'] != 'all' and select['city'] != 'all' and select['locality'] == 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s and CITY=%s order by NAME'
                    response['filter'] = filter_by_two_params(sql, select['state'], select['city'])
                    response['filter_locality_select'] = 'YES'
                    response['filterLocality'] = filter_by_two(select['state'], select['city'], None)
                    return jsonify(response)

                elif select['state'] != 'all' and select['city'] == 'all' and select['locality'] != 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s and LOCALITY=%s order by NAME'
                    response['filter'] = filter_by_two_params(sql, select['state'], select['locality'])
                    response['filter_city_select'] = 'YES'
                    response['filterLocality'] = filter_by_two(select['state'], None, select['locality'])
                    return jsonify(response)

                elif select['state'] == 'all' and select['city'] != 'all' and select['locality'] == 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and CITY=%s order by NAME'
                    response['filter'] = filter_by_one_param(sql, select['city'])
                    temp = filter_by_one(None, select['city'], None)
                    response['filter_locality_select'] = 'YES'
                    response['filter_state_select'] = 'YES'
                    response['filterState'] = temp['res1']
                    response['filterLocality'] = temp['res2']
                    return jsonify(response)

                elif select['state'] == 'all' and select['city'] != 'all' and select['locality'] != 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and CITY=%s and LOCALITY=%s order by NAME'
                    response['filter'] = filter_by_two_params(sql, select['city'], select['locality'])
                    response['filter_state_select'] = 'YES'
                    response['filterState'] = filter_by_two(None, select['city'], select['locality'])
                    return jsonify(response)

                elif select['state'] == 'all' and select['city'] == 'all' and select['locality'] != 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and LOCALITY=%s order by NAME'
                    response['filter'] = filter_by_one_param(sql, select['locality'])
                    temp = filter_by_one(None, None, select['locality'])
                    response['filter_state_select'] = 'YES'
                    response['filter_city_select'] = 'YES'
                    response['filterState'] = temp['res1']
                    response['filterCity'] = temp['res2']
                    return jsonify(response)

                elif select['state'] == 'all' and select['city'] == 'all' and select['locality'] == 'all':
                    sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' order by NAME'
                    response['filter'] = display_donors(sql)
                    response['filter_state_select'] = 'YES'
                    response['filter_city_select'] = 'YES'
                    response['filter_locality_select'] = 'YES'
                    temp = display_all_option(sql)
                    response['filterState'] = temp['res1']
                    response['filterCity'] = temp['res2']
                    response['filterCity'] = temp['res3']
                    return jsonify(response)

                sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s and CITY=%s and LOCALITY=%s order by NAME'
                cursor = mysql.connection.cursor()
                cursor.execute(sql, (select['state'], select['city'], select['locality']))
                fetch = cursor.fetchone()

                res = []
                while fetch:
                    res.append(fetch)
                    fetch = cursor.fetchone()
                response['filter'] = res
                cursor.close()
                return jsonify(response)
            elif 'email' in select:
                counter = donor_req_count(session['donor-email'])

                date_format = "%Y-%m-%d %H:%M:%S"
                if counter < 5:
                    temp = donors_info(session['donor-email'])
                    if counter == 0:
                        donate_req(session['donor-email'], select['email'], select['name'], temp['B_group'], temp['Name'], temp['Contact'])
                        response['donate_req_status'] = 'Success'
                    else:
                        sql = 'select ORG_EMAIL from DONATE_REQUESTS where DONOR_EMAIL=%s and ORG_EMAIL=%s'
                        cursor = mysql.connection.cursor()
                        cursor.execute(sql, (session['donor-email'], select['email']))
                        fetch = cursor.fetchone()
                        if fetch:
                            response['donate_req_status'] = 'Already'
                        else:
                            donate_req(session['donor-email'], select['email'], select['name'], temp['B_group'], temp['Name'], temp['Contact'])
                            response['donate_req_status'] = 'Success'
                elif counter >= 5:
                    sql = 'select * from DONATE_REQUESTS where DONOR_EMAIL=%s'
                    cursor = mysql.connection.cursor()
                    cursor.execute(sql, (session['donor-email'],))
                    fetch = cursor.fetchone()

                    while fetch:
                        no_of_days = (datetime.datetime.now() - datetime.datetime.strptime(fetch['REQUEST_MADE_TIME'], date_format)).days
                        if fetch['ORG_EMAIL'] == 'email' and no_of_days >= 2:
                            sql2 = 'delete from DONATE_REQUESTS where DONOR_EMAIL=%s and ORG_EMAIL=%s'
                            cursor = mysql.connection.cursor()
                            cursor.execute(sql2, (session['donor-email'], fetch['org_email']))
                        fetch = cursor.fetchone()

                    if donor_req_count(session['donor-email'])['1'] < 5:
                        temp = donors_info(session['donor-email'])
                        donate_req(session['donor-email'], select['email'], select['name'], temp['B_group'], temp['Name'], temp['Contact'])
                        response['donate_req_status'] = 'Success'
                    else:
                        response['donate_req_status'] = 'After'
                    cursor.close()
                return response
        else:
            sql = 'select * from ORGANISATION_DETAILS where APPROVED=\'YES\' order by NAME'
            cursor = mysql.connection.cursor()
            cursor.execute(sql)
            fetch = cursor.fetchone()

            res, cities, states, locality = [], [], [], []
            while fetch:
                if fetch['city'] not in cities:
                    cities.append(fetch['city'])
                if fetch['state'] not in states:
                    states.append(fetch['state'])
                if fetch['locality'] not in locality:
                    locality.append(fetch['locality'])
                res.append(fetch)
                fetch = cursor.fetchone()

            states.sort()
            cities.sort()
            locality.sort()
            return render_template('donate.html', res=res, cities=cities, states=states, locality=locality)
    else:
        return redirect(url_for('sprint3.login_as', redirect_to='donor'))


@sprint4.route('/donor-profile', methods=['GET', 'POST'])
def donor_profile():
    if 'user' in session:
        if request.method == 'POST':
            response = dict()
            org_email = request.json
            sql = 'delete from DONATE_REQUESTS where DONOR_EMAIL=%s and ORG_EMAIL=%s'
            cursor = mysql.connection.cursor()
            cursor.execute(sql, (session['donor-email'], org_email['org-email']))
            cursor.connection.commit()
            cursor.close()
            response['CancelStatus'] = 'True'
            return response
        else:
            sql = 'select * from DONATE_REQUESTS where DONOR_EMAIL=%s'
            cursor = mysql.connection.cursor()
            cursor.execute(sql, (session['donor-email'],))
            fetch = cursor.fetchone()

            res = []
            while fetch:
                res.append(fetch)
                fetch = cursor.fetchone()
            return render_template('donor_profile.html', res=res)
    else:
        return redirect(url_for('sprint3.login_as', redirect_to='donor'))