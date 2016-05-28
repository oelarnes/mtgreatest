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
        'champion_id'       : 'int'             ,
        'event_type'        : 'varchar(40)'     ,
        'host_country'      : 'varchar(10)'     ,
        'team_event'        : 'int'             ,
        'event_link'        : 'varchar(320)'    ,
        'process_status'    : 'int'             ,

        #player specific
        #
        #join key
        'player_id'         : 'int'             ,
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
        'result'            : 'int'             ,
        'vs'                : 'varchar(10)'     ,
        'p1_country'        : 'varchar(10)'     ,
        'p2_country'        : 'varchar(10)'     ,
        'elim'              : 'int'             ,
        'bo5'               : 'int'             ,

        #rating
        #...
}

table_definitions = {
        'event_table' : [ 'event_id', 'event_full_name', 'location', 'day_1_date', 'day_1_rounds', 'day_2_date', 'day_2_rounds', 'day_3_date', 'day_3_rounds',
            'day_4_date', 'day_4_rounds', 'num_players', 'ftm_desc', 'fmt_type', 'fmt_primary', 'fmt_secondary', 'fmt_third', 'fmt_fourth', 'season', 'champion_id',
            'event_type', 'host_country', 'event_link', 'team_event', 'process_status' ],
        'player_table' : [ 'player_id', 'country', 'country_2', 'norm_name_1', 'norm_name_2', 'norm_name_3', 'norm_name_4', 'display_name' ],
        'event_player_table' : [ 'event_id', 'player_id', 'norm_name', 'norm_name_alt', 'finish', 'match_point', 'pro_points', 'cash_prize' ],
        'standings_raw_table' : [ 'event_id', 'player_name_raw', 'finish', 'match_points', 'pro_points', 'cash_prize', 'country' ],
        'results_raw_table' : [ 'event_id', 'round_num', 'table_id', 'p1_name_raw', 'p1_country', 'vs', 'p2_name_raw', 'p2_country', 'result_raw', 'elim', 'bo5' ]
}





        



        


