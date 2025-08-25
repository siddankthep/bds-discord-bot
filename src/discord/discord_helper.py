import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
import discord
from discord import app_commands
from src.bds.birdeye import BirdeyeHelper
from src.discord.logger import handler, logger
from src.db.database import DatabaseConnection

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

if not TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN is not set in your environment/.env")
if not BIRDEYE_API_KEY:
    raise SystemExit("BIRDEYE_API_KEY is not set in your environment/.env")

intents = discord.Intents.default()
intents.message_content = True  # also enable this in the Developer Portal


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        # self.monitor_task: Optional[asyncio.Task] = None
        self.logger = logger
        self.db = DatabaseConnection()
        self.bds = BirdeyeHelper(api_key=BIRDEYE_API_KEY, chain="solana")

    async def setup_hook(self):
        await self.tree.sync()
        # start background monitor
        # if not self.monitor_task or self.monitor_task.done():
        #     self.monitor_task = asyncio.create_task(self.monitor_loop())

    async def send_notification(self, user_id: int, text: str, channel_id: Optional[int]):
        try:
            if channel_id:
                ch = self.get_channel(channel_id) or await self.fetch_channel(channel_id)
                await ch.send(text)
            else:
                user = self.get_user(user_id) or await self.fetch_user(user_id)
                await user.send(text)
            logger.info(f"Sent notification to {user_id} in channel {channel_id}")

        except Exception as e:
            logger.warning("Notify failed for %s: %s", user_id, e)

    async def monitor_loop(self):
        # Single loop scans all watches; each user has its own poll cadence via next_due bookkeeping
        logger.info("Price monitor started")
        while True:
            try:
                all_wallets = await self.db.get_all_wallets()
                for wallet in all_wallets:
                    price_watch = await self.db.get_price_watch(wallet.discord_id)
                    if price_watch:
                        all_users_tokens = self.bds.get_wallet_portfolio(wallet.wallet_address).get("data", {}).get("items", [])
                        for token in all_users_tokens:
                            token_overview = self.bds.get_token_overview(token.get("address"))
                            if not token_overview.get("success"):
                                logger.error(f"Failed to get token data for {token.get('address')}: {token_overview.get('error')}")
                                continue
                            token_overview_data = token_overview.get("data", {})
                            price_change_5m = token_overview_data.get("priceChange5mPercent", 0)
                            if price_change_5m > price_watch.threshold:
                                token_creation_info = self.bds.get_token_creation_info(token.get("address"))
                                if not token_creation_info.get("success"):
                                    token_creation_time = "-"
                                else:
                                    token_creation_time = (
                                        token_creation_info.get("data", {}).get("blockHumanTime", "-") if token_creation_info.get("data") else "-"
                                    )

                                security_info = self.bds.get_token_security(token.get("address"))
                                if not security_info.get("success"):
                                    security_info = "-"
                                else:
                                    security_data = security_info.get("data", {})
                                    no_mint = security_data.get("ownerOfOwnerAddress") == "11111111111111111111111111111111"

                                    non_transferable = bool(security_data.get("nonTransferable"))  # None/False -> not enforced
                                    blacklist_safe = not non_transferable

                                    total_supply = token_overview_data.get("totalSupply", 1)

                                top_10_holders = self.bds.get_token_holders(token.get("address"))
                                top_10_holders_data = top_10_holders.get("data", {}).get("items", [])
                                top_10_holders_pct = [item.get("ui_amount", 0) / total_supply * 100 for item in top_10_holders_data]
                                top_10_holders_pct_str = [f"{pct:.2f}%" for pct in top_10_holders_pct]
                                top_10_holders_pct_str_formatted = " | ".join(top_10_holders_pct_str)

                                formatted_response = build_token_card(
                                    token,
                                    token_overview_data,
                                    token_creation_time,
                                    no_mint,
                                    blacklist_safe,
                                    top_10_holders_pct_str_formatted,
                                    "Solana",
                                )

                                await self.send_notification(
                                    wallet.discord_id,
                                    formatted_response,
                                    None,
                                )

                await asyncio.sleep(5 * 60)  # Update every frame
            except Exception as e:
                logger.exception("Monitor loop error: %s", e)
                await asyncio.sleep(5)


client = MyClient(intents=intents)


@client.event
async def on_ready():
    client.logger.info(f"Logged in as {client.user} ({client.user.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author.id == client.user.id:
        return
    if message.content.startswith("$hello"):
        client.logger.info(f"Message received: {message.content}")
        await message.channel.send("Hello!")


@client.tree.command(name="hello", description="Say hello")
@app_commands.describe(name="The name to say hello to")
async def hello(interaction: discord.Interaction, name: str):
    client.logger.info(f"Hello command received: {name}")
    await interaction.response.send_message(f"Hello {name}!")


@client.tree.command(name="setup", description="Setup your wallet and price watch")
@app_commands.describe(wallet_address="The Solana wallet address to check", price_watch="The price to watch")
async def setup(interaction: discord.Interaction, wallet_address: str, price_watch: float):
    client.logger.info(f"Setup command received: {wallet_address}, {price_watch}")
    try:
        await client.db.insert_ignore_wallet(interaction.user.id, wallet_address)
        await client.db.upsert_price_watch(interaction.user.id, price_watch)
        await interaction.response.send_message(
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
        price_watch = await client.db.get_price_watch(interaction.user.id)
        wallet = await client.db.get_wallet(interaction.user.id)

        print(f"DEBUG: price_watch = {price_watch}, wallet = {wallet}")
        logger.info(f"Retrieved price_watch: {price_watch}, wallet: {wallet}")

        if not price_watch or not wallet:
            print("DEBUG: No price watch or wallet found")
            await interaction.followup.send("You haven't setup a price watch yet. Please use the `/setup` command to setup a price watch.")
            return

        print(f"DEBUG: Getting portfolio for wallet {wallet.wallet_address}")
        logger.info(f"Getting portfolio for wallet {wallet.wallet_address}")

        # Get user's tokens
        portfolio_response = client.bds.get_wallet_portfolio(wallet.wallet_address)
        print(f"DEBUG: Portfolio response: {portfolio_response}")

        all_users_tokens = portfolio_response.get("data", {}).get("items", [])
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
            token_address = token.get("address")
            print(f"DEBUG: Checking token {tokens_checked}/{len(all_users_tokens)}: {token_address}")

            token_overview = client.bds.get_token_overview(token_address)
            print(f"DEBUG: Token overview response: {token_overview}")

            if not token_overview.get("success"):
                print(f"DEBUG: Failed to get token data for {token_address}: {token_overview.get('error')}")
                logger.error(f"Failed to get token data for {token_address}: {token_overview.get('error')}")
                continue

            token_overview_data = token_overview.get("data", {})
            price_change_5m = token_overview_data.get("priceChange5mPercent", 0)

            print(f"DEBUG: Token {token_address} - Price change 5m: {price_change_5m}%, Threshold: {price_watch.threshold}%")
            logger.info(f"Token {token_address} - Price change: {price_change_5m}%, Threshold: {price_watch.threshold}%")

            if price_change_5m > price_watch.threshold:
                print(f"DEBUG: Token {token_address} meets threshold! Getting additional data...")

                token_creation_info = client.bds.get_token_creation_info(token_address)
                if not token_creation_info.get("success"):
                    token_creation_time = "-"
                else:
                    token_creation_time = token_creation_info.get("data", {}).get("blockHumanTime", "-") if token_creation_info.get("data") else "-"

                security_info = client.bds.get_token_security(token_address)
                if not security_info.get("success"):
                    print(f"DEBUG: Failed to get security info for {token_address}")
                    no_mint = None
                    blacklist_safe = None
                else:
                    security_data = security_info.get("data", {})
                    no_mint = security_data.get("ownerOfOwnerAddress") == "11111111111111111111111111111111"
                    non_transferable = bool(security_data.get("nonTransferable"))
                    blacklist_safe = not non_transferable

                total_supply = token_overview_data.get("totalSupply", 1)

                top_10_holders = client.bds.get_token_holders(token_address)
                top_10_holders_data = top_10_holders.get("data", {}).get("items", [])
                top_10_holders_pct = [item.get("ui_amount", 0) / total_supply * 100 for item in top_10_holders_data]
                top_10_holders_pct_str = [f"{pct:.2f}%" for pct in top_10_holders_pct]
                top_10_holders_pct_str_formatted = " | ".join(top_10_holders_pct_str)

                formatted_response = build_token_card(
                    token,
                    token_overview_data,
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


def _pct(x, decimals=2):
    try:
        return f"{float(x):.{decimals}f}%"
    except Exception:
        return "-"


def build_token_card(
    token,
    token_overview_data,
    token_creation_time,
    no_mint=None,
    blacklist_safe=None,  # bool | None (from token_security)
    top_10_holders_pct_str_formatted=None,  # list[float] (each already in %), optional
    chain="Solana",
):
    # Pull what you already computed in your snippet
    liquidity = token_overview_data.get("liquidity", 0)
    price = token_overview_data.get("price", 0)
    token_symbol = token_overview_data.get("symbol", "Unknown")
    market_cap = token_overview_data.get("marketCap", 0)
    price_change_5m = token_overview_data.get("priceChange5mPercent", 0)

    # Header
    addr = token.get("address", "—")
    header_left = f"${token_symbol} – {chain}"
    header = f"{header_left}\n{addr}"

    # Lines matching the original bot
    # Create
    line_info_create = f"Create: {token_creation_time}"

    # MC, Liq, Price
    line_info_mc = f"MC: {_fmt_usd(market_cap)}"
    line_info_liq = f"Liq: {_fmt_usd(liquidity)}"
    line_info_px = f"Price: {_fmt_price_with_zeroes(price)} ({price_change_5m:+.2f}%)"

    # Security
    line_sec = f"NoMint {_yn(no_mint)}, Blacklist {_yn(blacklist_safe)}"

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
