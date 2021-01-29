from enum import Enum, auto


class AppSummaryAttribute(Enum):
    app_name = auto()
    error_message = auto()
    risk = auto()
    abnormal_attributes = auto()
    latest_retrieved_app_details = auto()
    modelled_app_details = auto()
