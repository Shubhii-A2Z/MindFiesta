from src.configs.settings import get_settings
from src.controllers.strategies.ingestion_strategy import IngestionStrategy

class IngestionStrategyFactory:

    @staticmethod
    def get_ingestion_strategy()->IngestionStrategy:
        settings=get_settings()

        if settings.ingestion_strategy.lower()=='temporal':
            from src.controllers.strategies.temporal_ingestion_strategy import (
                TemporalIngestionStrategy
            )
            return TemporalIngestionStrategy()
        elif settings.ingestion_strategy.lower()=='synchronous':
            from src.controllers.strategies.synchronous_ingestion_strategy import(
                SynchronousIngestionStrategy
            )
            return SynchronousIngestionStrategy()
        else:
            raise ValueError(f"Invalid ingestion strategy: {settings.ingestion_strategy}")