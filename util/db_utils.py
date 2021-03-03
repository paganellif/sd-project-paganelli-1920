from enum import Enum, unique


@unique
class Parameters(Enum):
    temperature = "temp"
    humidity = "hum"
    wind = "wind"


@unique
class TriggerEvents(Enum):
    event = "flame"


@unique
class Collections(Enum):
    sensors_detections = "sensorvalues"
    event_detections = "flame_detection"
    triggered_actions = "alarm_activation"
    failure_reports = "error_report"
    detection_statistics = "agent_stats"


@unique
class Databases(Enum):
    test_db = "testdb"
