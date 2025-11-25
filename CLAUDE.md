# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BlogDex blog grade scraper that automates browser interactions to collect blog rating information from blogdex.space. The project uses undetected-chromedriver to bypass bot detection and requires manual Google 2FA completion.

## Essential Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with Google credentials
```

### Running the Scraper
```bash
# Interactive mode (up to 17 searches per session)
python open_blogdex.py

# Single URL mode
python open_blogdex.py <blog_url>

# Example
python open_blogdex.py https://blog.naver.com/nightd/224041403656
```

### Dependencies
- `selenium==4.15.2` - Browser automation
- `undetected-chromedriver==3.5.4` - Bot detection bypass
- `webdriver-manager==4.0.1` - ChromeDriver management
- `python-dotenv==1.0.0` - Environment variable handling

## Core Architecture

### Authentication Flow
1. **Auto-navigate** to BlogDex login → Google OAuth flow
2. **Auto-input** Google email address
3. **Manual intervention** (60 seconds) for password + 2FA completion
4. **Auto-save** session cookies to `cookies.json` for future sessions
5. **Cookie reuse** eliminates need for repeated logins

**Critical constraint**: Google detects automated tools and blocks full automation. The hybrid approach (auto email + manual password/2FA) is the most reliable solution.

### Scraping Workflow
1. Navigate to blogdex.space
2. Handle popup dismissal (multiple fallback methods)
3. Complete Google OAuth (hybrid auto/manual)
4. For each blog URL:
   - Return to BlogDex home
   - Input blog URL into search field (character-by-character for human-like behavior)
   - Extract grade data from SVG element
   - Save to timestamped individual JSON file
5. Limit: 17 searches per session

### Bot Detection Avoidance
- **undetected-chromedriver**: Primary tool for Cloudflare/bot detection bypass
- **Progressive delays**: 2-5 second waits between actions
- **Character-by-character input**: Simulates human typing with 0.1s intervals
- **Mouse movement simulation**: Random offset movements during login
- **Multiple selector fallbacks**: Graceful degradation if elements change

### Data Storage
- **Individual JSON files**: `data/json_results/{blog_id}_grade_{timestamp}.json`
- **Timestamped format**: `YYYYMMDD_HHMMSS` for chronological sorting
- **Metadata included**: blog_url, grade, timestamp
- **No aggregation**: Each scrape creates a new file (historical tracking)

```json
{
  "blog_url": "https://blog.naver.com/example",
  "grade": "준최2",
  "timestamp": "2025-10-16 15:19:40"
}
```

## Key Technical Details

### CSS Selectors
The script relies on specific CSS selectors for BlogDex elements. Key selectors:
- Login popup close: `#radix-\:r12\: > div.relative > ...`
- URL input field: `#__next > div > main > section... > input`
- Grade SVG element: `#__next > div > main > div > ... > svg > text:nth-child(2)`

**Note**: These selectors may break if BlogDex updates their UI. Use browser DevTools to identify new selectors.

### Element Interaction Strategy
1. **WebDriverWait**: 10-15 second timeouts for element presence
2. **Multiple fallback methods**: Try different selectors/approaches
3. **JavaScript fallback**: Use `driver.execute_script()` if normal clicks fail
4. **Keyboard alternatives**: ESC key, RETURN key as last resort

### Human-like Behavior Patterns
- **Typing delays**: 0.1s between characters
- **Action delays**: 2-5s between major actions (clicks, navigation)
- **Mouse movements**: Random offset movements during sensitive operations
- **Progressive waits**: Longer waits after authentication steps (3-8s)

### Session Limits
- **17 searches maximum**: Hard limit per browser session
- **Reason**: Prevents rate limiting/account restrictions
- **Workaround**: Restart script for additional searches (reuses cookies)

## Important Constraints

### Google Authentication
- **Cannot fully automate**: Google actively blocks automation tools
- **Email input**: Automated successfully
- **Password + 2FA**: Requires manual completion within 60 seconds
- **Alternative approaches**: All tested and failed (Stealth plugins, undetected-chromedriver alone)
- **Cookie persistence**: First login enables future automatic authentication

### Error Handling
- **Timeouts**: Script uses 10-15s waits before failing
- **Selector failures**: Multiple fallback strategies implemented
- **Manual fallback**: Prompts user input if automation fails
- **Browser persistence**: Browser stays open for debugging on errors

## Environment Variables

Required in `.env`:
```env
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password
```

Optional (currently hardcoded):
```env
WAIT_TIME=10
TWO_FACTOR_WAIT_TIME=60
HEADLESS=false
```

## File Structure Context

```
블랜크/
├── open_blogdex.py               # Main scraper (primary script)
├── blogdex_selenium_login.py    # Alternative implementation
├── requirements.txt              # Python dependencies
├── .env                         # Credentials (gitignored)
├── .env.example                 # Environment variable template
├── cookies.json                 # Session cookies (auto-generated, gitignored)
└── data/
    └── json_results/            # Individual JSON outputs
        └── {blog_id}_grade_{timestamp}.json
```

## Development Notes

### When Modifying Selectors
1. Open blogdex.space in Chrome
2. Use DevTools (F12) → Inspect element
3. Right-click element → Copy → Copy selector
4. Test selector in console: `document.querySelector('[selector]')`
5. Update selector strings in `open_blogdex.py`

### Adding New Features
- **Extend process_blog_loop()**: For additional scraping logic
- **Modify extract_blog_grade()**: For different data extraction
- **Update save_individual_json()**: For alternative storage formats

### Testing Without Full Flow
- Comment out login sections to test scraping only
- Use existing `cookies.json` to skip authentication
- Reduce `MAX_SEARCHES = 1` for quick tests
