#Song class to be put into the playlist
import datetime
import discord

class Song:
    def __init__(
        self, 
        origin, 
        host, 
        base_url=None, 
        uploader=None, 
        title=None, 
        duration=None, 
        page_url=None, 
        thumbnail=None,
        embed_color=0x000000,
        songinfo_uploader="Uploader",
        songinfo_duration="Duration",
        songinfo_unknown_duration="Unknown"
    ):
        self.host = host
        self.origin = origin
        self.base_url = base_url
        self.embed_color = embed_color
        self.songinfo_uploader = songinfo_uploader
        self.songinfo_duration = songinfo_duration
        self.songinfo_unknown_duration = songinfo_unknown_duration
        self.info = self.Songinfo(uploader, title, duration, page_url, thumbnail, self)

    class Songinfo:
        def __init__(self, uploader, title, duration, page_url, thumbnail, parent):
            self.uploader = uploader
            self.title = title
            self.duration = duration
            self.page_url = page_url
            self.thumbnail = thumbnail
            self.output = ""
            self.parent = parent  # Reference to outer Song instance

        def format_output(self, playtype):
            """Return a nicely formatted Discord embed for the song."""
            embed = discord.Embed(
                title=playtype,
                description=f"[{self.title}]({self.webpage_url})",
                color=self.parent.embed_color
            )

            if self.thumbnail:
                embed.set_thumbnail(url=self.thumbnail)

            embed.add_field(
                name=self.parent.songinfo_uploader,
                value=self.uploader or "Unknown",
                inline=False
            )

            if self.duration is not None:
                duration_str = str(datetime.timedelta(seconds=self.duration))
            else:
                duration_str = self.parent.songinfo_unknown_duration

            embed.add_field(
                name=self.parent.songinfo_duration,
                value=duration_str,
                inline=False
            )

            return embed


