from django.db import models
from datetime import datetime, timezone

class ProcessStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_at = models.DateTimeField(null=True, blank=True)
    error_msg = models.CharField(max_length=1000, null=True, blank=True)
    warning_at = models.DateTimeField(null=True, blank=True)
    warning_msg = models.CharField(max_length=1000, null=True, blank=True)
    interval = models.IntegerField(default=0)

    def startByName(name, interval=None):
        processStatus = ProcessStatus.objects.get_or_create(name=name)[0]
        processStatus.interval = interval if interval is not None else 0
        return processStatus.start()

    def start(self):
        self.started_at = datetime.now(timezone.utc)
        self.save()
        return self

    def finish(self):
        self.finished_at = datetime.now(timezone.utc)
        self.save()
        return self

    def error(self, message):
        self.error_at = datetime.now(timezone.utc)
        self.error_msg = message
        self.save()
        return self

    def warning(self, message):
        self.warning_at = datetime.now(timezone.utc)
        self.warning_msg = message
        self.save()
        return self

    @property
    def is_started_at_due(self):
        return self._is_datetime_due(self.started_at) and self.is_finished_at_due()

    @property
    def is_finished_at_due(self):
        return self._is_datetime_due(self.finished_at)

    def _is_datetime_due(self, dt):
        if not self.interval:
            return None
        return (datetime.now(timezone.utc) - dt).total_seconds() > self.interval
