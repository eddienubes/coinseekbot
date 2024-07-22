import dataclasses
from collections.abc import Callable

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler.abc import Trigger


@dataclasses.dataclass
class CronJob:
    fn: Callable
    trigger: Trigger


class CronService:
    def __init__(self):
        self.__jobs = list[CronJob]()
        self.__scheduler: AsyncScheduler | None = None

    def add_job(self, fn: Callable, trigger: Trigger) -> None:
        self.__jobs.append(CronJob(fn=fn, trigger=trigger))

    async def on_module_init(self):
        # TODO: Perhaps, we could turn the entire container into its own context manager.
        # And then replace on_module_init and on_module_destroy with __aenter__ and __aexit__.
        # I guess, it'd be a more pythonic way of handling lifecycle of objects.
        # Otherwise, the scheduler's exit doesn't do anything besides stopping recurring tasks.
        self.__scheduler = await AsyncScheduler().__aenter__()
        for job in self.__jobs:
            await self.__scheduler.add_schedule(
                job.fn,
                trigger=job.trigger,
                conflict_policy=ConflictPolicy.do_nothing,
                max_running_jobs=1
            )

        await self.__scheduler.start_in_background()

    async def on_module_destroy(self):
        await self.__scheduler.stop()
