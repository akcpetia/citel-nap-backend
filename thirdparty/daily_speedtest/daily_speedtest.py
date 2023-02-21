# daily_speedtest - run an ookla speedtest daily at configured hour and put results to description

import time
import datetime
from csclient import EventingCSClient
from speedtest import Speedtest

# Hour of day to run speedtest. 5:00pm = 17
testing_hour = 11

def run_speedtest():
    cp.log(f'Daily speedtest scheduled for {testing_hour}:00 -- Running now...')
    speedtest.get_best_server()
    speedtest.download()
    speedtest.upload(pre_allocate=False)
    down = '{:.2f}'.format(speedtest.results.download / 1000 / 1000)
    up = '{:.2f}'.format(speedtest.results.upload / 1000 / 1000)
    latency = int(speedtest.results.ping)
    results_text = f'{down}Mbps Down / {up}Mbps Up / {latency}ms latency'
    cp.log(results_text)
    cp.alert(results_text)
    # cp.put('config/system/desc', results_text)


cp = EventingCSClient('daily_speedtest')
cp.log('Starting...')

# Wait for NCM connection
while not cp.get('status/ecm/state') == 'connected':
    time.sleep(2)

speedtest = Speedtest()

# Loop to check data and time to run speedtest
last_test_date = None
while True:
    try:
        testing_hour = int(cp.get('config/hotspot/tos/text'))
    except:
        pass
    current_date = datetime.date.today()
    if current_date != last_test_date:
        current_hour = datetime.datetime.now().hour
        # DEBUG:
        # cp.log(f'{last_test_date=} {current_date.isoformat()=} {current_hour=} {testing_hour=}')
        if current_hour >= testing_hour:
            run_speedtest()
            last_test_date = current_date
    time.sleep(60)
