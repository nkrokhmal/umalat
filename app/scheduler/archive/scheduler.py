from app.imports.runtime import *
from app.scheduler.frontend import *


class BoilingPlanner:
    def read_boiling_plan(self, fn):
        pass

    def saturate(self, df):
        return df


class ScheduleMaker:
    def make_schedule(self, boiling_plan_df, start_times=None, first_boiling_id=None):
        pass


class FrontendWrapper:
    def __init__(self, style):
        self.style = style

    def wrap_frontend(self, schedule):
        pass


class Scheduler:
    def __init__(self, name, boiling_planner, schedule_maker, frontend_wrapper):
        self.name = name
        self.boiling_planner = boiling_planner
        self.scheduler_maker = schedule_maker
        self.frontend_wrapper = frontend_wrapper

    def submit(
        self,
        boiling_plan_fn,
        path,
        prefix,
        start_times=None,
        first_boiling_id=1,
        open_file=False,
    ):
        utils.makedirs(path)
        boiling_plan_df = self.boiling_planner.read_boiling_plan(boiling_plan_fn)

        schedule = self.scheduler_maker.make_schedule(
            boiling_plan_df,
            start_times=start_times,
            first_batch_id=first_boiling_id,
        )

        try:
            frontend = self.frontend_wrapper.wrap_frontend(schedule)
        except Exception as e:
            raise Exception("Ошибка при построении расписания")

        with code("Dump schedule as pickle file"):
            base_fn = f"Расписание {self.name}.pickle"
            if prefix:
                base_fn = prefix + " " + base_fn
            output_pickle_fn = os.path.join(path, base_fn)
            output_pickle_fn = utils.SplitFile(output_pickle_fn).get_new()

            with open(output_pickle_fn, "wb") as f:
                pickle.dump(schedule.to_dict(), f)

        with code("Dump frontend as excel file"):
            base_fn = f"Расписание {self.name}.xlsx"
            if prefix:
                base_fn = prefix + " " + base_fn
            output_fn = os.path.join(path, base_fn)

            draw_excel_frontend(
                frontend,
                open_file=open_file,
                fn=output_fn,
                style=self.frontend_wrapper.style,
            )

        return {"schedule": schedule, "frontend": frontend}
