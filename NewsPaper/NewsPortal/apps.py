from django.apps import AppConfig


class NewsportalConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'NewsPortal'

    def ready(self):
        import NewsPortal.signals

        from .tasks import send
        from .scheduler import  post_scheduler

        post_scheduler.add_job(
            id='send',
            func=send,
            trigger='interval',
            seconds=10
        )

        #post_scheduler.start()
