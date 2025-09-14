from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import os
import requests

from src.sol_data.data_models import (
    TokenOverviewResponse,
    TokenSecurityResponse,
    TokenCreationInfoResponse,
    TokenHoldersResponse,
    WalletPortfolioResponse,
)

load_dotenv()


class DataManagerAPIError(RuntimeError):
    pass


class DataManager:
    def __init__(self, chain: str = "solana", base_url: str = "https://public-api.birdeye.so") -> None:
        self.sess = requests.Session()
        self.base_url = base_url
        self.headers = {"accept": "application/json", "X-API-KEY": os.getenv("BIRDEYE_API_KEY"), "x-chain": chain}

    def make_request(self, method: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        r = self.sess.request(method=method, url=url, params=params, headers=self.headers)

        if r.status_code != 200:
            raise DataManagerAPIError(f"{r.status_code} {r.reason}: {r.text}")

        data = r.json()

        if not data.get("success"):
            raise DataManagerAPIError(f"Error fetching data from Birdeye: {data.get('message')}")

        return data.get("data")

    def get_token_overview(self, token_address: str, frames: Optional[List[str]] = None) -> TokenOverviewResponse:
        params = {"address": token_address}

        if frames:
            params["frames"] = frames

        data = self.make_request("GET", "/defi/token_overview", params=params)

        if not data:
            return TokenOverviewResponse()

        return TokenOverviewResponse(**data)

    def get_wallet_portfolio(self, wallet_address: str) -> WalletPortfolioResponse:
        data = self.make_request("GET", "/v1/wallet/token_list", params={"wallet": wallet_address})

        if not data:
            return WalletPortfolioResponse()

        return WalletPortfolioResponse(**data)

    def get_token_security(self, address: str) -> TokenSecurityResponse:
        """GET /defi/token_security"""
        data = self.make_request("GET", "/defi/token_security", params={"address": address})
        if not data:
            return TokenSecurityResponse()
        return TokenSecurityResponse(**data)

    def get_token_creation_info(self, address: str) -> TokenCreationInfoResponse:
        data = self.make_request("GET", "/defi/token_creation_info", params={"address": address})
        if not data:
            return TokenCreationInfoResponse()
        return TokenCreationInfoResponse(**data)

    def get_token_holders(
        self,
        address: str,
        offset: int = 0,
        limit: int = 10,
        ui_amount_mode: str = "scaled",
    ) -> TokenHoldersResponse:
        data = self.make_request(
            "GET",
            "/defi/v3/token/holder",
            params={
                "address": address,
                "offset": offset,
                "limit": min(limit, 1000),
                "ui_amount_mode": ui_amount_mode,
            },
        )
        if not data:
            return TokenHoldersResponse()

        return TokenHoldersResponse(**data)