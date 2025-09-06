from pydantic import BaseModel, RootModel
from typing import Optional, List, Dict


class Price(BaseModel):
    isScaledUiToken: bool
    value: float
    updateUnixTime: int
    updateHumanTime: str
    priceChange24h: float
    priceInNative: float
    liquidity: float


class MultiPriceResponse(RootModel[Dict[str, Price]]):
    root: Dict[str, Price]


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
    # Basic token info
    address: str
    decimals: int
    symbol: str
    name: str
    marketCap: float
    fdv: float
    extensions: TokenExtensions
    logoURI: str
    liquidity: float

    # Last trade info
    lastTradeUnixTime: int
    lastTradeHumanTime: str

    # Current price and price changes
    price: float
    history1mPrice: float
    priceChange1mPercent: float
    history5mPrice: float
    priceChange5mPercent: float
    history30mPrice: float
    priceChange30mPercent: float
    history1hPrice: float
    priceChange1hPercent: float
    history2hPrice: float
    priceChange2hPercent: float
    history4hPrice: float
    priceChange4hPercent: float
    history6hPrice: float
    priceChange6hPercent: float
    history8hPrice: float
    priceChange8hPercent: float
    history12hPrice: float
    priceChange12hPercent: float
    history24hPrice: float
    priceChange24hPercent: float

    # Unique wallet metrics
    uniqueWallet1m: int
    uniqueWalletHistory1m: int
    uniqueWallet1mChangePercent: float
    uniqueWallet5m: int
    uniqueWalletHistory5m: int
    uniqueWallet5mChangePercent: float
    uniqueWallet30m: int
    uniqueWalletHistory30m: int
    uniqueWallet30mChangePercent: float
    uniqueWallet1h: int
    uniqueWalletHistory1h: int
    uniqueWallet1hChangePercent: float
    uniqueWallet2h: int
    uniqueWalletHistory2h: int
    uniqueWallet2hChangePercent: float
    uniqueWallet4h: int
    uniqueWalletHistory4h: int
    uniqueWallet4hChangePercent: float
    uniqueWallet8h: int
    uniqueWalletHistory8h: int
    uniqueWallet8hChangePercent: float
    uniqueWallet24h: int
    uniqueWalletHistory24h: int
    uniqueWallet24hChangePercent: float

    # Supply metrics
    totalSupply: float
    circulatingSupply: float
    holder: int

    # Trade count metrics
    trade1m: int
    tradeHistory1m: int
    trade1mChangePercent: float
    sell1m: int
    sellHistory1m: int
    sell1mChangePercent: float
    buy1m: int
    buyHistory1m: int
    buy1mChangePercent: float
    trade5m: int
    tradeHistory5m: int
    trade5mChangePercent: float
    sell5m: int
    sellHistory5m: int
    sell5mChangePercent: float
    buy5m: int
    buyHistory5m: int
    buy5mChangePercent: float
    trade30m: int
    tradeHistory30m: int
    trade30mChangePercent: float
    sell30m: int
    sellHistory30m: int
    sell30mChangePercent: float
    buy30m: int
    buyHistory30m: int
    buy30mChangePercent: float
    trade1h: int
    tradeHistory1h: int
    trade1hChangePercent: float
    sell1h: int
    sellHistory1h: int
    sell1hChangePercent: float
    buy1h: int
    buyHistory1h: int
    buy1hChangePercent: float
    trade2h: int
    tradeHistory2h: int
    trade2hChangePercent: float
    sell2h: int
    sellHistory2h: int
    sell2hChangePercent: float
    buy2h: int
    buyHistory2h: int
    buy2hChangePercent: float
    trade4h: int
    tradeHistory4h: int
    trade4hChangePercent: float
    sell4h: int
    sellHistory4h: int
    sell4hChangePercent: float
    buy4h: int
    buyHistory4h: int
    buy4hChangePercent: float
    trade8h: int
    tradeHistory8h: int
    trade8hChangePercent: float
    sell8h: int
    sellHistory8h: int
    sell8hChangePercent: float
    buy8h: int
    buyHistory8h: int
    buy8hChangePercent: float
    trade24h: int
    tradeHistory24h: int
    trade24hChangePercent: float
    sell24h: int
    sellHistory24h: int
    sell24hChangePercent: float
    buy24h: int
    buyHistory24h: int
    buy24hChangePercent: float

    # Volume metrics
    v1m: float
    v1mUSD: float
    vHistory1m: float
    vHistory1mUSD: float
    v1mChangePercent: float
    vBuy1m: float
    vBuy1mUSD: float
    vBuyHistory1m: float
    vBuyHistory1mUSD: float
    vBuy1mChangePercent: float
    vSell1m: float
    vSell1mUSD: float
    vSellHistory1m: float
    vSellHistory1mUSD: float
    vSell1mChangePercent: float
    v5m: float
    v5mUSD: float
    vHistory5m: float
    vHistory5mUSD: float
    v5mChangePercent: float
    vBuy5m: float
    vBuy5mUSD: float
    vBuyHistory5m: float
    vBuyHistory5mUSD: float
    vBuy5mChangePercent: float
    vSell5m: float
    vSell5mUSD: float
    vSellHistory5m: float
    vSellHistory5mUSD: float
    vSell5mChangePercent: float
    v30m: float
    v30mUSD: float
    vHistory30m: float
    vHistory30mUSD: float
    v30mChangePercent: float
    vBuy30m: float
    vBuy30mUSD: float
    vBuyHistory30m: float
    vBuyHistory30mUSD: float
    vBuy30mChangePercent: float
    vSell30m: float
    vSell30mUSD: float
    vSellHistory30m: float
    vSellHistory30mUSD: float
    vSell30mChangePercent: float
    v1h: float
    v1hUSD: float
    vHistory1h: float
    vHistory1hUSD: float
    v1hChangePercent: float
    vBuy1h: float
    vBuy1hUSD: float
    vBuyHistory1h: float
    vBuyHistory1hUSD: float
    vBuy1hChangePercent: float
    vSell1h: float
    vSell1hUSD: float
    vSellHistory1h: float
    vSellHistory1hUSD: float
    vSell1hChangePercent: float
    v2h: float
    v2hUSD: float
    vHistory2h: float
    vHistory2hUSD: float
    v2hChangePercent: float
    vBuy2h: float
    vBuy2hUSD: float
    vBuyHistory2h: float
    vBuyHistory2hUSD: float
    vBuy2hChangePercent: float
    vSell2h: float
    vSell2hUSD: float
    vSellHistory2h: float
    vSellHistory2hUSD: float
    vSell2hChangePercent: float
    v4h: float
    v4hUSD: float
    vHistory4h: float
    vHistory4hUSD: float
    v4hChangePercent: float
    vBuy4h: float
    vBuy4hUSD: float
    vBuyHistory4h: float
    vBuyHistory4hUSD: float
    vBuy4hChangePercent: float
    vSell4h: float
    vSell4hUSD: float
    vSellHistory4h: float
    vSellHistory4hUSD: float
    vSell4hChangePercent: float
    v8h: float
    v8hUSD: float
    vHistory8h: float
    vHistory8hUSD: float
    v8hChangePercent: float
    vBuy8h: float
    vBuy8hUSD: float
    vBuyHistory8h: float
    vBuyHistory8hUSD: float
    vBuy8hChangePercent: float
    vSell8h: float
    vSell8hUSD: float
    vSellHistory8h: float
    vSellHistory8hUSD: float
    vSell8hChangePercent: float
    v24h: float
    v24hUSD: float
    vHistory24h: float
    vHistory24hUSD: float
    v24hChangePercent: float
    vBuy24h: float
    vBuy24hUSD: float
    vBuyHistory24h: float
    vBuyHistory24hUSD: float
    vBuy24hChangePercent: float
    vSell24h: float
    vSell24hUSD: float
    vSellHistory24h: float
    vSellHistory24hUSD: float
    vSell24hChangePercent: float

    # Additional metrics
    numberMarkets: int
    isScaledUiToken: bool
    multiplier: Optional[float] = None


class TokenSecurityResponse(BaseModel):
    # Creator information
    creatorAddress: str
    creatorOwnerAddress: Optional[str] = None
    creatorBalance: float
    creatorPercentage: float

    # Owner information
    ownerAddress: Optional[str] = None
    ownerOfOwnerAddress: Optional[str] = None
    ownerBalance: Optional[float] = None
    ownerPercentage: Optional[float] = None

    # Creation details
    creationTx: str
    creationTime: int
    creationSlot: int

    # Mint details
    mintTx: str
    mintTime: int
    mintSlot: int

    # Metaplex metadata authority
    metaplexUpdateAuthority: str
    metaplexOwnerUpdateAuthority: Optional[str] = None
    metaplexUpdateAuthorityBalance: float
    metaplexUpdateAuthorityPercent: float
    mutableMetadata: bool

    # Top holders information
    top10HolderBalance: float
    top10HolderPercent: float
    top10UserBalance: float
    top10UserPercent: float

    # Token characteristics
    isTrueToken: Optional[bool] = None
    fakeToken: Optional[bool] = None
    totalSupply: float

    # Pre-market and holder data
    preMarketHolder: List = []  # Empty list in the example, could be List[str] if it contains addresses

    # Lock and freeze information
    lockInfo: Optional[str] = None  # Could be a complex object, using str for now
    freezeable: Optional[bool] = None
    freezeAuthority: Optional[str] = None

    # Transfer fee information
    transferFeeEnable: Optional[bool] = None
    transferFeeData: Optional[str] = None  # Could be a complex object, using str for now

    # Token standard and features
    isToken2022: bool
    nonTransferable: Optional[bool] = None
    jupStrictList: bool


class TokenCreationInfoResponse(BaseModel):
    # Transaction details
    txHash: str
    slot: int

    # Token information
    tokenAddress: str
    decimals: int
    owner: str

    # Timing information
    blockUnixTime: int
    blockHumanTime: str


class TokenHolder(BaseModel):
    amount: str
    decimals: int
    mint: str
    owner: str
    token_account: str
    ui_amount: float
    is_scaled_ui_token: bool
    multiplier: Optional[float] = None


class TokenHoldersResponse(BaseModel):
    items: List[TokenHolder]


class MintBurnTx(BaseModel):
    amount: str
    block_human_time: str
    block_time: int
    common_type: str
    decimals: int
    mint: str
    program_id: str
    slot: int
    tx_hash: str
    ui_amount: float
    ui_amount_string: str


class MintBurnTxsResponse(BaseModel):
    items: List[MintBurnTx]


class WalletPortfolioItem(BaseModel):
    address: str
    decimals: int
    balance: int
    uiAmount: float
    chainId: str
    name: str
    symbol: str
    icon: str
    logoURI: str
    priceUsd: float
    valueUsd: float
    isScaledUiToken: bool
    multiplier: Optional[float] = None


class WalletPortfolioResponse(BaseModel):
    items: List[WalletPortfolioItem]
