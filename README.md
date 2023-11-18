# bot_ai_ventures
This is a bot to register for AI ventures in the Imperial College internal website.

Usage : python3 main.py <time_out in seconds> <username> <plain text password>

Features:
- Uses selenium to crawl through pre determined webpage to register for given course.
- Has timeouts in the event of receiving API errors such as for error 429.
- Automatic exit upon successful registration.

Possible improvements:
- encrypting plain text password in API request.
- More robust method of detecting places to click.


