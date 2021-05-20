import schedule
import time

def job(message='stuff'):
    print("I'm working on:", message)

schedule.every(10).seconds.do(job).tag('hello')
schedule.every(5).to(10).days.do(job)
schedule.every().hour.do(job, message='things')
schedule.every().day.at("10:30").do(job)

while True:
        schedule.run_pending()
        time.sleep(1)
        print(str(schedule.next_run('hello')))

