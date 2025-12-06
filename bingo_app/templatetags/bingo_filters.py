from django import template
import re
from urllib.parse import urlparse, urlencode

register = template.Library()

@register.filter(name='get_embed_url')
def get_embed_url(video_url):
    if not video_url:
        return ""
    
    # Regex for YouTube URLs (handles youtu.be, youtube.com, youtube-nocookie.com, and YouTube Shorts)
    # Improved regex to capture video ID from various YouTube URL formats
    youtube_regex = (
        r'(?:https?://)?(?:www\.)?'
        r'(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/|youtube-nocookie\.com/embed/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    
    youtube_match = re.search(youtube_regex, video_url)
    if youtube_match:
        video_id = youtube_match.group(1)
        # Build embed URL with necessary parameters
        # Using youtube.com/embed instead of youtube-nocookie.com for better compatibility
        # Note: origin parameter removed as it causes "checking your connection" error
        params = {
            'enablejsapi': '1',
            'rel': '0',  # Don't show related videos
            'modestbranding': '1',  # Reduce YouTube branding
            'playsinline': '1',  # Important for mobile devices
            'autoplay': '0',  # Don't autoplay (better UX)
            'mute': '0',  # Don't mute by default
        }
        return f"https://www.youtube.com/embed/{video_id}?{urlencode(params)}"

    # Regex for Vimeo URLs
    vimeo_regex = r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)'
    vimeo_match = re.search(vimeo_regex, video_url)
    if vimeo_match:
        video_id = vimeo_match.group(1)
        return f"https://player.vimeo.com/video/{video_id}"
        
    return video_url # Fallback for other video URLs

@register.filter
def is_player_in_game(user, game):
    if not user.is_authenticated:
        return False
    return game.player_set.filter(user=user).exists()

@register.filter
def get_item(value, index):
    try:
        return value[index]
    except (TypeError, IndexError, KeyError):
        return None

@register.simple_tag
def get_pattern_mask(game):
    """Return a 5x5 matrix marking the required cells for the current winning pattern."""
    size = 5
    mask = [[0 for _ in range(size)] for _ in range(size)]
    if not game:
        return mask

    pattern = getattr(game, "winning_pattern", None)
    if pattern == "FULL":
        return [[1 for _ in range(size)] for _ in range(size)]
    if pattern == "HORIZONTAL":
        for col in range(size):
            mask[size // 2][col] = 1
        return mask
    if pattern == "VERTICAL":
        for row in range(size):
            mask[row][size // 2] = 1
        return mask
    if pattern == "DIAGONAL":
        for i in range(size):
            mask[i][i] = 1
            mask[i][size - 1 - i] = 1
        return mask
    if pattern == "CORNERS":
        mask[0][0] = mask[0][size - 1] = mask[size - 1][0] = mask[size - 1][size - 1] = 1
        return mask
    if pattern == "CUSTOM":
        custom_pattern = getattr(game, "custom_pattern", None)
        if custom_pattern:
            for row_index in range(min(size, len(custom_pattern))):
                row = custom_pattern[row_index]
                for col_index in range(min(size, len(row))):
                    mask[row_index][col_index] = 1 if row[col_index] == 1 else 0
    return mask
