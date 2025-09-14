from typing import Optional
from dotenv import load_dotenv
import os
import discord
from discord.ext import tasks
from src.sol_data.data_models import TokenOverviewResponse, WalletPortfolioItem
from src.db.database import DatabaseConnection
from src.sol_data.data_manager import DataManager, DataManagerAPIError
from src.discord.logger import handler, logger

load_dotenv()

WRAPPED_TOKENS = {"SOL": "So11111111111111111111111111111111111111112", "ETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"}

intents = discord.Intents.default()
intents.message_content = True


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.db = DatabaseConnection()
        self.dm = DataManager()

    async def setup_hook(self) -> None:
        await self.tree.sync()
        # Start the automatic alert checking task
        automatic_alerts.start()


client = MyClient(intents=intents)


@client.event
async def on_ready():
    logger.info(f"Logged in as user {client.user} with ID {client.user.id}")


@tasks.loop(minutes=5)
async def automatic_alerts():
    """Background task that runs every 5 minutes to check alerts for all users"""
    logger.info("Starting automatic alert check for all users")

    try:
        # Get all users with both wallet and threshold configured
        users_with_settings = client.db.get_all_users_with_settings()
        logger.info(f"Found {len(users_with_settings)} users to check")

        for discord_id, wallet_address, threshold in users_with_settings:
            try:
                logger.info(f"Checking alerts for user {discord_id}")

                # Get alerts for this user
                tokens_meeting_threshold = await check_user_alerts(discord_id, wallet_address, threshold)

                if tokens_meeting_threshold:
                    # Get the Discord user object
                    user = await client.fetch_user(discord_id)
                    if user:
                        try:
                            # Send alerts via DM
                            await user.send(
                                f"🚨 **Price Alert!** Found {len(tokens_meeting_threshold)} tokens that meet your {threshold}% threshold:"
                            )
                            for token_card in tokens_meeting_threshold:
                                await user.send(token_card)
                            logger.info(f"Sent {len(tokens_meeting_threshold)} alerts to user {discord_id}")
                        except discord.Forbidden:
                            logger.warning(f"Cannot send DM to user {discord_id} - DMs might be disabled")
                        except discord.HTTPException as e:
                            logger.error(f"HTTP error sending DM to user {discord_id}: {e}")
                    else:
                        logger.warning(f"Could not find Discord user with ID {discord_id}")
                else:
                    logger.info(f"No tokens meeting threshold for user {discord_id}")

            except Exception as e:
                logger.error(f"Error checking alerts for user {discord_id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in automatic alerts task: {e}")


@automatic_alerts.before_loop
async def before_automatic_alerts():
    """Wait until the bot is ready before starting the task"""
    await client.wait_until_ready()
    logger.info("Bot is ready, automatic alerts task will start")


@client.tree.command(name="setup", description="Setup user's wallet address and desired threshold")
async def setup_user(interactions: discord.Interaction, wallet_address: str, threshold: float):
    try:
        client.db.upsert_wallet(interactions.user.id, wallet_address)
        logger.info(f"Upserted wallet address for user {interactions.user}!")
        client.db.upsert_price_watch(interactions.user.id, threshold)
        logger.info(f"Upserted wallet threshold for user {interactions.user}!")

        await interactions.response.send_message("Setup complete! Now you can watch over tokens in your wallet!")

    except Exception as e:
        await interactions.response.send_message(f"Error setting up wallet: {e}")


async def check_user_alerts(discord_id: int, wallet_address: str, threshold: float):
    """Check alerts for a single user and return token cards that meet the threshold"""
    try:
        all_users_tokens = client.dm.get_wallet_portfolio(wallet_address).items

        if not all_users_tokens:
            logger.info(f"No tokens found in wallet {wallet_address}")
            return []

        logger.info(f"Checking {len(all_users_tokens)} tokens for user {discord_id} with threshold {threshold}")

        tokens_meeting_threshold = []

        for token in all_users_tokens:
            logger.info(f"Processing token: {token.address}")

            if token.name in WRAPPED_TOKENS:
                token.address = WRAPPED_TOKENS[token.name]

            try:
                token_overview = client.dm.get_token_overview(token.address)
                price_change_5m = token_overview.priceChange5mPercent

                if not price_change_5m:
                    logger.info(f"Price change 5m is not available for {token.address}")
                    continue
            except DataManagerAPIError:
                logger.error("Failed to fetch token overview!")
                continue

            if price_change_5m >= threshold:
                try:
                    creation_info = client.dm.get_token_creation_info(token.address)
                    token_creation_time = creation_info.blockHumanTime
                except DataManagerAPIError:
                    logger.error("Failed to fetch token creation info!")
                    token_creation_time = "-"

                try:
                    security = client.dm.get_token_security(token.address)
                    no_mint = security.ownerOfOwnerAddress == "11111111111111111111111111111111"
                    blacklist = security.fakeToken
                except DataManagerAPIError:
                    logger.error("Failed to fetch token security data!")
                    no_mint = None
                    blacklist = None

                total_supply = token_overview.totalSupply
                try:
                    top_holders = client.dm.get_token_holders(token.address)
                    top_10_holder_str = ""
                    for holder in top_holders.items:
                        top_10_holder_str += f" {holder.ui_amount / total_supply * 100:.2f}%" + " | "

                except DataManagerAPIError:
                    logger.error("Failed to fetch top 10 token holders!")
                    top_10_holder_str = "-" + " | -" * 9

                token_card = build_token_card(token, token_overview, token_creation_time, no_mint, blacklist, top_10_holder_str)

                tokens_meeting_threshold.append(token_card)

        return tokens_meeting_threshold

    except Exception as e:
        logger.error(f"Error occurred while checking alerts for user {discord_id}: {e}")
        return []


@client.tree.command(name="alert", description="Get all tokens alert")
async def alert(interactions: discord.Interaction):
    await interactions.response.defer()

    try:
        discord_id = interactions.user.id
        wallet = client.db.get_wallet(discord_id)
        price_watch = client.db.get_price_watch(discord_id)

        if not wallet or not price_watch:
            await interactions.followup.send("Please setup your wallet and threshold first!")
            return

        tokens_meeting_threshold = await check_user_alerts(discord_id, wallet.wallet_address, price_watch.threshold)

        if not tokens_meeting_threshold:
            await interactions.followup.send(f"No tokens found that met threshold {price_watch.threshold}!")
        else:
            await interactions.followup.send(f"Found {len(tokens_meeting_threshold)} tokens that meets your threshold!")
            for token_card in tokens_meeting_threshold:
                await interactions.followup.send(token_card)
    except Exception as e:
        logger.error(f"Error occurred while getting token alerts: {e}")
        await interactions.followup.send(f"Error occurred while getting token alerts: {e}")


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
    blacklist: Optional[bool] = None,
    top_10_holders_str: str = None,
    chain="Solana",
):
    liquidity = token_overview.liquidity
    price = token_overview.price
    token_symbol = token_overview.symbol or "Unknown"
    market_cap = token_overview.marketCap
    price_change_5m = token_overview.priceChange5mPercent

    # Header
    addr = token.address or "—"
    header_left = f"${token_symbol} – {chain}"
    header = f"{header_left}\n{addr}"

    # Create
    line_info_create = f"Creation Time: {token_creation_time}"

    # MC, Liq, Price
    line_info_mc = f"- MC: {_fmt_usd(market_cap)}"
    line_info_liq = f"Liq: {_fmt_usd(liquidity)}"
    line_info_px = f"Price: {_fmt_price_with_zeroes(price)} ({price_change_5m:+.2f}%)"

    # Security
    line_sec = f"NoMint {_yn(no_mint)} | Blacklist {_yn(blacklist)}"

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
{top_10_holders_str}
"""
    ).strip()

    return card


def run_bot():
    client.run(os.getenv("DISCORD_BOT_TOKEN"), log_handler=handler)
