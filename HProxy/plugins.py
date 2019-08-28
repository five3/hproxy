
class Plugins:
    def fire(self, context):
        for func in self.events:
            func(context)

    def register(self, func):
        self.events.append(func)


class PRE_PROXY(Plugins):
    def __init__(self):
        self.events = []


class POST_PROXY(Plugins):
    def __init__(self):
        self.events = []


pre_proxy = PRE_PROXY()
post_proxy = POST_PROXY()


def before_proxy(func):
    pre_proxy.register(func)
    return func


def after_proxy(func):
    post_proxy.register(func)
    return func
