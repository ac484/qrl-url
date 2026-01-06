from fastapi import APIRouter, HTTPException

from src.app.application.account.use_cases.get_balance import GetBalanceUseCase

router = APIRouter()


@router.get("/balance")
async def get_balance():
    """Get subaccount balance for QRL/USDT."""
    try:
        usecase = GetBalanceUseCase()
        result = await usecase.execute()
        
        if result.error:
            raise HTTPException(status_code=502, detail=result.error)
        
        return {
            "balances": [
                {
                    "asset": balance.asset,
                    "free": str(balance.free),
                    "locked": str(balance.locked),
                    "total": str(balance.total)
                }
                for balance in result.balances
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch balance: {str(e)}")


