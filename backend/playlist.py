import random
from collections import deque

class Playlist:
    def __init__(self):
        # Double-ended queues for efficient pops/appends
        self.playlist = deque()
        self.playlist_history = deque()
        self.trackname_history = deque()
        self.max_track_len = 10  # maximum number of history items to store
        self.looping = False

    def get_len(self):
        return len(self.playlist)

    def add_track(self, track):
        """Add a track to the playlist."""
        self.playlist.append(track)
    
    def get_track(self):
        """Return the current track"""
        return self.playlist[0]

    def randomize(self):
        """Randomly shuffle the playlist."""
        temp = list(self.playlist)
        random.shuffle(temp)
        self.playlist = deque(temp)

    def clear_playlist(self):
        """Clear the current playlist and its history."""
        self.playlist.clear()
        self.playlist_history.clear()
        self.trackname_history.clear()

    def add_name(self, name):
        """Keep track of the names of recently played tracks."""
        self.trackname_history.append(name)
        if len(self.trackname_history) > self.max_track_len:
            self.trackname_history.popleft()

    def play_next(self):
        """Play the next track."""
        if not self.playlist:
            return None

        current_track = self.playlist.popleft() 
        self.playlist_history.append(current_track)
        self.add_name(current_track)

        if self.looping:
            self.playlist.append(current_track)

        if len(self.playlist_history) > self.max_track_len:
            self.playlist_history.popleft()

        return current_track

    def play_prev(self):
        """Go back to the previous track (if any)."""
        if not self.playlist_history:
            return None

        prev_track = self.playlist_history.pop()
        self.playlist.appendleft(prev_track)
        return prev_track
