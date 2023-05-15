from main import mysql


def display_donors(sql):
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    res = []
    dictionary = cursor.fetchone()
    while dictionary:
        for x in dictionary:
            dictionary[x] = str(dictionary[x]).strip()
        res.append(dictionary)
        dictionary = cursor.fetchone()
    cursor.close()
    return res


def filter_by_one_param(sql, filter_by):
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (filter_by,))
    filters = cursor.fetchone()

    res = []
    while filters:
        res.append(filters)
        filters = cursor.fetchone()
    cursor.close()
    return res


def city_filter(state):
    res = []
    cursor = mysql.connection.cursor()
    if state is not None:
        sql = 'select distinct CITY from PERSONALDETAILS where STATE=%s'
        cursor.execute(sql, (state,))
    else:
        sql = 'select distinct CITY from PERSONALDETAILS'
        cursor.execute(sql)
    filters = cursor.fetchone()

    while filters:
        if filters['CITY'] not in res:
            res.append(filters['CITY'])
        filters = cursor.fetchone()
    cursor.close()
    res.sort()
    return res


def filter_by_two_params(sql, param1, param2):
    res = []
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (param1, param2))
    filters = cursor.fetchone()
    while filters:
        res.append(filters)
        filters = cursor.fetchone()
    cursor.close()
    return res


def filter_by_one(state, city, locality):
    sql = ""
    param1 = ""
    param2 = ""
    param3 = ""
    if city is None and locality is None:
        sql = 'select distinct CITY, LOCALITY from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s'
        param1 = state
        param2 = 'CITY'
        param3 = 'LOCALITY'
    elif state is None and locality is None:
        sql = 'select distinct STATE, LOCALITY from ORGANISATION_DETAILS where APPROVED=\'YES\' and CITY=%s'
        param1 = city
        param2 = 'STATE'
        param3 = 'LOCALITY'
    elif state is None and city is None:
        sql = 'select distinct STATE, CITY from ORGANISATION_DETAILS where APPROVED=\'YES\' and LOCALITY=%s'
        param1 = locality
        param2 = 'STATE'
        param3 = 'CITY'
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (param1,))
    fetch = cursor.fetchone()

    res1, res2 = [], []
    while fetch:
        if fetch[param2] not in res1:
            res1.append(fetch[param2])
        if fetch[param3] not in res2:
            res2.append(fetch[param3])
        fetch = cursor.fetchone()
    cursor.close()
    d = {'res1': res1, 'res2': res2}
    return d


def filter_by_two(state, city, locality):
    sql = ""
    param1 = ""
    param2 = ""
    param3 = ""
    if locality is None:
        sql = 'select distinct LOCALITY from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s and CITY=%s'
        param1 = state
        param2 = city
        param3 = 'LOCALITY'
    elif city is None:
        sql = 'select distinct CITY from ORGANISATION_DETAILS where APPROVED=\'YES\' and STATE=%s and LOCALITY=%s'
        param1 = state
        param2 = locality
        param3 = 'CITY'
    elif state is None:
        sql = 'select distinct STATE from ORGANISATION_DETAILS where APPROVED=\'YES\' and CITY=%s and LOCALITY=%s'
        param1 = city
        param2 = locality
        param3 = 'STATE'
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (param1, param2))
    fetch = cursor.fetchone()

    res = []
    while fetch:
        if fetch[param3] not in res:
            res.append(fetch[param3])
        fetch = cursor.fetchone()
    cursor.close()
    return res


def display_all_option(sql):
    res1, res2, res3 = [], [], []
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    fetch = cursor.fetchone()
    while fetch:
        if fetch['state'] not in res1:
            res1.append(fetch['state'])
        if fetch['city'] not in res2:
            res2.append(fetch['city'])
        if fetch['locality'] not in res3:
            res3.append(fetch['locality'])
        fetch = cursor.fetchone()
    cursor.close()
    d = {'res1': res1, 'res2': res2, 'res3': res3}
    return d