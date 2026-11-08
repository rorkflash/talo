"""Typed errors. Each maps to a stable `code` that callers can branch on."""

from talo.core.envelope import ErrorResponse


class TaloError(Exception):
    code = "internal"
    retryable = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(code=self.code, message=self.message, retryable=self.retryable)


class InvalidInputError(TaloError):
    code = "invalid_input"


class OutsideWorkspaceError(TaloError):
    code = "outside_workspace"


class UnknownModuleError(TaloError):
    code = "unknown_module"


class UnknownReferenceError(TaloError):
    """The reference is malformed, expired, or belongs to another workspace."""

    code = "unknown_reference"


class BusyError(TaloError):
    code = "busy"
    retryable = True


class BackendUnavailableError(TaloError):
    code = "backend_unavailable"


class RemoteNotAllowedError(TaloError):
    code = "remote_not_allowed"


class NotCalibratedError(TaloError):
    code = "not_calibrated"


class NotImplementedYetError(TaloError):
    code = "not_implemented"
