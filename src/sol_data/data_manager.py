from __future__ import annotations

from typing import Iterable, Optional, Dict, Any, Union, List
import requests

from src.sol_data.data_models import (
    MultiPriceResponse,
    TokenOverviewResponse,
    TokenSecurityResponse,
    TokenCreationInfoResponse,
    TokenHoldersResponse,
    MintBurnTxsResponse,
    WalletPortfolioResponse,
)


class DataManagerAPIError(RuntimeError):
    pass


class DataManager:
    def __init__(
        self,
        api_key: str,
        chain: str = "solana",
        base_url: str = "https://public-api.birdeye.so",
    ) -> None:
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Birdeye API key is required.")

        self.base_url = base_url.rstrip("/")
        self.chain = chain

        # Session with sane retries
        self.sess = requests.Session()

    # -----------------------------
    # internal helpers
    # -----------------------------
    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h = {
            "accept": "application/json",
            "X-API-KEY": self.api_key,
            "x-chain": self.chain,
        }
        if extra:
            h.update(extra)
        return h

    def make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.sess.request(
            method,
            url,
            headers=self._headers(extra_headers),
            params=params,
            json=json,
        )
        if r.status_code != 200:
            raise DataManagerAPIError(f"{r.status_code} {r.reason}: {r.text}")

        data = r.json()
        # DataManager JSON envelope: usually {"success": true, "data": {...}}
        if isinstance(data, dict) and data.get("success") is False:
            raise DataManagerAPIError(f"Error fetching data from Birdeye: {data.get('message')}")
            
        return data.get("data")

    def to_csv(self, addresses: Iterable[str]) -> str:
        return ",".join(a.strip() for a in addresses if a and a.strip())

    def get_multi_price(
        self,
        addresses: List[str],
        ui_amount_mode: str = "raw",
        include_liquidity: Optional[bool] = None,
        check_liquidity: Optional[Union[int, float]] = None,
    ) -> MultiPriceResponse:
        """GET /defi/multi_price (comma-separated list_address)"""
        params: Dict[str, Any] = {
            "list_address": self.to_csv(addresses),
            "ui_amount_mode": ui_amount_mode,
        }
        if include_liquidity is not None:
            params["include_liquidity"] = str(include_liquidity).lower()
        if check_liquidity is not None:
            params["check_liquidity"] = check_liquidity

        data = self.make_request("GET", "/defi/multi_price", params=params)

        return MultiPriceResponse(**data)

    def get_token_overview(self, address: str, frames: Optional[Iterable[str]] = None) -> TokenOverviewResponse:
        """GET /defi/token_overview"""
        params: Dict[str, Any] = {"address": address}
        if frames:
            params["frames"] = self.to_csv(frames)
        data = self.make_request("GET", "/defi/token_overview", params=params)

        return TokenOverviewResponse(**data)

    # -----------------------------
    # Token metadata & security
    # -----------------------------

    def get_token_security(self, address: str) -> TokenSecurityResponse:
        """GET /defi/token_security"""
        data = self.make_request("GET", "/defi/token_security", params={"address": address})
        return TokenSecurityResponse(**data)

    def get_token_creation_info(self, address: str) -> TokenCreationInfoResponse:
        """GET /defi/token_creation_info"""
        data = self.make_request("GET", "/defi/token_creation_info", params={"address": address})
        return TokenCreationInfoResponse(**data)

    # -----------------------------
    # Holders & supply signals
    # -----------------------------
    def get_token_holders(
        self,
        address: str,
        offset: int = 0,
        limit: int = 10,
        ui_amount_mode: str = "scaled",
    ) -> TokenHoldersResponse:
        """GET /defi/v3/token/holder"""
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
        return TokenHoldersResponse(**data)

    def get_mint_burn_txs(self, address: str, offset: int = 0, limit: int = 100) -> MintBurnTxsResponse:
        """GET /defi/v3/token/mint-burn-txs (Solana only)"""
        data = self.make_request(
            "GET",
            "/defi/v3/token/mint-burn-txs",
            params={"address": address, "offset": offset, "limit": limit},
        )
        return MintBurnTxsResponse(**data)

    def get_wallet_portfolio(self, wallet_address: str) -> WalletPortfolioResponse:
        """GET /v1/wallet/token_list
        Get all tokens on solana in a wallet"""
        data = self.make_request("GET", "/v1/wallet/token_list", params={"wallet": wallet_address})
        return WalletPortfolioResponse(**data)
