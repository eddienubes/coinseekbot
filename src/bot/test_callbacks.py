from .callbacks import RedisCb


class TestCallbacks:
    async def test_storage(self):
        class SomeCb(RedisCb, prefix='SomeCb'):
            some_int: int
            some_str: str

        cb = SomeCb(some_int=1, some_str='test')
        cb_data = await cb.save()

        assert cb_data == f'SomeCb::{cb.id}'

        cb_data = cb.pack()

        assert cb_data == f'SomeCb::{cb.id}'

        unpacked_id = SomeCb.unpack(cb_data)

        assert unpacked_id.id == cb.id
        assert unpacked_id.some_int is None
        assert unpacked_id.some_str is None

        await cb.load()

        assert cb.some_int == 1
        assert cb.some_str == 'test'
