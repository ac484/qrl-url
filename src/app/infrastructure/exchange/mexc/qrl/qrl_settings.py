from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class QrlSettings(MexcSettings):
    """Alias for QRL-only flows; reuses general MEXC credentials."""

    @property
    def symbol(self) -> str:
        return "QRLUSDT"
