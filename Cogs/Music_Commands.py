import discord
import asyncio
import requests
import secret
from discord import FFmpegPCMAudio, app_commands
from yt_dlp import YoutubeDL

music_queues = {}
main_event_loop = asyncio.new_event_loop()

ydl_opts_browse = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "extract_flat": "in_playlist",
}
browse_ydl = YoutubeDL(ydl_opts_browse)

class MusicGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="music")
        self.currently_processing = False
        self.playlist_cache = {}

    async def ensure_voice(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return False

        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()
        elif interaction.guild.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message("❌ I'm already in another voice channel!", ephemeral=True)
            return False

        return True

    async def get_spotify_metadata(self, spotify_url: str):
        try:
            auth_url = "https://accounts.spotify.com/api/token"
            auth_response = requests.post(
                auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": secret.SPOTIFY_CLIENT_ID,
                    "client_secret": secret.SPOTIFY_CLIENT_SECRET,
                },
            )
            auth_data = auth_response.json()
            access_token = auth_data["access_token"]

            if "track" in spotify_url:
                spotify_id = spotify_url.split("track/")[-1].split("?")[0]
                endpoint = f"tracks/{spotify_id}"
            elif "album" in spotify_url:
                spotify_id = spotify_url.split("album/")[-1].split("?")[0]
                endpoint = f"albums/{spotify_id}/tracks"
            elif "playlist" in spotify_url:
                spotify_id = spotify_url.split("playlist/")[-1].split("?")[0]
                endpoint = f"playlists/{spotify_id}/tracks"
            else:
                return None

            headers = {"Authorization": f"Bearer {access_token}"}
            api_url = f"https://api.spotify.com/v1/{endpoint}"
            response = requests.get(api_url, headers=headers)
            data = response.json()

            tracks = []
            if "tracks" in data:
                if "items" in data["tracks"]:
                    items = data["tracks"]["items"]
                else:
                    items = [data]
            elif "items" in data:
                items = data["items"]
            else:
                items = [data]

            for item in items:
                track = item["track"] if "track" in item else item
                if not track:
                    continue
                tracks.append({
                    "title": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"] if "album" in track else "Unknown Album",
                })

            return tracks

        except Exception as e:
            print(f"❌ Spotify API Error: {e}")
            return None

    async def search_youtube(self, query: str):
        try:
            result = await asyncio.to_thread(browse_ydl.extract_info, f"ytsearch:{query}", download=False)
            if result and "entries" in result:
                return result["entries"][0]["url"]
        except Exception as e:
            print(f"❌ YouTube search failed: {e}")
        return None

    async def search_soundcloud(self, query: str):
        try:
            result = await asyncio.to_thread(browse_ydl.extract_info, f"scsearch:{query}", download=False)
            if result and "entries" in result:
                return result["entries"][0]["url"]
        except Exception as e:
            print(f"❌ SoundCloud search failed: {e}")
        return None

    async def process_playlist(self, interaction: discord.Interaction, url: str, is_spotify: bool = False):
        guild_id = interaction.guild.id
        music_queues.setdefault(guild_id, asyncio.Queue())

        if is_spotify:
            tracks = await self.get_spotify_metadata(url)
            if not tracks:
                await interaction.followup.send("❌ Could not fetch Spotify tracks.", ephemeral=True)
                return

            await interaction.followup.send(f"🎵 Adding {len(tracks)} Spotify tracks to queue...")
            
            # Store playlist in cache for proper continuation
            self.playlist_cache[guild_id] = {
                "tracks": tracks,
                "current_index": 0,
                "source": "spotify"
            }
            
            # Process first few tracks immediately
            for track in tracks[:3]:
                query = f"{track['title']} {track['artist']}"
                yt_url = await self.search_youtube(query) or await self.search_soundcloud(query)
                if yt_url:
                    await self.add_single_track(interaction, yt_url, is_playlist=True)
                else:
                    await interaction.followup.send(f"❌ Could not find: **{query}**", ephemeral=True)
            return

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "extract_flat": False,
                "noplaylist": False,
                "extractor_args": {"youtube": {"player_skip": ["js"]}},
                "http_headers": {"User-Agent": "Mozilla/5.0"},
            }

            info = await asyncio.to_thread(YoutubeDL(ydl_opts).extract_info, url, download=False)
            if "entries" in info:
                playlist_name = info.get("title", "Unknown Playlist")
                await interaction.followup.send(f"🎵 Adding playlist: **{playlist_name}** ({len(info['entries'])} tracks).")
                
                # Store playlist in cache for proper continuation
                self.playlist_cache[guild_id] = {
                    "entries": info["entries"],
                    "current_index": 0,
                    "source": "youtube"
                }
                
                # Process first few tracks immediately
                for entry in info["entries"][:3]:
                    await self.add_single_track(interaction, entry["url"], is_playlist=True)
            else:
                await self.add_single_track(interaction, url)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    async def add_single_track(self, interaction: discord.Interaction, url: str, is_playlist: bool = False):
        guild_id = interaction.guild.id
        music_queues.setdefault(guild_id, asyncio.Queue())

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": False,
            "noplaylist": True,
        }

        try:
            info = await asyncio.to_thread(YoutubeDL(ydl_opts).extract_info, url, download=False)
            await music_queues[guild_id].put({
                "url": info["url"],
                "title": info.get("title", "Unknown Track"),
                "author": info.get("uploader", "Unknown Artist"),
                "guild_id": guild_id
            })

            if not is_playlist:
                await interaction.followup.send(f"🎶 Added to queue: **{info['title']}**.")

            if not interaction.guild.voice_client.is_playing():
                await self.play_next_in_queue(interaction.guild)

        except Exception as e:
            await interaction.followup.send(f"❌ Error processing track: {e}", ephemeral=True)

    async def continue_playlist(self, guild: discord.Guild):
        guild_id = guild.id
        if guild_id not in self.playlist_cache:
            return

        playlist_data = self.playlist_cache[guild_id]
        
        if playlist_data["source"] == "spotify":
            tracks = playlist_data["tracks"]
            current_index = playlist_data["current_index"]
            
            # Process next 3 tracks
            for track in tracks[current_index:current_index+3]:
                query = f"{track['title']} {track['artist']}"
                yt_url = await self.search_youtube(query) or await self.search_soundcloud(query)
                if yt_url:
                    await music_queues[guild_id].put({
                        "url": yt_url,
                        "title": track["title"],
                        "author": track["artist"],
                        "guild_id": guild_id
                    })
            
            playlist_data["current_index"] = min(current_index + 3, len(tracks))
            
        elif playlist_data["source"] == "youtube":
            entries = playlist_data["entries"]
            current_index = playlist_data["current_index"]
            
            # Process next 3 tracks
            for entry in entries[current_index:current_index+3]:
                await music_queues[guild_id].put({
                    "url": entry["url"],
                    "title": entry.get("title", "Unknown Track"),
                    "author": entry.get("uploader", "Unknown Artist"),
                    "guild_id": guild_id
                })
            
            playlist_data["current_index"] = min(current_index + 3, len(entries))

    async def play_next_in_queue(self, guild: discord.Guild):
        guild_id = guild.id
        
        # Continue playlist if we're at the end of the current batch
        if guild_id in self.playlist_cache:
            playlist_data = self.playlist_cache[guild_id]
            if playlist_data["current_index"] < len(playlist_data["tracks" if playlist_data["source"] == "spotify" else "entries"]):
                await self.continue_playlist(guild)

        if guild_id not in music_queues or music_queues[guild_id].empty():
            return

        next_song = await music_queues[guild_id].get()
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "extract_flat": False,
            }

            info = await asyncio.to_thread(YoutubeDL(ydl_opts).extract_info, next_song["url"], download=False)
            audio_url = info["url"]

            source = FFmpegPCMAudio(
                audio_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn",
            )

            def after_play(error):
                if error:
                    print(f"Playback error: {error}")
                asyncio.run_coroutine_threadsafe(self.play_next_in_queue(guild), main_event_loop)

            guild.voice_client.play(source, after=after_play)

            channel = discord.utils.get(guild.text_channels, name="music")
            if channel:
                await channel.send(f"🎵 Now playing: **{next_song['title']}**")

        except Exception as e:
            print(f"❌ Playback error: {e}")
            await self.play_next_in_queue(guild)

    @app_commands.command(name="play", description="Play a song or playlist")
    @app_commands.describe(url="YouTube, SoundCloud, or Spotify URL")
    async def music_play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        if not await self.ensure_voice(interaction):
            return

        if self.currently_processing:
            await interaction.followup.send("🔄 Already processing a playlist, please wait...")
            return

        if "spotify.com" in url:
            self.currently_processing = True
            try:
                await self.process_playlist(interaction, url, is_spotify=True)
            finally:
                self.currently_processing = False
            return

        is_playlist = "playlist" in url or "album" in url
        if is_playlist:
            self.currently_processing = True
            try:
                await self.process_playlist(interaction, url)
            finally:
                self.currently_processing = False
        else:
            await self.add_single_track(interaction, url)

    @app_commands.command(name="skip", description="Skip the current song")
    async def music_skip(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return

        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped!")
        await self.play_next_in_queue(interaction.guild)

    @app_commands.command(name="stop", description="Stop playback and clear the queue")
    async def music_stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in music_queues:
            music_queues[guild_id] = asyncio.Queue()
        
        if guild_id in self.playlist_cache:
            del self.playlist_cache[guild_id]

        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()

        await interaction.response.send_message("🛑 Stopped playback and cleared queue.")

    @app_commands.command(name="queue", description="Show the current queue")
    async def music_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in music_queues or music_queues[guild_id].empty():
            await interaction.response.send_message("🎶 Queue is empty.", ephemeral=True)
            return

        queue_list = list(music_queues[guild_id]._queue)
        embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)

        for i, song in enumerate(queue_list[:10], 1):
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"by {song['author']}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    bot.tree.add_command(MusicGroup())