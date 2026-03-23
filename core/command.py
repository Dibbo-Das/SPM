from django.core.management.base import BaseCommand as DjangoBaseCommand
from core.models import ProcessStatus

class BaseCommand(DjangoBaseCommand):
    processMonitorName = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--monitoring-interval',
            type=int,
            required=False,
            help='Process monitoring interval'
        )

    def warning(self, msg):
        if self.processMonitorName is not None:
            self.getProcessMonitor().warning(msg)
        self.stderr.write(self.style.WARNING(msg))

    def error(self, msg):
        if self.processMonitorName is not None:
            self.getProcessMonitor().error(msg)
        self.stderr.write(self.style.ERROR(msg))

    def execute(self, *args, **options):
        try:
            super().execute(self, *args, **options)
        except Exception as e:
            self.error(f'{type(e).__name__}: {e}')
            raise e

    def getProcessMonitor(self):
        return ProcessStatus.objects.get_or_create(name=self.processMonitorName)[0]

    def processMonitorStart(self, name, options):
        interval = options.get('monitoring_interval')
        self.processMonitorName = name
        processMonitor = self.getProcessMonitor()
        processMonitor.interval = interval if interval is not None else 0
        processMonitor.start()

    def processMonitorFinish(self):
        self.getProcessMonitor().finish()
