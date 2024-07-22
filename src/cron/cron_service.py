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
        self.__scheduler = await AsyncScheduler().__aenter__()
        for job in self.__jobs:
            await self.__scheduler.add_schedule(job.fn, trigger=job.trigger, conflict_policy=ConflictPolicy.do_nothing)

        await self.__scheduler.start_in_background()

    async def on_module_destroy(self):
        await self.__scheduler.__aexit__(None, None, None)
