from utils_ak.interactive_imports import *

EVENT_MANAGER = SimpleEventManager()


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
    configure_logging(stream_level=logging.INFO)
    today_ts = int(custom_round(cast_ts(datetime.now()), 24 * 3600))
    cooling_line = CoolingLine()
    cooling_line.on_start_cooling('sample', today_ts, {'bff': 1, 'cooling_id': 'cid_1', 'speed': 100})
    cooling_line.on_start_cooling('sample', today_ts + 1800, {'bff': 1, 'cooling_id': 'cid_2', 'speed': 200})
    cooling_line.on_finish_cooling('sample', today_ts + 3600, {'bff': 1, 'cooling_id': 'cid_1', 'speed': 100})
    cooling_line.on_finish_cooling('sample', today_ts + 5400, {'bff': 1, 'cooling_id': 'cid_2', 'speed': 200})
    print(cooling_line.queue)

    today_ts = int(custom_round(cast_ts(datetime.now()), 24 * 3600))
    cooling_line = CoolingLine()
    EVENT_MANAGER.subscribe('cooling.start', cooling_line.on_start_cooling)
    EVENT_MANAGER.subscribe('cooling.finish', cooling_line.on_finish_cooling)
    cooling_line.start_input(today_ts, {'bff': 1, 'cooling_id': 'cid_1', 'speed': 100})
    cooling_line.start_input(today_ts + 1800, {'bff': 1, 'cooling_id': 'cid_2', 'speed': 200})
    cooling_line.finish_input(today_ts + 3600, {'bff': 1, 'cooling_id': 'cid_1', 'speed': 100})
    cooling_line.finish_input(today_ts + 5400, {'bff': 1, 'cooling_id': 'cid_2', 'speed': 200})
    EVENT_MANAGER.run()
    print(cooling_line.queue)