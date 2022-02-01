import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

if __name__ == "__main__":
    cnx = create_engine('postgresql://sqwmtyaiabsiff:7ecca47616bef71798632076ef45a52d3fba58691acbda0766f04bdd87d0155e@ec2-3-222-49-168.compute-1.amazonaws.com:5432/dcr89i9f2cnh2l')

    sql = '''select *
             from public.test_table;'''

    query = text(sql)
    raw_data = pd.read_sql_query(query, cnx)
    
    new_dict = {'listing_id': raw_data.tail(1).iloc[0][0]+1,'added_date': datetime.datetime.now()}

    raw_data = raw_data.append(new_dict, ignore_index = True)

    raw_data.to_sql('test_table', cnx, schema = 'public', index = False, chunksize=100, if_exists='replace', method = 'multi')