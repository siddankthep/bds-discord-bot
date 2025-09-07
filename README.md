# SOL Discord Alert Bot

A discord bot that pulls data for Solana and alert the user if a token price changes above a specific threshold

# Project Setup

## Install uv

https://docs.astral.sh/uv/getting-started/installation/

## Dependencies

Run

```bash
uv sync
```

and all dependencies included in `pyproject.toml` will be installed.

# Major Components

## Database (Supabase Postgresql)

- User's Wallet Address
- User's desired threshold

## Chain Data

- All the requests needed
- Pydantic Data Models

# Discord Bot

- Get User's wallet address and gather all of the token in the wallet
- Get token info and price change
- If price change meets threshold, send alert to user (manually)
