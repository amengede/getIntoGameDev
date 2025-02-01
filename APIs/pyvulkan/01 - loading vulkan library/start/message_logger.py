class Logger:
    """
        logs various messages.
    """


    def __init__(self):

        self._enabled = True
    
    def set_mode(self, new_mode: bool) -> None:
        """
            Set the logger to either enabled (True) or
            disabled (False)
        """

        self._enabled = new_mode
    
    def is_enabled(self) -> bool:
        """
            Returns the mode of the logger.
        """

        return self._enabled
    
    def log(self, message: str) -> None:
        """
            Send the logger a message to print.
        """

        if not self._enabled:
            return
        
        print(message)

logger = Logger()