import os


# Path to directory we will browse recursively to find all .wav
dir_path = r"D:\Media\Musique\Rekordbox\Tracks"


def get_wav(dir_path: str) -> list[str]:
    """Return list with .wav files pathes."""

    tracks_wav = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file[-4:] == ".wav":
                tracks_wav.append(rf"{root}{os.sep}{file}")
    return tracks_wav


def get_unsupported(tracks_wav: list[str]) -> list[str]:
    """Return all unsupported files in list of .wav files."""

    unsupported_tracks = []
    for track in tracks_wav:
        with open(track, "rb") as f:
            content = f.read(22)
            if content[-2:] == b"\xfe\xff":
                unsupported_tracks.append(track)
                print(f"To fix: {track}")
    return unsupported_tracks


def fix_unspported(unsupported_tracks: list[str]) -> None:
    """Fix given tracks."""

    for track in unsupported_tracks:
        with open(track, "rb") as f:
            content = list(f.read())
        content[20] = 0x01
        content[21] = 0x00
        with open(track, "wb") as f:
            f.write(bytes(content))
            print(f"Fixed: {track}")


wav = get_wav(dir_path)
print(f"Found {len(wav)} WAV files")
uns = get_unsupported(wav)
print(f"Found {len(uns)} unsupported WAV files")
# fix_unspported(uns)
