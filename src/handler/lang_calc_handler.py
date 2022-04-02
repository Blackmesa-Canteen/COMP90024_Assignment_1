# author: YuanZhi Shang

import logging

import threading
from src.util.twitter_json_parser import TwitterJsonParser
from src.config.config_handler import ConfigHandler
from src.util.grid_json_parser import GridJsonParser
from mpi4py import MPI


comm = MPI.COMM_WORLD    
class LangCalcHandler:

    def __init__(self, grid_parser, lang_parser):
        self._thread_id = threading.current_thread().name
        self._table = grid_parser.get_raw_table()
        self._grid_parser = grid_parser
        self._lang_parser = lang_parser
    '''
    Update per-thread table

    table: 'A1':[num, set(), {}]
    '''
    def handle(self, message):            
        area = self._grid_parser.which_grid(tuple(message['coordinates']))
        lang = self._lang_parser.get_lang_by_tag_name(message['lang_tag'])
        record = self._table[area]

        # update tweet num
        record[0] += 1

        # update lang num
        record[1].add(lang)

        # update ranks
        lang_dict = record[2]

        if lang in lang_dict:
            lang_dict[lang] += 1
        else:
            lang_dict[lang] = 1

    def result(self):
        return self._table

    '''
    Union all table from a table list

    input: table_list [table1, table2, table3, ... ]
    out: table {'A1':[num, (), {}], 'B1':[num, (), {}], .... }
    '''
    @staticmethod
    def table_union(table_list, grid_parser):
        raw_table = grid_parser.get_raw_table()    

        for table in table_list:
            for key in table.keys():
                # update num
                raw_table[key][0] += table[key][0]

                # update lang num
                raw_table[key][1] = raw_table[key][1].union(table[key][1])

                # update lang rank
                raw_lang_dict = raw_table[key][2]
                lang_dict = table[key][2]

                for lang in lang_dict.keys():
                    
                    if lang in raw_lang_dict:
                        raw_lang_dict[lang] += lang_dict[lang]
                    else:
                        raw_lang_dict[lang] = lang_dict[lang]
        return raw_table

    @staticmethod
    def lang_calc(args):

        thread_id = threading.current_thread().name
        # print("[INFO] Thread ", thread_id, " start job")
        main_queue, step, grid_parser, lang_tag_parser = args
        lang_calc_handler = LangCalcHandler(grid_parser, lang_tag_parser)
        records = 0
        while step != 0:
            if main_queue.empty():
                break
            else:
                try:
                    message = main_queue.get(block=False)
                    lang_calc_handler.handle(message)
                    records += 1
                except Exception as e:
                    return lang_calc_handler.result()
            step -= 1
        return lang_calc_handler.result()

    @staticmethod
    def view(final_table, check=False):

        print ("\nOUTPUT: \n{:<5} {:<5} {:<5} {:<10}".format('Cell','#Total Tweets','#Number of Languages Used', '#Top 10 Languages & #Tweets)'))
        total_tweets = 0
        # simple visualise
        for key in final_table.keys():
            record = final_table[key]
            lang_vs_num = record[2]
            lang_types_num = record[1]
            tweets = record[0]

            total_tweets += tweets
            if check:
                assert (len(record[2]) == lang_types_num)
                sum = 0
                for lang in lang_vs_num.keys():
                    sum += lang_vs_num[lang]
                assert (sum == tweets)
            
            records_list = final_table[key]
            
            TotalTweets = records_list[0]
            NumberOfLanguage = records_list[1]
            TOPTENLang = records_list[2]

            # print(key, ": ", final_table[key], "\n")
            print ("{0}     {1}     {2}     {3}".format(key, TotalTweets, NumberOfLanguage, TOPTENLang))


        print(" Toal records: ", total_tweets)

