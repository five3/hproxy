from .plugins import before_proxy, after_proxy


@before_proxy
def before(context):
    print(context)


@after_proxy
def after(context):
    print(context)
