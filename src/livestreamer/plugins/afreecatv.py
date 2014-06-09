import re

from livestreamer.plugin import Plugin
from livestreamer.plugin.api import http
from livestreamer.stream import HLSStream

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 "
    "(KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
)
HEADERS = {"User-Agent": USER_AGENT}
PLAYLIST_URL = "http://m.afreeca.com/live/stream/a/hls/broad_no/{0}"
CHANNEL_URL = "http://afbbs.afreeca.com:8080/api/video/get_bj_liveinfo.php"

_broadcast_re = re.compile(r".+\/(\d+)\.gif")
_url_re = re.compile("http(s)?://(\w+\.)?afreeca.com/(?P<username>\w+)")


class AfreecaTV(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _find_broadcast(self, username):
        res = http.get(CHANNEL_URL, headers=HEADERS, params=dict(szBjId=username))
        liveinfo = http.xml(res)
        thumb = liveinfo.findtext("thumb")
        if not thumb:
            return

        match = _broadcast_re.match(thumb)
        if match:
            return match.group(1)

    def _get_streams(self):
        match = _url_re.match(self.url)
        if not match:
            return

        username = match.group("username")
        broadcast = self._find_broadcast(username)
        if not broadcast:
            return

        playlist_url = PLAYLIST_URL.format(broadcast)
        return HLSStream.parse_variant_playlist(self.session, playlist_url,
                                                headers=HEADERS)

__plugin__ = AfreecaTV
