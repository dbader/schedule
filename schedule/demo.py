from schedule.async_schedule import Scheduler


def job(message='stuff'):
    print('message is:', message)


def run_main_thread():
    scheduler = Scheduler()
    scheduler.every(10).seconds.do(job)
    scheduler.every(5).to(10).days.do(job)
    scheduler.every().hour.do(job, message='things')
    scheduler.every().day.at("10:30").do(job)
    scheduler.run_pending()


def run_new_thread():
    scheduler = Scheduler()

    cancel_job = scheduler.every(10).seconds.do(job)
    scheduler.every(5).to(10).days.do(job)
    scheduler.every().hour.do(job, message='things')
    scheduler.every().day.at("10:30").do(job)

    bkg_handler = scheduler.run_new_thread_pending()

    import time
    time.sleep(15)
    scheduler.cancel_job(cancel_job)
    time.sleep(15)
    bkg_handler.cancel()
