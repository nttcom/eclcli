from ..i18n import _


class ESIException(Exception):
    message = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        if message:
            self.message = message
        try:
            self._error_string = self.message % kwargs
        except Exception:
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class ESIClientException(ESIException):
    status_code = 0

    def __init__(self, message=None, **kwargs):
        if 'status_code' in kwargs:
            self.status_code = kwargs['status_code']
        super(ESIClientException, self).__init__(message, **kwargs)


class BadRequest(ESIClientException):
    status_code = 400
    message = _("Bad Request")


class Unauthorized(ESIClientException):
    status_code = 401
    message = _("Unauthorized: bad credentials.")


class Forbidden(ESIClientException):
    status_code = 403
    message = _("Forbidden: your credentials don't give you access to this "
                "resource.")


class NotFound(ESIClientException):
    status_code = 404
    message = _("Not Found")


class Conflict(ESIClientException):
    status_code = 409
    message = _("Conflict")


class InternalServerError(ESIClientException):
    status_code = 500
    message = _("Internal Server Error")


class ServiceUnavailable(ESIClientException):
    status_code = 503
    message = _("Service Unavailable")


HTTP_EXCEPTION_MAP = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    409: Conflict,
    500: InternalServerError,
    503: ServiceUnavailable,
}


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


class AlreadyAttachedClient(Conflict):
    pass


class IpAddressGenerationFailureClient(Conflict):
    pass


class MacAddressInUseClient(Conflict):
    pass


class ExternalIpAddressExhaustedClient(BadRequest):
    pass


class NoAuthURLProvided(Unauthorized):
    message = _("auth_url was not provided to the ESI client")


class EndpointNotFound(ESIClientException):
    message = _("Could not find Service or Region in Service Catalog.")


class EndpointTypeNotFound(ESIClientException):
    message = _("Could not find endpoint type %(type_)s in Service Catalog.")


class AmbiguousEndpoints(ESIClientException):
    message = _("Found more than one matching endpoint in Service Catalog: "
                "%(matching_endpoints)")


class RequestURITooLong(ESIClientException):
    def __init__(self, **kwargs):
        self.excess = kwargs.get('excess', 0)
        super(RequestURITooLong, self).__init__(**kwargs)


class ConnectionFailed(ESIClientException):
    message = _("Connection to esi failed: %(reason)s")


class SslCertificateValidationError(ESIClientException):
    message = _("SSL certificate validation has failed: %(reason)s")


class MalformedResponseBody(ESIClientException):
    message = _("Malformed response body: %(reason)s")


class InvalidContentType(ESIClientException):
    message = _("Invalid content type %(content_type)s.")


class ESICLIError(ESIException):
    pass


class CommandError(ESICLIError):
    pass


class UnsupportedVersion(ESICLIError):
    pass


class ESIClientNoUniqueMatch(ESICLIError):
    message = _("Multiple %(resource)s matches found for name '%(name)s',"
                " use an ID to be more specific.")
