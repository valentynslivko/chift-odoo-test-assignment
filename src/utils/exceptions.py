class RedisConnectionError(Exception):
    pass


class OdooError(Exception):
    """Base exception for Odoo related errors"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class OdooProtocolError(OdooError):
    """Exception raised for HTTP protocol errors (e.g. 400 Bad Request)"""
    pass


class OdooFaultError(OdooError):
    """Exception raised for Odoo-level faults (e.g. Access Denied, Invalid Domain)"""
    pass
