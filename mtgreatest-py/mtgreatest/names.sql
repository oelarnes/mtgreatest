select min(p1_name_raw), event_id from results_raw_table where elim=1 group by event_id;
