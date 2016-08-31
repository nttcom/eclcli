from ..i18n import _


class EccException(Exception):
    """Base Ecc Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        if message:
            self.message = message
        try:
            self._error_string = self.message % kwargs
        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class EccClientException(EccException):
    """Base exception which exceptions from Ecc are mapped into.

    NOTE: on the client side, we use different exception types in order
    to allow client library users to handle server exceptions in try...except
    blocks. The actual error message is the one generated on the server side.
    """

    status_code = 0

    def __init__(self, message=None, **kwargs):
        if 'status_code' in kwargs:
            self.status_code = kwargs['status_code']
        super(EccClientException, self).__init__(message, **kwargs)


# Base exceptions from Ecc

class BadRequest(EccClientException):
    status_code = 400


class Unauthorized(EccClientException):
    status_code = 401
    message = _("Unauthorized: bad credentials.")


class Forbidden(EccClientException):
    status_code = 403
    message = _("Forbidden: your credentials don't give you access to this "
                "resource.")


class NotFound(EccClientException):
    status_code = 404


class Conflict(EccClientException):
    status_code = 409


class InternalServerError(EccClientException):
    status_code = 500


class ServiceUnavailable(EccClientException):
    status_code = 503


HTTP_EXCEPTION_MAP = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    409: Conflict,
    500: InternalServerError,
    503: ServiceUnavailable,
}


# Exceptions mapped to Ecc server exceptions
# These are defined if a user of client library needs specific exception.
# Exception name should be <Ecc Exception Name> + 'Client'
# e.g., NetworkNotFound -> NetworkNotFoundClient

class NetworkNotFoundClient(NotFound):
    pass


class PortNotFoundClient(NotFound):
    pass


class StateInvalidClient(BadRequest):
    pass


class NetworkInUseClient(Conflict):
    pass


class PortInUseClient(Conflict):
    pass


class IpAddressInUseClient(Conflict):
    pass


class InvalidIpForNetworkClient(BadRequest):
    pass


class OverQuotaClient(Conflict):
    pass


# TODO(amotoki): It is unused in Ecc, but it is referred to
# in Horizon code. After Horizon code is updated, remove it.
class AlreadyAttachedClient(Conflict):
    pass


class IpAddressGenerationFailureClient(Conflict):
    pass


class MacAddressInUseClient(Conflict):
    pass


class ExternalIpAddressExhaustedClient(BadRequest):
    pass


# Exceptions from client library

class NoAuthURLProvided(Unauthorized):
    message = _("auth_url was not provided to the Ecc client")


class EndpointNotFound(EccClientException):
    message = _("Could not find Service or Region in Service Catalog.")


class EndpointTypeNotFound(EccClientException):
    message = _("Could not find endpoint type %(type_)s in Service Catalog.")


class AmbiguousEndpoints(EccClientException):
    message = _("Found more than one matching endpoint in Service Catalog: "
                "%(matching_endpoints)")


class RequestURITooLong(EccClientException):
    """Raised when a request fails with HTTP error 414."""

    def __init__(self, **kwargs):
        self.excess = kwargs.get('excess', 0)
        super(RequestURITooLong, self).__init__(**kwargs)


class ConnectionFailed(EccClientException):
    message = _("Connection to ecc failed: %(reason)s")


class SslCertificateValidationError(EccClientException):
    message = _("SSL certificate validation has failed: %(reason)s")


class MalformedResponseBody(EccClientException):
    message = _("Malformed response body: %(reason)s")


class InvalidContentType(EccClientException):
    message = _("Invalid content type %(content_type)s.")


# Command line exceptions

class EccCLIError(EccException):
    """Exception raised when command line parsing fails."""
    pass


class CommandError(EccCLIError):
    pass


class UnsupportedVersion(EccCLIError):
    """Indicates that the user is trying to use an unsupported version of
    the API.
    """
    pass


class EccClientNoUniqueMatch(EccCLIError):
    message = _("Multiple %(resource)s matches found for name '%(name)s',"
                " use an ID to be more specific.")
