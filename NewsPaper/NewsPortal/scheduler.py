from apscheduler.schedulers.background import  BackgroundScheduler

post_scheduler = BackgroundScheduler()
# post_scheduler.add_job(
#     id = 'send',
#     func=lambda: print('BBBBB!'),
#     trigger='interval',
#     seconds=5
# )