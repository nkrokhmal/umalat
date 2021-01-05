from utils_ak.interactive_imports import *

ERROR = 1e-5

EVENT_MANAGER = SimpleEventManager()


class MeltingLine:
    def __init__(self, plan, configuration_time=300):
        self.plan = plan
        self.plan['collected'] = 0

        self.queue = pd.DataFrame(columns=['bff', 'kg'])

        self.cur_row_id = 0
        self.cur_bff = None
        self.cur_speed = None
        self.last_ts = None

        self.logger = logging.getLogger('MeltingLine')
        self.configuration_time = 300

    def update(self, topic, ts, event):
        self.logger.info(('Melting line update', ts))

        if self.cur_speed:
            produced = (ts - self.last_ts) * self.cur_speed / 3600

            self.logger.info(('Produced', produced, self.cur_bff))

            if len(self.queue) == 0 or self.queue.iloc[0]['bff'] != self.cur_bff:
                # create new queue
                new_row = pd.DataFrame([[self.cur_bff, 0]], columns=['bff', 'kg'])
                self.queue = pd.concat([new_row, self.queue])

            self.queue.at[self.queue.index[0], 'kg'] += produced
            self.plan.at[self.cur_row_id, 'collected'] += produced

            self.cur_speed = None

        self.logger.info('Current queue \n' + str(self.queue))
        self.logger.info('Current plan \n' + str(self.plan))

        self.last_ts = ts

        if len(self.plan) == 0:
            return

        # set new plan row
        if abs(self.plan.at[self.cur_row_id, 'collected'] - self.plan.at[self.cur_row_id, 'kg']) < ERROR:
            if self.cur_row_id == len(self.plan) - 1:
                return
            else:
                self.cur_row_id += 1

            if self.configuration_time:
                self.logger.info(('Configuration time', self.configuration_time))
                EVENT_MANAGER.add_event('update', self.last_ts + self.configuration_time, {})
                return

        self.cur_bff = self.plan.iloc[self.cur_row_id]['bff']
        self.cur_speed = self.plan.iloc[self.cur_row_id]['max_speed']

        left_to_produce = self.plan.iloc[self.cur_row_id]['kg'] - self.plan.iloc[self.cur_row_id]['collected']
        left_seconds = left_to_produce / self.cur_speed * 3600

        EVENT_MANAGER.add_event('update', self.last_ts + left_seconds, {})


if __name__ == '__main__':
    configure_logging(stream_level=logging.INFO)
    plan = pd.DataFrame([[1, 100, 100], [2, 100, 100]], columns=['bff', 'kg', 'max_speed'])
    melting_line = MeltingLine(plan)
    EVENT_MANAGER.subscribe('update', melting_line.update)
    today_ts = int(custom_round(cast_ts(datetime.now()), 24 * 3600))
    EVENT_MANAGER.add_event('update', today_ts, {})
    EVENT_MANAGER.run()