class KafkaConfigError(Exception):
    """Custom exception for Kafka client configuration errors"""
    def __init__(self, message):
        super().__init__(message)
