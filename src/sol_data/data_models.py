from pydantic import BaseModel, RootModel
from typing import Optional, List, Dict


# https://docs.birdeye.so/reference/get-defi-multi_price
class Price(BaseModel):
    value: float
    updateUnixTime: int
    updateHumanTime: str
    priceChange24h: float
    priceInNative: Optional[float] = None
    liquidity: Optional[float] = None
    isScaledUiToken: Optional[bool] = None
    scaledValue: Optional[float] = None
    multiplier: Optional[float] = None
    scaledPriceInNative: Optional[float] = None


class MultiPriceResponse(RootModel[Dict[str, Price]]):
    root: Dict[str, Price]


# https://docs.birdeye.so/reference/get-defi-token_overview
class TokenExtensions(BaseModel):
    coingeckoId: Optional[str] = None
    serumV3Usdc: Optional[str] = None
    serumV3Usdt: Optional[str] = None
    website: Optional[str] = None
    telegram: Optional[str] = None
    twitter: Optional[str] = None
    description: Optional[str] = None
    discord: Optional[str] = None
    medium: Optional[str] = None


class TokenOverviewResponse(BaseModel):
    address: Optional[str] = None
    decimals: Optional[int] = None
    symbol: Optional[str] = None
    name: Optional[str] = None
    marketCap: Optional[float] = None
    fdv: Optional[float] = None
    extensions: Optional[TokenExtensions] = None
    logoURI: Optional[str] = None
    liquidity: Optional[float] = None
    lastTradeUnixTime: Optional[int] = None
    lastTradeHumanTime: Optional[str] = None
    price: Optional[float] = None
    history1mPrice: Optional[float] = None
    priceChange1mPercent: Optional[float] = None
    history5mPrice: Optional[float] = None
    priceChange5mPercent: Optional[float] = None
    history30mPrice: Optional[float] = None
    priceChange30mPercent: Optional[float] = None
    history1hPrice: Optional[float] = None
    priceChange1hPercent: Optional[float] = None
    history2hPrice: Optional[float] = None
    priceChange2hPercent: Optional[float] = None
    history4hPrice: Optional[float] = None
    priceChange4hPercent: Optional[float] = None
    history6hPrice: Optional[float] = None
    priceChange6hPercent: Optional[float] = None
    history8hPrice: Optional[float] = None
    priceChange8hPercent: Optional[float] = None
    history12hPrice: Optional[float] = None
    priceChange12hPercent: Optional[float] = None
    history24hPrice: Optional[float] = None
    priceChange24hPercent: Optional[float] = None
    uniqueWallet1m: Optional[int] = None
    uniqueWalletHistory1m: Optional[int] = None
    uniqueWallet1mChangePercent: Optional[float] = None
    uniqueWallet5m: Optional[int] = None
    uniqueWalletHistory5m: Optional[int] = None
    uniqueWallet5mChangePercent: Optional[float] = None
    uniqueWallet30m: Optional[int] = None
    uniqueWalletHistory30m: Optional[int] = None
    uniqueWallet30mChangePercent: Optional[float] = None
    uniqueWallet1h: Optional[int] = None
    uniqueWalletHistory1h: Optional[int] = None
    uniqueWallet1hChangePercent: Optional[float] = None
    uniqueWallet2h: Optional[int] = None
    uniqueWalletHistory2h: Optional[int] = None
    uniqueWallet2hChangePercent: Optional[float] = None
    uniqueWallet4h: Optional[int] = None
    uniqueWalletHistory4h: Optional[int] = None
    uniqueWallet4hChangePercent: Optional[float] = None
    uniqueWallet8h: Optional[int] = None
    uniqueWalletHistory8h: Optional[int] = None
    uniqueWallet8hChangePercent: Optional[float] = None
    uniqueWallet24h: Optional[int] = None
    uniqueWalletHistory24h: Optional[int] = None
    uniqueWallet24hChangePercent: Optional[float] = None
    totalSupply: Optional[float] = None
    circulatingSupply: Optional[float] = None
    holder: Optional[int] = None
    trade1m: Optional[int] = None
    tradeHistory1m: Optional[int] = None
    trade1mChangePercent: Optional[float] = None
    sell1m: Optional[int] = None
    sellHistory1m: Optional[int] = None
    sell1mChangePercent: Optional[float] = None
    buy1m: Optional[int] = None
    buyHistory1m: Optional[int] = None
    buy1mChangePercent: Optional[float] = None
    trade5m: Optional[int] = None
    tradeHistory5m: Optional[int] = None
    trade5mChangePercent: Optional[float] = None
    sell5m: Optional[int] = None
    sellHistory5m: Optional[int] = None
    sell5mChangePercent: Optional[float] = None
    buy5m: Optional[int] = None
    buyHistory5m: Optional[int] = None
    buy5mChangePercent: Optional[float] = None
    trade30m: Optional[int] = None
    tradeHistory30m: Optional[int] = None
    trade30mChangePercent: Optional[float] = None
    sell30m: Optional[int] = None
    sellHistory30m: Optional[int] = None
    sell30mChangePercent: Optional[float] = None
    buy30m: Optional[int] = None
    buyHistory30m: Optional[int] = None
    buy30mChangePercent: Optional[float] = None
    trade1h: Optional[int] = None
    tradeHistory1h: Optional[int] = None
    trade1hChangePercent: Optional[float] = None
    sell1h: Optional[int] = None
    sellHistory1h: Optional[int] = None
    sell1hChangePercent: Optional[float] = None
    buy1h: Optional[int] = None
    buyHistory1h: Optional[int] = None
    buy1hChangePercent: Optional[float] = None
    trade2h: Optional[int] = None
    tradeHistory2h: Optional[int] = None
    trade2hChangePercent: Optional[float] = None
    sell2h: Optional[int] = None
    sellHistory2h: Optional[int] = None
    sell2hChangePercent: Optional[float] = None
    buy2h: Optional[int] = None
    buyHistory2h: Optional[int] = None
    buy2hChangePercent: Optional[float] = None
    trade4h: Optional[int] = None
    tradeHistory4h: Optional[int] = None
    trade4hChangePercent: Optional[float] = None
    sell4h: Optional[int] = None
    sellHistory4h: Optional[int] = None
    sell4hChangePercent: Optional[float] = None
    buy4h: Optional[int] = None
    buyHistory4h: Optional[int] = None
    buy4hChangePercent: Optional[float] = None
    trade8h: Optional[int] = None
    tradeHistory8h: Optional[int] = None
    trade8hChangePercent: Optional[float] = None
    sell8h: Optional[int] = None
    sellHistory8h: Optional[int] = None
    sell8hChangePercent: Optional[float] = None
    buy8h: Optional[int] = None
    buyHistory8h: Optional[int] = None
    buy8hChangePercent: Optional[float] = None
    trade24h: Optional[int] = None
    tradeHistory24h: Optional[int] = None
    trade24hChangePercent: Optional[float] = None
    sell24h: Optional[int] = None
    sellHistory24h: Optional[int] = None
    sell24hChangePercent: Optional[float] = None
    buy24h: Optional[int] = None
    buyHistory24h: Optional[int] = None
    buy24hChangePercent: Optional[float] = None
    v1m: Optional[float] = None
    v1mUSD: Optional[float] = None
    vHistory1m: Optional[float] = None
    vHistory1mUSD: Optional[float] = None
    v1mChangePercent: Optional[float] = None
    vBuy1m: Optional[float] = None
    vBuy1mUSD: Optional[float] = None
    vBuyHistory1m: Optional[float] = None
    vBuyHistory1mUSD: Optional[float] = None
    vBuy1mChangePercent: Optional[float] = None
    vSell1m: Optional[float] = None
    vSell1mUSD: Optional[float] = None
    vSellHistory1m: Optional[float] = None
    vSellHistory1mUSD: Optional[float] = None
    vSell1mChangePercent: Optional[float] = None
    v5m: Optional[float] = None
    v5mUSD: Optional[float] = None
    vHistory5m: Optional[float] = None
    vHistory5mUSD: Optional[float] = None
    v5mChangePercent: Optional[float] = None
    vBuy5m: Optional[float] = None
    vBuy5mUSD: Optional[float] = None
    vBuyHistory5m: Optional[float] = None
    vBuyHistory5mUSD: Optional[float] = None
    vBuy5mChangePercent: Optional[float] = None
    vSell5m: Optional[float] = None
    vSell5mUSD: Optional[float] = None
    vSellHistory5m: Optional[float] = None
    vSellHistory5mUSD: Optional[float] = None
    vSell5mChangePercent: Optional[float] = None
    v30m: Optional[float] = None
    v30mUSD: Optional[float] = None
    vHistory30m: Optional[float] = None
    vHistory30mUSD: Optional[float] = None
    v30mChangePercent: Optional[float] = None
    vBuy30m: Optional[float] = None
    vBuy30mUSD: Optional[float] = None
    vBuyHistory30m: Optional[float] = None
    vBuyHistory30mUSD: Optional[float] = None
    vBuy30mChangePercent: Optional[float] = None
    vSell30m: Optional[float] = None
    vSell30mUSD: Optional[float] = None
    vSellHistory30m: Optional[float] = None
    vSellHistory30mUSD: Optional[float] = None
    vSell30mChangePercent: Optional[float] = None
    v1h: Optional[float] = None
    v1hUSD: Optional[float] = None
    vHistory1h: Optional[float] = None
    vHistory1hUSD: Optional[float] = None
    v1hChangePercent: Optional[float] = None
    vBuy1h: Optional[float] = None
    vBuy1hUSD: Optional[float] = None
    vBuyHistory1h: Optional[float] = None
    vBuyHistory1hUSD: Optional[float] = None
    vBuy1hChangePercent: Optional[float] = None
    vSell1h: Optional[float] = None
    vSell1hUSD: Optional[float] = None
    vSellHistory1h: Optional[float] = None
    vSellHistory1hUSD: Optional[float] = None
    vSell1hChangePercent: Optional[float] = None
    v2h: Optional[float] = None
    v2hUSD: Optional[float] = None
    vHistory2h: Optional[float] = None
    vHistory2hUSD: Optional[float] = None
    v2hChangePercent: Optional[float] = None
    vBuy2h: Optional[float] = None
    vBuy2hUSD: Optional[float] = None
    vBuyHistory2h: Optional[float] = None
    vBuyHistory2hUSD: Optional[float] = None
    vBuy2hChangePercent: Optional[float] = None
    vSell2h: Optional[float] = None
    vSell2hUSD: Optional[float] = None
    vSellHistory2h: Optional[float] = None
    vSellHistory2hUSD: Optional[float] = None
    vSell2hChangePercent: Optional[float] = None
    v4h: Optional[float] = None
    v4hUSD: Optional[float] = None
    vHistory4h: Optional[float] = None
    vHistory4hUSD: Optional[float] = None
    v4hChangePercent: Optional[float] = None
    vBuy4h: Optional[float] = None
    vBuy4hUSD: Optional[float] = None
    vBuyHistory4h: Optional[float] = None
    vBuyHistory4hUSD: Optional[float] = None
    vBuy4hChangePercent: Optional[float] = None
    vSell4h: Optional[float] = None
    vSell4hUSD: Optional[float] = None
    vSellHistory4h: Optional[float] = None
    vSellHistory4hUSD: Optional[float] = None
    vSell4hChangePercent: Optional[float] = None
    v8h: Optional[float] = None
    v8hUSD: Optional[float] = None
    vHistory8h: Optional[float] = None
    vHistory8hUSD: Optional[float] = None
    v8hChangePercent: Optional[float] = None
    vBuy8h: Optional[float] = None
    vBuy8hUSD: Optional[float] = None
    vBuyHistory8h: Optional[float] = None
    vBuyHistory8hUSD: Optional[float] = None
    vBuy8hChangePercent: Optional[float] = None
    vSell8h: Optional[float] = None
    vSell8hUSD: Optional[float] = None
    vSellHistory8h: Optional[float] = None
    vSellHistory8hUSD: Optional[float] = None
    vSell8hChangePercent: Optional[float] = None
    v24h: Optional[float] = None
    v24hUSD: Optional[float] = None
    vHistory24h: Optional[float] = None
    vHistory24hUSD: Optional[float] = None
    v24hChangePercent: Optional[float] = None
    vBuy24h: Optional[float] = None
    vBuy24hUSD: Optional[float] = None
    vBuyHistory24h: Optional[float] = None
    vBuyHistory24hUSD: Optional[float] = None
    vBuy24hChangePercent: Optional[float] = None
    vSell24h: Optional[float] = None
    vSell24hUSD: Optional[float] = None
    vSellHistory24h: Optional[float] = None
    vSellHistory24hUSD: Optional[float] = None
    vSell24hChangePercent: Optional[float] = None
    numberMarkets: Optional[int] = None
    isScaledUiToken: Optional[bool] = None
    multiplier: Optional[float] = None


# https://docs.birdeye.so/reference/get-defi-token_security
class TokenSecurityResponse(BaseModel):
    creatorAddress: Optional[str] = None
    creatorOwnerAddress: Optional[str] = None
    creatorBalance: Optional[float] = None
    creatorPercentage: Optional[float] = None
    ownerAddress: Optional[str] = None
    ownerOfOwnerAddress: Optional[str] = None
    ownerBalance: Optional[float] = None
    ownerPercentage: Optional[float] = None
    creationTx: Optional[str] = None
    creationTime: Optional[int] = None
    creationSlot: Optional[int] = None
    mintTx: Optional[str] = None
    mintTime: Optional[int] = None
    mintSlot: Optional[int] = None
    metaplexUpdateAuthority: Optional[str] = None
    metaplexOwnerUpdateAuthority: Optional[str] = None
    metaplexUpdateAuthorityBalance: Optional[float] = None
    metaplexUpdateAuthorityPercent: Optional[float] = None
    mutableMetadata: Optional[bool] = None
    top10HolderBalance: Optional[float] = None
    top10HolderPercent: Optional[float] = None
    top10UserBalance: Optional[float] = None
    top10UserPercent: Optional[float] = None
    isTrueToken: Optional[bool] = None
    fakeToken: Optional[bool] = None
    totalSupply: Optional[float] = None
    preMarketHolder: List = []
    lockInfo: Optional[dict] = None
    freezeable: Optional[bool] = None
    freezeAuthority: Optional[str] = None
    transferFeeEnable: Optional[bool] = None
    transferFeeData: Optional[str] = None
    isToken2022: Optional[bool] = None
    nonTransferable: Optional[bool] = None
    jupStrictList: Optional[bool] = None


# https://docs.birdeye.so/reference/get-defi-token_creation_info
class TokenCreationInfoResponse(BaseModel):
    txHash: Optional[str] = None
    slot: Optional[int] = None
    tokenAddress: Optional[str] = None
    decimals: Optional[int] = None
    owner: Optional[str] = None
    blockUnixTime: Optional[int] = None
    blockHumanTime: Optional[str] = None


class TokenHolder(BaseModel):
    amount: Optional[str] = None
    decimals: Optional[int] = None
    mint: Optional[str] = None
    owner: Optional[str] = None
    token_account: Optional[str] = None
    ui_amount: Optional[float] = None
    is_scaled_ui_token: Optional[bool] = None
    multiplier: Optional[float] = None


# https://docs.birdeye.so/reference/get-defi-v3-token-holder
class TokenHoldersResponse(BaseModel):
    items: List[TokenHolder] = []

class WalletPortfolioItem(BaseModel):
    address: Optional[str] = None
    decimals: Optional[int] = None
    balance: Optional[int] = None
    uiAmount: Optional[float] = None
    chainId: Optional[str] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    icon: Optional[str] = None
    logoURI: Optional[str] = None
    priceUsd: Optional[float] = None
    valueUsd: Optional[float] = None
    isScaledUiToken: Optional[bool] = None
    multiplier: Optional[float] = None


class WalletPortfolioResponse(BaseModel):
    items: List[WalletPortfolioItem] = []
