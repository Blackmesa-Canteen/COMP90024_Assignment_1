# Here we will write main script with

from mimetypes import init
import os
import random

import sys

# make single script runnable!!!
import time


# from pip import main



sys.path.append(os.path.dirname(sys.path[0]))
print('[debug] running root path:', os.path.dirname(sys.path[0]))

from mpi4py import MPI

from src.config.config_handler import ConfigHandler
from src.handler.result_gather_handler import ResultGatherHandler
from src.handler.test_send_handler import TestSendHandler
from src.util.grid_json_parser import GridJsonParser
from src.util.lang_tag_json_parser import LangTagJsonParser
from src.util.twitter_json_parser import TwitterJsonParser
from src.handler.thread_pool_handler import ThreadPoolHandler
from src.handler.lang_calc_handler import LangCalcHandler


GAP = 0.15

# The world
comm = MPI.COMM_WORLD

# Total Processes
total_processes = comm.Get_size()

# Current Process rank
current_process_rank = comm.Get_rank()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# demo for multi process calc running
# mpiexec -np 8 python /home/xiaotian/Desktop/projects/comp90024_ass_1/COMP90024_Assignment_1/src/main.py
def multi_process_calc():
    thread_demo = ResultGatherHandler(comm)
    if current_process_rank == 0:

        thread_demo.start()

        # fake calculation
        time.sleep(random.randint(1, 3))

        # busy waiting to wait for others
        while not thread_demo.is_finished_receiving():
            pass

        # now we received all res,
        res = thread_demo.get_received_data()

        # insert master's fake result
        res[0] = 0
        print("[debug] received data:", res)

    else:
        # fake calculation
        time.sleep(random.randint(1, 8))

        # send result
        TestSendHandler(comm).start()


# Press the green button in the gutter to run the script.

if __name__ == '__main__':

    '''
    单进程多线程测试
    '''
    # init parser
    config_handler = ConfigHandler()
    lang_tag_parser = LangTagJsonParser()
    grid_parser = GridJsonParser()
    twitter_json_parser = TwitterJsonParser()

    # init data
    twitter_json_parser.parse_valid_coordinate_lang_maps_in_range(start_index=0, step=500000000)
    step = config_handler.get_step()
    main_queue = twitter_json_parser.get_twitter_queue()
    total_row = config_handler.get_upper_bound_rows_per_iteration()
    thread_nums = int( total_row / step)
    job_nums = thread_nums


    print(grid_parser.get_all_grids())


    # Scheduler
    # pool = ThreadPoolHandler(2)

    # print(thread_nums, step, total_row)

    # for i in range(0, 2):
    #     pool.submit(lang_calc, (main_queue, step))

    # result = pool.collect_result()
    # pool.stop()
    # # time.sleep(2)
    # # print(pool)
    # # collect结果和queue的超时时间需要精确把控
    # print("Result: ", result)
    

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
