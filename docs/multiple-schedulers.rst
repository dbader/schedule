Multiple schedulers
###################

You can run as many jobs from a single scheduler as you wish.
However, for larger installations it might be desirable to have multiple schedulers.
This is supported:

.. code-block:: python

    import time
    import schedule

    def fooJob():
        print("Foo")

    def barJob():
        print("Bar")

    # Create a new scheduler
    scheduler1 = schedule.Scheduler()

    # Add jobs to the created scheduler
    scheduler1.every().hour.do(fooJob)
    scheduler1.every().hour.do(barJob)

    # Create as many schedulers as you need
    scheduler2 = schedule.Scheduler()
    scheduler2.every().second.do(fooJob)
    scheduler2.every().second.do(barJob)

    while True:
        # run_pending needs to be called on every scheduler
        scheduler1.run_pending()
        scheduler2.run_pending()
        time.sleep(1)
