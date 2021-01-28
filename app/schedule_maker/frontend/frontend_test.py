import os
os.environ['environment'] = 'interactive'

import warnings
warnings.filterwarnings("ignore")

from app.interactive_imports import *


def test():
    makedirs('schedules/')
    fn = r"C:\Users\Mi\Desktop\code\git\2020.10-umalat\umalat\app\schedule_maker\data\sample_boiling_plan.xlsx"
    boiling_plan_df = read_boiling_plan(fn)
    start_times = {LineName.WATER: '08:00', LineName.SALT: '07:00'}
    boilings = make_boilings(boiling_plan_df)
    schedule = make_schedule(boilings, cleaning_boiling=None, start_times=start_times)

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception('Ошибка при построении расписания')

    draw_excel_frontend(frontend, open_file=True, fn='schedules/schedule.xlsx')

if __name__ == '__main__':
    test()