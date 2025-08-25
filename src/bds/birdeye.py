from __future__ import annotations

from typing import Iterable, Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter, Retry


class BirdeyeAPIError(RuntimeError):
    """Raised when Birdeye returns a non-successful response (HTTP or JSON)."""


class BirdeyeHelper:
    """
    Thin client for Birdeye Data Service.

    Notes:
    - Every request sends your API key as `X-API-KEY` and the chain via the required `x-chain` header.
    - `ui_amount_mode` is supported by many endpoints: "raw" or "scaled".
    """

    def __init__(
        self,
        api_key: str,
        chain: str = "solana",
        base_url: str = "https://public-api.birdeye.so",
        timeout: float = 15.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Birdeye API key is required.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.chain = chain

        # Session with sane retries
        self.sess = requests.Session()
        retry = Retry(
            total=retries,
            status=retries,
            connect=retries,
            read=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "POST"}),
            raise_on_status=False,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry))

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

    def _request(
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
            timeout=self.timeout,
        )
        # HTTP errors
        if r.status_code >= 400:
            raise BirdeyeAPIError(f"{r.status_code} {r.reason}: {r.text}")

        data = r.json()
        # Birdeye JSON envelope: usually {"success": true, "data": {...}}
        if isinstance(data, dict) and data.get("success") is False:
            raise BirdeyeAPIError(f"Birdeye error: {data}")
        return data

    @staticmethod
    def _csv(addresses: Iterable[str]) -> str:
        return ",".join(a.strip() for a in addresses if a and a.strip())

    # -----------------------------
    # Prices & market snapshots
    # -----------------------------
    def get_price(self, address: str, ui_amount_mode: str = "raw") -> Dict[str, Any]:
        """GET /defi/price"""
        return self._request(
            "GET",
            "/defi/price",
            params={"address": address, "ui_amount_mode": ui_amount_mode},
        )

    def get_multi_price(
        self,
        addresses: Iterable[str],
        ui_amount_mode: str = "raw",
        include_liquidity: Optional[bool] = None,
        check_liquidity: Optional[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        """GET /defi/multi_price (comma-separated list_address)"""
        params: Dict[str, Any] = {
            "list_address": self._csv(addresses),
            "ui_amount_mode": ui_amount_mode,
        }
        if include_liquidity is not None:
            params["include_liquidity"] = str(include_liquidity).lower()
        if check_liquidity is not None:
            params["check_liquidity"] = check_liquidity
        return self._request("GET", "/defi/multi_price", params=params)

    def get_token_overview(self, address: str, frames: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """GET /defi/token_overview"""
        params: Dict[str, Any] = {"address": address}
        if frames:
            params["frames"] = self._csv(frames)
        return self._request("GET", "/defi/token_overview", params=params)

    def get_market_data(self, address: str, ui_amount_mode: str = "scaled") -> Dict[str, Any]:
        """GET /defi/v3/token/market-data"""
        return self._request(
            "GET",
            "/defi/v3/token/market-data",
            params={"address": address, "ui_amount_mode": ui_amount_mode},
        )

    def get_market_data_multiple(self, addresses: Iterable[str], ui_amount_mode: str = "scaled") -> Dict[str, Any]:
        """GET /defi/v3/token/market-data/multiple"""
        return self._request(
            "GET",
            "/defi/v3/token/market-data/multiple",
            params={"list_address": self._csv(addresses), "ui_amount_mode": ui_amount_mode},
        )

    # -----------------------------
    # Token metadata & security
    # -----------------------------
    def get_token_metadata(self, address: str) -> Dict[str, Any]:
        """GET /defi/v3/token/meta-data/single"""
        return self._request("GET", "/defi/v3/token/meta-data/single", params={"address": address})

    def get_token_security(self, address: str) -> Dict[str, Any]:
        """GET /defi/token_security"""
        return self._request("GET", "/defi/token_security", params={"address": address})

    def get_token_creation_info(self, address: str) -> Dict[str, Any]:
        """GET /defi/token_creation_info"""
        return self._request("GET", "/defi/token_creation_info", params={"address": address})

    def get_exit_liquidity(self, address: str) -> Dict[str, Any]:
        """GET /defi/v3/token/exit-liquidity (chain support varies)
        Only base chain is supported for now"""
        return self._request("GET", "/defi/v3/token/exit-liquidity", params={"address": address}, extra_headers={"x-chain": "base"})

    def get_exit_liquidity_multiple(self, addresses: Iterable[str]) -> Dict[str, Any]:
        """GET /defi/v3/token/exit-liquidity/multiple (chain support varies)
        Only base chain is supported for now"""
        return self._request(
            "GET", "/defi/v3/token/exit-liquidity/multiple", params={"list_address": self._csv(addresses)}, extra_headers={"x-chain": "base"}
        )

    # -----------------------------
    # Holders & supply signals
    # -----------------------------
    def get_token_holders(
        self,
        address: str,
        offset: int = 0,
        limit: int = 10,
        ui_amount_mode: str = "scaled",
    ) -> Dict[str, Any]:
        """GET /defi/v3/token/holder"""
        return self._request(
            "GET",
            "/defi/v3/token/holder",
            params={
                "address": address,
                "offset": offset,
                "limit": min(limit, 1000),
                "ui_amount_mode": ui_amount_mode,
            },
        )

    def get_mint_burn_txs(self, address: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """GET /defi/v3/token/mint-burn-txs (Solana only)"""
        return self._request(
            "GET",
            "/defi/v3/token/mint-burn-txs",
            params={"address": address, "offset": offset, "limit": limit},
        )

    # -----------------------------
    # Pairs / pools
    # -----------------------------
    def get_pair_overview_single(self, pair_address: str, ui_amount_mode: str = "scaled") -> Dict[str, Any]:
        """GET /defi/v3/pair/overview/single (Raydium/other DEX pool address)"""
        return self._request(
            "GET",
            "/defi/v3/pair/overview/single",
            params={"address": pair_address, "ui_amount_mode": ui_amount_mode},
        )

    # -----------------------------
    # Trades (for first-buyer cohorts, etc.)
    # -----------------------------
    def get_trades_token_v3(
        self,
        address: str,
        offset: int = 0,
        limit: int = 100,
        sort_by: str = "block_unix_time",
        sort_type: str = "desc",
        tx_type: Optional[str] = None,  # "swap", "buy", "sell", etc.
        owner: Optional[str] = None,
        pool_id: Optional[str] = None,
        source: Optional[str] = None,  # e.g. "raydium", "pump_dot_fun"
        ui_amount_mode: str = "scaled",
        time_from: Optional[int] = None,  # unix secs
        time_to: Optional[int] = None,  # unix secs
    ) -> Dict[str, Any]:
        """
        GET /defi/v3/token/txs
        Many filters are optional. Use this to reconstruct early buyers, PnL, behavior tags, etc.
        """
        params: Dict[str, Any] = {
            "address": address,
            "offset": offset,
            "limit": limit,
            "sort_by": sort_by,
            "sort_type": sort_type,
            "ui_amount_mode": ui_amount_mode,
        }
        if tx_type:
            params["tx_type"] = tx_type
        if owner:
            params["owner"] = owner
        if pool_id:
            params["pool_id"] = pool_id
        if source:
            params["source"] = source
        if time_from is not None and time_to is not None:
            params["time_range"] = f"{time_from},{time_to}"
        return self._request("GET", "/defi/v3/token/txs", params=params)

    def get_trades_token_seek_by_time(
        self,
        address: str,
        offset: int = 0,
        limit: int = 100,
        tx_type: str = "swap",
        ui_amount_mode: str = "scaled",
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """GET /defi/txs/token/seek_by_time (classic seek-by-time)."""
        params: Dict[str, Any] = {
            "address": address,
            "offset": offset,
            "limit": limit,
            "tx_type": tx_type,
            "ui_amount_mode": ui_amount_mode,
        }
        if before_time is not None:
            params["before_time"] = before_time
        if after_time is not None:
            params["after_time"] = after_time
        return self._request("GET", "/defi/txs/token/seek_by_time", params=params)

    def get_wallet_portfolio(self, wallet_address: str) -> Dict[str, Any]:
        """GET /v1/wallet/token_list
        Get all tokens on solana in a wallet"""
        return self._request("GET", "/v1/wallet/token_list", params={"wallet": wallet_address})
