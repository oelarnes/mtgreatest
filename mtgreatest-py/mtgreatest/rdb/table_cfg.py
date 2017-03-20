from mtgreatest.rdb import Cursor

column_info = {
        #event specific
        #
        #join key
        'event_id'          : 'varchar(80)'     ,
        #other columns
        'event_full_name'   : 'varchar(160)'    ,
        'location'          : 'varchar(80)'     ,
        'day_1_date'        : 'date'            ,
        'day_1_rounds'      : 'int'             ,
        'day_2_date'        : 'date'            ,
        'day_2_rounds'      : 'int'             ,
        'day_3_date'        : 'date'            ,
        'day_3_rounds'      : 'int'             ,
        'day_4_date'        : 'date'            ,
        'day_4_rounds'      : 'int'             ,
        'num_players'       : 'int'             ,
        'fmt_desc'          : 'varchar(160)'    ,
        'fmt_type'          : 'varchar(20)'     ,
        'fmt_primary'       : 'varchar(40)'     ,
        'fmt_secondary'     : 'varchar(40)'     ,
        'fmt_third'         : 'varchar(40)'     ,
        'fmt_fourth'        : 'varchar(40)'     ,
        'season'            : 'varchar(20)'     ,
        'champion_id'       : 'varchar(12)'     ,
        'event_type'        : 'varchar(40)'     ,
        'host_country'      : 'varchar(10)'     ,
        'team_event'        : 'int'             ,
        'event_link'        : 'varchar(320)'    ,
        'process_status'    : 'int'             ,
        'last_error'        : 'varchar(1600)'   ,

        #player specific
        #
        #join key
        'player_id'         : 'varchar(12)'     ,
        #other columns
        'country'           : 'varchar(10)'     ,
        'country_2'         : 'varchar(10)'     ,
        'norm_name_1'       : 'varchar(80)'     ,
        'norm_name_2'       : 'varchar(80)'     ,
        'norm_name_3'       : 'varchar(80)'     ,
        'norm_name_4'       : 'varchar(80)'     ,
        'display_name'      : 'varchar(80)'     ,

        #event/player
        #
        #columns
        'norm_name'         : 'varchar(80)'     ,
        'norm_name_alt'     : 'varchar(80)'     ,
        'finish'            : 'int'             ,
        'player_name_raw'   : 'varchar(80)'     ,
        'match_points'      : 'int'             ,
        'pro_points'        : 'int'             ,
        'cash_prize'        : 'int'             ,

        #round
        #
        #keys
        'round_num'         : 'int'             ,
        'table_id'          : 'int'             ,
        #other columns
        'p1_name_raw'       : 'varchar(80)'     ,
        'p2_name_raw'       : 'varchar(80)'     ,
        'result_raw'        : 'varchar(20)'     ,
        'vs'                : 'varchar(10)'     ,
        'p1_country'        : 'varchar(10)'     ,
        'p2_country'        : 'varchar(10)'     ,
        'is_elim'           : 'int'             ,
        'bo_num'            : 'int'             ,
        #processed
        'p1_player_id'      : 'varchar(12)'     ,
        'p2_player_id'      : 'varchar(12)'     ,
        'p1_games'          : 'int'             ,
        'p2_games'          : 'int'             ,
        'p1_match_points'   : 'int'             ,
        'p2_match_points'   : 'int'             ,
        'draw_games'        : 'int'             ,
        'result'            : 'int'             , #-1,0,1 for p1 w/l/d

        #rating
        #...

        #conflicts
        'conflict_norm_name': 'varchar(80)'     ,
        'conflict_id'       : 'varchar(12)'     ,
        'player_id_1'       : 'varchar(12)'     ,
        'player_id_2'       : 'varchar(12)'     ,
        'player_id_3'       : 'varchar(12)'     ,
        'player_id_4'       : 'varchar(12)'     
}

table_definitions = {
    'event_table' : [ 
        'event_id', 
        'event_full_name', 
        'location', 
        'day_1_date', 
        'day_1_rounds', 
        'day_2_date', 
        'day_2_rounds', 
        'day_3_date', 
        'day_3_rounds',
        'day_4_date', 
        'day_4_rounds', 
        'num_players', 
        'fmt_desc', 
        'fmt_type', 
        'fmt_primary', 
        'fmt_secondary', 
        'fmt_third', 
        'fmt_fourth', 
        'season', 
        'champion_id',
        'event_type', 
        'host_country', 
        'event_link', 
        'team_event', 
        'process_status', 
        'last_error' 
    ],
    'player_table' : [ 
        'player_id', 
        'country', 
        'country_2', 
        'norm_name_1', 
        'norm_name_2', 
        'norm_name_3', 
        'norm_name_4', 
        'display_name' 
    ],
    'event_player_table' : [ 
        'event_id', 
        'player_id', 
        'norm_name', 
        'norm_name_alt', 
        'finish', 
        'match_points', 
        'pro_points', 
        'cash_prize' 
    ],
    'standings_raw_table' : [ 
        'event_id', 
        'player_name_raw', 
        'finish', 
        'match_points', 
        'pro_points', 
        'cash_prize', 
        'country' 
    ],
    'results_raw_table' : [ 
        'event_id', 
        'round_num', 
        'table_id', 
        'p1_name_raw', 
        'p1_country', 
        'result_raw', 
        'vs', 
        'p2_name_raw', 
        'p2_country', 
        'is_elim', 
        'bo_num' 
    ],
    'results_table' : [
        'event_id',
        'p1_player_id',
        'p2_player_id',
        'round_num',
        'p1_games',
        'p2_games',
        'p1_match_points',
        'p2_match_points',
        'draw_games',
        'result',
    ],
    'conflicts_table' : [
        'conflict_norm_name',
        'conflict_id',
        'player_id_1',
        'player_id_2',
        'player_id_3',
        'player_id_4'
    ],
    'conflict_resulution_table' : [
        'conflict_id',
        'event_id',
        'player_id'
    ]
}

def create_table_statement(table_name, columns):
    statement = 'CREATE TABLE ' + table_name + ' ('
    for column in columns:
        statement += ' ' + column + ' ' + column_info[column] + ','
    statement = statement.rstrip(',')
    statement += ' );'
    return statement

def create_tables():
    cursor = Cursor()
    for table_name, column in table_definitions.iteritems():
        cursor.execute(create_table_statement(table_name, column))
    cursor.close()




        



        


