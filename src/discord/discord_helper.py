import os
from typing import Optional, List
from dotenv import load_dotenv
import discord
from discord import app_commands
from src.sol_data.data_manager import DataManager, DataManagerAPIError
from src.sol_data.data_models import WalletPortfolioItem, TokenOverviewResponse
from src.discord.logger import handler, logger
from src.db.database import DatabaseConnection

load_dotenv()

WRAPPED_TOKENS = {"SOL": "So11111111111111111111111111111111111111112", "ETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"}

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

if not TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN is not set in your environment/.env")
if not BIRDEYE_API_KEY:
    raise SystemExit("BIRDEYE_API_KEY is not set in your environment/.env")

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.logger = logger
        self.db = DatabaseConnection()
        self.data_manager = DataManager(api_key=BIRDEYE_API_KEY, chain="solana")

    async def setup_hook(self):
        await self.tree.sync()



client = MyClient(intents=intents)


@client.event
async def on_ready():
    client.logger.info(f"Logged in as {client.user} ({client.user.id})")


@client.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    client.logger.info(f"Hello command received: {interaction.user.id}")
    await interaction.response.send_message("Hello!")

@client.tree.command(name="setup", description="Setup your wallet and price watch")
@app_commands.describe(wallet_address="The Solana wallet address to check", price_watch="The price to watch")
async def setup(interaction: discord.Interaction, wallet_address: str, price_watch: float):
    client.logger.info(f"Setup command received: {wallet_address}, {price_watch}")
    try:
        client.db.upsert_wallet(interaction.user.id, wallet_address)
        client.db.upsert_price_watch(interaction.user.id, price_watch)
        interaction.response.send_message(
            f"Setup complete: {wallet_address}, {price_watch}! Now you will receive a notification when the price of the token you are watching reaches your threshold."
        )
    except Exception as e:
        await interaction.response.send_message(f"Error setting up: {str(e)}")


@client.tree.command(name="alert", description="Get a token alert")
async def get_token_alert(interaction: discord.Interaction):
    try:
        print(f"DEBUG: Alert command started for user {interaction.user.id}")
        logger.info(f"Alert command started for user {interaction.user.id}")

        # Defer the response immediately to avoid timeout
        await interaction.response.defer()
        print("DEBUG: Interaction response deferred")

        # Check if user has setup
        price_watch = client.db.get_price_watch(interaction.user.id)
        wallet = client.db.get_wallet(interaction.user.id)

        print(f"DEBUG: price_watch = {price_watch}, wallet = {wallet}")
        logger.info(f"Retrieved price_watch: {price_watch}, wallet: {wallet}")

        if not price_watch or not wallet:
            print("DEBUG: No price watch or wallet found")
            await interaction.followup.send("You haven't setup a price watch yet. Please use the `/setup` command to setup a price watch.")
            return

        print(f"DEBUG: Getting portfolio for wallet {wallet.wallet_address}")
        logger.info(f"Getting portfolio for wallet {wallet.wallet_address}")

        # Get user's tokens
        portfolio_response = client.data_manager.get_wallet_portfolio(wallet.wallet_address)
        print(f"DEBUG: Portfolio response: {portfolio_response}")

        all_users_tokens = portfolio_response.items
        print(f"DEBUG: Found {len(all_users_tokens)} tokens in portfolio")
        logger.info(f"Found {len(all_users_tokens)} tokens in portfolio")

        if not all_users_tokens:
            await interaction.followup.send("No tokens found in your wallet portfolio.")
            return

        # Send status message
        await interaction.followup.send(
            f"🔍 Checking {len(all_users_tokens)} tokens in your portfolio for price changes above {price_watch.threshold}%..."
        )

        tokens_meeting_threshold = []
        tokens_checked = 0

        for token in all_users_tokens:
            tokens_checked += 1
            token_name = token.name
            token_address = token.address
            if token_name in WRAPPED_TOKENS:
                token_address = WRAPPED_TOKENS[token_name]
            print(f"DEBUG: Checking token {tokens_checked}/{len(all_users_tokens)}: {token_address}")

            try:
                token_overview = client.data_manager.get_token_overview(token_address)
            except DataManagerAPIError as e:
                logger.error(f"Failed to get token data for {token_address}: {e}")
                continue

            price_change_5m = token_overview.priceChange5mPercent

            print(f"DEBUG: Token {token_address} - Price change 5m: {price_change_5m}%, Threshold: {price_watch.threshold}%")
            logger.info(f"Token {token_address} - Price change: {price_change_5m}%, Threshold: {price_watch.threshold}%")

            if price_change_5m is None:
                print(f"DEBUG: Token {token_address} has no price change 5m")
                logger.info(f"Token {token_address} has no price change 5m")
                continue

            if price_change_5m > price_watch.threshold:
                print(f"DEBUG: Token {token_address} meets threshold! Getting additional data...")

                try:
                    token_creation_info = client.data_manager.get_token_creation_info(token_address)
                    token_creation_time = token_creation_info.blockHumanTime
                except DataManagerAPIError as e:
                    logger.error(f"Failed to get token creation info for {token_address}: {e}")
                    token_creation_time = "-"

                try:
                    security_info = client.data_manager.get_token_security(token_address)
                    no_mint = security_info.ownerOfOwnerAddress == "11111111111111111111111111111111"
                    non_transferable = bool(security_info.nonTransferable)
                    blacklist_safe = not non_transferable
                except DataManagerAPIError as e:
                    logger.error(f"Failed to get security info for {token_address}: {e}")
                    no_mint = None
                    blacklist_safe = None


                total_supply = token_overview.totalSupply

                try:
                    top_10_holders = client.data_manager.get_token_holders(token_address)
                    top_10_holders_data = top_10_holders.items
                    top_10_holders_pct = [item.ui_amount / total_supply * 100 for item in top_10_holders_data]
                    top_10_holders_pct_str = [f"{pct:.2f}%" for pct in top_10_holders_pct]
                    top_10_holders_pct_str_formatted = " | ".join(top_10_holders_pct_str)
                except DataManagerAPIError as e:
                    logger.error(f"Failed to get top 10 holders for {token_address}: {e}")
                    top_10_holders_data = []
                    top_10_holders_pct = []
                    top_10_holders_pct_str = []


                formatted_response = build_token_card(
                    token,
                    token_overview,
                    token_creation_time,
                    no_mint,
                    blacklist_safe,
                    top_10_holders_pct_str_formatted,
                    "Solana",
                )

                tokens_meeting_threshold.append(formatted_response)

        print(f"DEBUG: Checked {tokens_checked} tokens, {len(tokens_meeting_threshold)} meet threshold")
        logger.info(f"Checked {tokens_checked} tokens, {len(tokens_meeting_threshold)} meet threshold")

        # Send followup messages with results
        if tokens_meeting_threshold:
            print("DEBUG: Sending alert for tokens meeting threshold")
            for i, token_alert in enumerate(tokens_meeting_threshold):
                if i == 0:
                    await interaction.followup.send(f"🚨 **ALERT: {len(tokens_meeting_threshold)} token(s) meet your threshold!**\n\n{token_alert}")
                else:
                    await interaction.followup.send(token_alert)
        else:
            print("DEBUG: No tokens meet the threshold, sending 'no alerts' message")
            await interaction.followup.send(
                f"✅ No alerts: None of your {tokens_checked} tokens currently exceed your {price_watch.threshold}% threshold."
            )

    except Exception as e:
        print(f"DEBUG: Exception in alert command: {str(e)}")
        logger.error(f"Exception in alert command: {str(e)}", exc_info=True)

        # Make sure we always respond to the interaction
        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
            await interaction.followup.send(f"❌ An error occurred while checking alerts: {str(e)}")
        except Exception as response_error:
            print(f"DEBUG: Failed to send error response: {str(response_error)}")
            logger.error(f"Failed to send error response: {str(response_error)}")


def run_bot():
    """Function to run the Discord bot"""
    client.run(TOKEN, log_handler=handler)


def _fmt_usd(n):
    try:
        n = float(n)
    except Exception:
        return "-"
    if n < 0:
        sign, n = "-", -n
    else:
        sign = ""
    if n >= 1_000_000_000:
        return f"{sign}${n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{sign}${n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{sign}${n / 1_000:.2f}K"
    return f"{sign}${n:,.2f}"


def _fmt_price_with_zeroes(p):
    try:
        p = float(p)
    except Exception:
        return "-"
    if p == 0:
        return "$0.00"
    if p >= 0.001:
        s = f"${p:,.6f}".rstrip("0").rstrip(".")
        return s
    # represent as $0.0{n}digits
    frac = f"{p:.18f}".split(".")[1].rstrip("0")
    n0 = 0
    for ch in frac:
        if ch == "0":
            n0 += 1
        else:
            break
    tail = frac[n0 : n0 + 6] or "0"
    return f"$0.0{{{n0}}}{tail}"


def _yn(flag):
    return "✅" if flag is True else ("❌" if flag is False else "—")


def build_token_card(
    token: WalletPortfolioItem,
    token_overview: TokenOverviewResponse,
    token_creation_time: str,
    no_mint: Optional[bool] = None,
    blacklist_safe: Optional[bool] = None,  # bool | None (from token_security)
    top_10_holders_pct_str_formatted: List[float] = None,  # list[float] (each already in %), optional
    chain="Solana",
):
    # Pull what you already computed in your snippet
    liquidity = token_overview.liquidity
    price = token_overview.price
    token_symbol = token_overview.symbol or "Unknown"
    market_cap = token_overview.marketCap
    price_change_5m = token_overview.priceChange5mPercent

    # Header
    addr = token.address or "—"
    header_left = f"${token_symbol} – {chain}"
    header = f"{header_left}\n{addr}"

    # Lines matching the original bot
    # Create
    line_info_create = f"Creation Time: {token_creation_time}"

    # MC, Liq, Price
    line_info_mc = f"MC: {_fmt_usd(market_cap)}"
    line_info_liq = f"Liq: {_fmt_usd(liquidity)}"
    line_info_px = f"Price: {_fmt_price_with_zeroes(price)} ({price_change_5m:+.2f}%)"

    # Security
    line_sec = f"NoMint {_yn(no_mint)} | Blacklist {_yn(blacklist_safe)}"

    # Put it all together
    card = (
        f"""{header}

📋 Info
{line_info_create}
{line_info_mc}
{line_info_liq}
{line_info_px}

🛡️ Security
{line_sec}

💰 Top10 Holding
{top_10_holders_pct_str_formatted}
"""
    ).strip()

    return card
