class AdminCli:
    def __init__(self, **kwargs):
        self.__service = kwargs["service"]
        self.__method = kwargs["method"]