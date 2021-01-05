from utils_ak.interactive_imports import *

ERROR = 1e-5
EVENT_MANAGER = SimpleEventManager()


class MeltingLine:
    def __init__(self, plan, cooling_line, configuration_time=300):
        self.plan = plan
        self.plan['collected'] = 0

        self.cur_row_id = 0
        self.cur_bff = None
        self.cur_speed = None
        self.last_ts = None
        self.cur_cooling_id = None

        self.logger = logging.getLogger('MeltingLine')
        self.configuration_time = 300
        self.cooling_line = cooling_line

    def update(self, topic, ts, event):
        self.logger.info(('Melting line update', ts))

        if len(self.plan) == 0:
            return

        if self.cur_speed:
            produced = (ts - self.last_ts) * self.cur_speed / 3600
            self.logger.info(('Produced', produced, self.cur_bff))
            self.plan.at[self.cur_row_id, 'collected'] += produced

        self.logger.info('Current plan \n' + str(self.plan))

        self.last_ts = ts

        assert self.plan.at[self.cur_row_id, 'collected'] < self.plan.at[self.cur_row_id, 'kg'] + ERROR

        # set new plan row
        if abs(self.plan.at[self.cur_row_id, 'collected'] - self.plan.at[self.cur_row_id, 'kg']) < ERROR:
            if self.cur_speed:
                # reset current speed and stop input to cooling
                self.cooling_line.finish_input(ts, {'cooling_id': self.cur_cooling_id, 'bff': self.cur_bff})
                self.cur_speed = None

            while abs(self.plan.at[self.cur_row_id, 'collected'] - self.plan.at[self.cur_row_id, 'kg']) < ERROR:
                if self.cur_row_id == len(self.plan) - 1:
                    # FINISHED
                    return
                # go to next plan row
                self.cur_row_id += 1

            if self.configuration_time:
                self.logger.info(('Configuration time', self.configuration_time))
                EVENT_MANAGER.add_event('update', self.last_ts + self.configuration_time, {})
                # will start producing on next step only
                return

        # set new speed
        if not self.cur_speed:
            self.cur_bff = self.plan.iloc[self.cur_row_id]['bff']
            self.cur_speed = self.plan.iloc[self.cur_row_id]['max_speed']
            self.cur_cooling_id = str(uuid.uuid4())
            self.cooling_line.start_input(ts, {'cooling_id': self.cur_cooling_id, 'bff': self.cur_bff, 'speed': self.cur_speed})

        left_to_produce = self.plan.iloc[self.cur_row_id]['kg'] - self.plan.iloc[self.cur_row_id]['collected']
        left_seconds = left_to_produce / self.cur_speed * 3600

        EVENT_MANAGER.add_event('update', self.last_ts + left_seconds, {})


class CoolingLine:
    def __init__(self):
        self.queue = pd.DataFrame(columns=['bff', 'kg', 'cur_speed'])
        self.last_ts = None
        self.logger = logging.getLogger('CoolingLine')

    def on_start_cooling(self, topic, ts, event):
        self.on_update(topic, ts, event)
        new_row = pd.DataFrame([[event['bff'], 0, event['speed']]], columns=['bff', 'kg', 'cur_speed'], index=[event['cooling_id']])
        self.queue = pd.concat([new_row, self.queue])
        self.logger.info(('Start cooling', ts, event))

    def on_finish_cooling(self, topic, ts, event):
        self.on_update(topic, ts, event)
        self.queue.at[event['cooling_id'], 'cur_speed'] = 0
        self.logger.info(('Finish cooling', ts, event))

    def on_update(self, topic, ts, event):
        if self.last_ts:
            self.queue['kg'] += (ts - self.last_ts) / 3600 * self.queue['cur_speed']
        self.last_ts = ts
        self.logger.info(('Current queue: \n' + str(self.queue)))

    def start_input(self, ts, event):
        # todo: take from bff
        cooling_time = 1800
        EVENT_MANAGER.add_event('cooling.start', ts + cooling_time, event)

    def finish_input(self, ts, event):
        # todo: take from bff
        cooling_time = 1800
        EVENT_MANAGER.add_event('cooling.finish', ts + cooling_time, event)


if __name__ == '__main__':
    plan = pd.DataFrame([[1, 100, 100], [2, 100, 100]], columns=['bff', 'kg', 'max_speed'])
    cooling_line = CoolingLine()
    melting_line = MeltingLine(plan, cooling_line)
    EVENT_MANAGER.subscribe('update', melting_line.update)
    EVENT_MANAGER.subscribe('cooling.start', cooling_line.on_start_cooling)
    EVENT_MANAGER.subscribe('cooling.finish', cooling_line.on_finish_cooling)
    today_ts = int(custom_round(cast_ts(datetime.now()), 24 * 3600))
    EVENT_MANAGER.add_event('update', today_ts, {})
    EVENT_MANAGER.run()
    print(cooling_line.queue)
    print(melting_line.plan)