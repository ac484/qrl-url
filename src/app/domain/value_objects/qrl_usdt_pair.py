class QrlUsdtPair:
    """QRL/USDT 專用交易對，不允許動態建構."""

    SYMBOL = "QRLUSDT"
    BASE = "QRL"
    QUOTE = "USDT"

    @classmethod
    def symbol(cls) -> str:
        return cls.SYMBOL

    @classmethod
    def base(cls) -> str:
        return cls.BASE

    @classmethod
    def quote(cls) -> str:
        return cls.QUOTE
