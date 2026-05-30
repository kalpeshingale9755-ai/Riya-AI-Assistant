# riya_engine/capabilities/base_response.py

class CapabilityResponse:

    def __init__(
        self,
        success,
        data=None,
        error=None
    ):

        self.success = success

        self.data = data or {}

        self.error = error

    def to_dict(self):

        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }