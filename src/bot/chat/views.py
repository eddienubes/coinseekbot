import inspect


def render_join() -> str:
    return inspect.cleandoc(
        """
        What's up Bitcoin holders, condolences to the rest 👋
        Try @coinseekbot inline to start searching for your precious coins.

        Use /help to get some <s>mental</s> help.
        """
    )
