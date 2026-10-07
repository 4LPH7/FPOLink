import runpy


def test_worker_module_bootstraps_as_main(monkeypatch):
    class DummyScheduler:
        def __init__(self, *args, **kwargs):
            self._jobs = []

        def add_job(self, *args, **kwargs):
            self._jobs.append((args, kwargs))

        def get_jobs(self):
            return []

        def start(self):
            return None

    monkeypatch.setattr("apscheduler.schedulers.blocking.BlockingScheduler", DummyScheduler)
    runpy.run_module("app.worker", run_name="__main__")
