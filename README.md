![enter image description here](https://cdn.discordapp.com/attachments/664881386011885568/1434172265280573532/logo_large.png?ex=69075c81&is=69060b01&hm=bf98838d08700bd9c9eccf22b8a8f99c18aec235f1208b6c75d9bde5747b31ba&)
The **Telepad** service isn’t hosted permanently and may occasionally be offline — this is a non-commercial project. Check the `uptime` badge for the current server status.

![Uptime Robot status](https://img.shields.io/uptimerobot/status/m801711046-3d4b109226cdcfdc2846fc84?up_message=ONLINE&down_message=OFFLINE&style=for-the-badge&logo=docker&logoColor=white)


# Overview
**Telepad** is a Telegram-integrated soundboard web app that lets you send custom voice messages. Authentication is handled via Telegram, so anyone using it may sign in instantly and access the full feature set. Telepad is composed of two main parts: the [web panel itself](https://telepad.cc) and the Telegram bot — *@tlpadbot*.

# Features
- Upload any media file from your device.
- Download media from many sites using [yt-dlp](https://github.com/yt-dlp/yt-dlp) (supported sites are listed [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)).
- No format worries — uploaded media are converted automatically.
- Type *@tlpadbot* in any Telegram chat to send sounds from your library.
- Make sounds private or public.
- Add tags to your sounds or filter the global library by tags when searching.

# Future plans
- Deeper bot and API integration to allow uploading and downloading sounds directly via the bot.
- Add the sound trimming feature.

# Technologies used in the API

| Technology | Purpose |
|-------------|----------|
| **Python** | Core programming language |
| **Django + Django Packages** | Web framework foundation |
| **Django REST Framework** | Building and managing the API |
| **PostgreSQL** | Database |
| **Celery** | Background task processing |
| **Redis** | Message broker for Celery |
| **yt-dlp** | Universal media downloader library |
| **FFmpeg** | Media processing and conversion |
| **Gunicorn** | WSGI server for running the API |
| **Nginx** | Reverse proxy and static file server |
| **Cloudflared Tunnel** | Exposing the server to the web |
| **python-telegram-bot** | Interface for the Telegram Bot API |
| **Docker** | Containerization platform |
| **Docker Compose** | Service orchestration and management |


