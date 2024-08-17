import inspect


def render_join() -> str:
    return inspect.cleandoc(
        """
        What's up Bitcoin holders, condolences to the rest 👋
        Try @coinseekbot inline to start searching for your precious coins.
        Don't forget to save your favourites.

        Later on, you can check them out with /watch to get notified!
        """
    )
