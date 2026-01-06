from fastapi import APIRouter, HTTPException

from src.app.application.market.use_cases.get_depth import GetDepthUseCase
from src.app.application.market.use_cases.get_kline import GetKlineUseCase, GetKlineInput
from src.app.application.market.use_cases.get_stats24h import GetStats24HUseCase
from src.app.application.market.use_cases.get_ticker import GetTickerUseCase

router = APIRouter()


@router.get("/depth")
async def get_depth():
    """Get order book depth for QRL/USDT."""
    usecase = GetDepthUseCase()
    return await usecase.execute()


@router.get("/ticker")
async def get_ticker():
    """Get ticker for QRL/USDT."""
    try:
        usecase = GetTickerUseCase()
        result = await usecase.execute()
        
        if result.error:
            raise HTTPException(status_code=502, detail=result.error)
        
        if not result.ticker:
            raise HTTPException(status_code=502, detail="Failed to retrieve ticker data")
        
        return {
            "symbol": result.ticker.symbol.value,
            "lastPrice": str(result.ticker.last_price),
            "bidPrice": str(result.ticker.bid_price),
            "askPrice": str(result.ticker.ask_price),
            "timestamp": result.ticker.ts.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch ticker: {str(e)}")


@router.get("/kline")
async def get_kline(interval: str = "1m", limit: int = 50):
    """Get kline data for QRL/USDT."""
    try:
        usecase = GetKlineUseCase(interval=interval, limit=limit)
        result = await usecase.execute(GetKlineInput(interval=interval, limit=limit))
        
        if result.error:
            raise HTTPException(status_code=502, detail=result.error)
        
        return {
            "symbol": "QRLUSDT",
            "interval": interval,
            "klines": [
                {
                    "openTime": kline.open_time.isoformat(),
                    "open": str(kline.open),
                    "high": str(kline.high),
                    "low": str(kline.low),
                    "close": str(kline.close),
                    "volume": str(kline.volume),
                    "closeTime": kline.close_time.isoformat(),
                    "quoteVolume": str(kline.quote_volume)
                }
                for kline in result.klines
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch kline: {str(e)}")


@router.get("/stats24h")
async def get_stats_24h():
    """Get 24h statistics for QRL/USDT."""
    usecase = GetStats24HUseCase()
    return await usecase.execute()


