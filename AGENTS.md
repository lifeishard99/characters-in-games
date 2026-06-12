# Information

The purpose of this project is to fetch media for characters in video-games.

This chore is tedious and time-consuming, so it's a good candidate for automation/assistance from agents.

The media is vital in our research around video-game characters.

## Media folder

The media is stored in the [media](media/) folder (git ignored).

# Plan

- [x] Fetch media for female characters in the game Marvel Rivals.
  - Character game screens.
  - Fan art images (especially sensual ones).
- [x] Fetch NSFW fan art for female characters in Marvel Rivals.
  - Focus on explicit/adult fan art.
  - Store in `media/marvel-rivals/{character}/fan-art-nsfw/`.

## Execution of plan

- You should git commit and push regularly, particularly after making many code changes.
- After every step you should tick the step off the plan and make sure everything is committed and pushed.
- Be autonomous, but if you need my input then ask for it in [QA.md](QA.md).

# The docs folder

[docs](docs/) may contain useful resources for agents when executing tasks.

- [plans](docs/plans/): long lasting plans with descriptions, implementation details and checklists.

# How media is fetched

- Uses `download_media.py` — a Python script that searches Bing Images and downloads results.
- Characters are listed in `characters.json`.
- Images are saved to `media/marvel-rivals/{character}/{category}/`.
- Dependencies: `pip install -r requirements.txt` (requests, beautifulsoup4, Pillow).
- The script includes rate limiting to avoid being blocked.

# AI-generated commit messages

When generating a commit message then follow these rules:

- follow the rules for conventional commits.
  - `fix` for changes in behavior
  - `refactor` when having rewritten code and does not change behavior.
  - `docs` when only documentation has changed.
  - `chore` for other things not affecting behavior in the application.
  - when updating dependencies then use `fix(deps)` for changes in production dependencies (`dependencies` in [package.json](package.json)) and use `chore(deps)` for changes in development dependencies (`devDependencies` in [package.json](package.json)).
- keep the commit message short and concise
- follow the pattern from existing commit messages.
