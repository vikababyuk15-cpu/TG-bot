# TG-bot
Telegram Broadcast &amp; Scheduler Bot

# Telegram Broadcast & Scheduler Bot

A Python-based Telegram bot designed to automate mass messaging across multiple channels and groups simultaneously. This tool simplifies the process of sending scheduled updates and template-based notifications.

## Key Features
* **Mass Broadcasting:** Send a single message to all connected chats with one command.
* **Template System:** Use predefined message templates for consistent planning and updates.
* **Multi-Chat Support:** Automatically manages distribution across all groups where the bot is an administrator.
* **Access Control:** Restricted admin panel to ensure only authorized users can trigger broadcasts.

## Tech Stack
* **Language:** Python 3.x
* **Framework:** aiogram (Asynchronous Telegram Bot API)
* **Storage:** (e.g., SQLite/JSON for storing Chat IDs)
* **Environment:** python-dotenv for secure token management

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [link to repo]
   
   Install dependencies:
   pip install -r requirements.txt

   Configure Environment Variables:
   BOT_TOKEN=your_token_here
   ADMIN_ID=your_telegram_id

   ## Quick Push Guide (English Commands)

If you are in your terminal and ready to upload the code, follow these steps:

1.  **Stage your changes:**
    `git add .`
2.  **Commit with a clear message:**
    `git commit -m "feat: add broadcasting logic and readme"`
3.  **Push to GitHub:**
    `git push origin main`

**Pro-tip:** Since you’re focusing on **backend logic**, having a clean `README` like this shows you care about how the system works under the hood, not just the code itself!

Enjoy! :)
