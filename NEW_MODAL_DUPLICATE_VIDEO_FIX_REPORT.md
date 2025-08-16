# New Skool Modal Player & Duplicate Video Fix Report

## Summary
- **Issue**: On communities using Skool’s new modal/popup video player, lessons sometimes received a duplicate/cached video URL from other lessons, or no video at all.
- **Root Cause**: State contamination (cookies/storage) and extraction paths not consistently validating/cleaning URLs when the real player only loads after opening a modal.
- **Fix**: Added modal-aware extraction (detect video URLs inside dialogs after safe thumbnail click), enforced stricter state isolation, and ensured URL cleaning/validation on all paths.

## Symptoms Observed
- Same YouTube ID appearing across unrelated lessons (cached bleed-through)
- “No video found” despite visible video thumbnail with magnifying glass cursor
- Post-click iframes only appear after modal interaction

## Technical Root Causes
- Modal-based player: iframe/video only exists after clicking a thumbnail (dialog opens)
- Inconsistent validation/cleaning across extraction paths
- Browser/session artifacts between lessons causing bleed-through

## Changes Implemented
- Modal-aware extraction step:
  - Detects thumbnails → opens modal → searches dialog for iframe/video/data attributes
  - Cleans URLs (YouTube embed → watch; Loom embed → share)
- State isolation helper:
  - Clear cookies, `localStorage`, `sessionStorage` when needed to avoid contamination
- Stronger validation:
  - Ensure cleaned URL passes through the same checks regardless of extraction method

## Code Touchpoints
- `extract_single_with_youtube_fix.py`
  - Added `extract_video_from_modal_if_open()` and integrated into post-click detection
  - Added `clear_browser_storage()` utility (cookies + storage)
  - Enhanced custom-player detection and canonical URL conversion (YouTube/Loom)

## Verification Results
- Lesson (modal → Loom):
  - Input: `https://www.skool.com/new-society/v56-persistent-images-chat-histories-2`
  - Output: `https://www.loom.com/share/4fc7319a691343ca89d5ea56d0d7640b`
- Lesson (modal → YouTube):
  - Input: `https://www.skool.com/new-society/classroom/5d7e39c5?md=073c596a86314c3eb20df3e0753fe592`
  - Output: `https://www.youtube.com/watch?v=dV5jUmGe-s8`

## Operational Notes
- If a click redirects to a lesson-specific path, continue detection on the redirected page.
- Prefer modal dialog scanning first after thumbnail click; then global selectors.
- Always canonicalize/clean URLs before saving or downloading.

## Impact
- Eliminates duplicate/cached video bleed-through in modal communities
- Recovers video URLs that previously required manual intervention
- Maintains compatibility with non-modal communities

## Next Steps
- Port modal extraction + state isolation to `skool_content_extractor.py` (batch)
- Add per-run duplicate-ID guard for batch mode
- Expand modal selectors for other Skool layouts

---
- Created: 2025-08-08
- Status: Applied to single-lesson extractor; verification successful

