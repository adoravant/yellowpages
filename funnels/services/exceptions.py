# services/exceptions.py
class FunnelException(Exception):
    pass

class InvalidAction(FunnelException):
    pass

class NoTemplateFound(FunnelException):
    pass

class StepNotFound(FunnelException):
    pass
