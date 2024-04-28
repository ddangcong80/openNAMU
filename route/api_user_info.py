from .tool.func import *

def api_user_info(user_name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        data_result = {}
        
        # name part
        data_result['render'] = ip_pas(conn, user_name)
        
        # auth part
        curs.execute(db_change("select data from user_set where id = ? and name = 'acl'"), [user_name])
        db_data = curs.fetchall()
        if db_data:
            if db_data[0][0] != 'user':
                curs.execute(db_change("select name from alist where name = ?"), [db_data[0][0]])
                if curs.fetchall() or db_data[0][0] in get_default_admin_group():
                    data_result['auth'] = db_data[0][0]
                else:
                    data_result['auth'] = '1'
            else:
                data_result['auth'] = '1'
        else:
            data_result['auth'] = '0'

        curs.execute(db_change("select data from user_set where id = ? and name = 'auth_date'"), [user_name])
        db_data = curs.fetchall()
        if db_data:
            data_result['auth_date'] = db_data[0][0]
        else:
            data_result['auth_date'] = '0'

        level_data = level_check(conn, user_name)
        data_result['level'] = level_data[0]
        data_result['exp'] = level_data[1]
        data_result['max_exp'] = level_data[2]
            
        # ban part
        if ban_check(conn, user_name)[0] == 0:
            data_result['ban'] = '0'
        else:
            data_result['ban'] = {}
            regex_ban = 0
            
            curs.execute(db_change("select login, block, end, why from rb where band = 'regex' and ongoing = '1'"))
            for db_data in curs.fetchall():
                if re.compile(db_data[1]).search(user_name):
                    regex_ban = 1
                    
                    data_result['ban']['type'] = 'regex'
                    if db_data[0] == 'E':
                        data_result['ban']['login_able'] = '2'
                    elif db_data[0] == 'O':
                        data_result['ban']['login_able'] = '1'
                    else:
                        data_result['ban']['login_able'] = '0'
                        
                    if db_data[2] == '':
                        data_result['ban']['period'] = '0'
                    else:
                        data_result['ban']['period'] = db_data[2]
                        
                    data_result['ban']['reason'] = db_data[3]
                    
                    break
                    
            if regex_ban == 0:
                curs.execute(db_change("select login, block, end, why from rb where block = ? and ongoing = '1'"), [user_name])
                db_data = curs.fetchall()
                if db_data:
                    data_result['ban']['type'] = 'normal'
                    if db_data[0][0] == 'E':
                        data_result['ban']['login_able'] = '2'
                    elif db_data[0][0] == 'O':
                        data_result['ban']['login_able'] = '1'
                    else:
                        data_result['ban']['login_able'] = '0'
                        
                    if db_data[0][2] == '':
                        data_result['ban']['period'] = '0'
                    else:
                        data_result['ban']['period'] = db_data[0][2]
                        
                    data_result['ban']['reason'] = db_data[0][3]
        
        # user document part
        curs.execute(db_change("select title from data where title = ?"), ['user:' + user_name])
        if curs.fetchall():
            data_result['document'] = '1'
        else:
            data_result['document'] = '0'

        # user title part
        curs.execute(db_change('select data from user_set where name = "user_title" and id = ?'), [user_name])
        db_data = curs.fetchall()
        if db_data:
            data_result['user_title'] = db_data[0][0]
        else:
            data_result['user_title'] = ''

        lang_data_list = [
            'user_name',
            'authority',
            'state',
            'member',
            'normal',
            'blocked',
            'type',
            'regex',
            'period',
            'limitless',
            'login_able',
            'why',
            'band_blocked',
            'ip',
            'ban',
            'level',
            'option',
            'edit_request_able',
            'cidr'
        ]
        lang_data = { for_a : get_lang(conn, for_a) for for_a in lang_data_list }
                
        return flask.jsonify({ 'data' : data_result, 'language' : lang_data })