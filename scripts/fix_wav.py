import os


# Paths to directories we will browse recursively to find all .wav
paths = [
    r"D:\Media\Musique\Rekordbox\Tracks",  # Elements
    r"C:\Users\Ewael\Music\PioneerDJ\Imported from Device\Contents",  # Rekordbox
    r"C:\Users\Ewael\Documents\Son\Thomasson\Calage",  # Calage
    r"D:\Contents",  # USB key
]


def get_wav(dir_path: str) -> list[str]:
    """Return list with .wav files paths."""

    tracks_wav = []
    if os.path.exists(dir_path):
        print(f"Searching wav in {dir_path}")
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
        print(f"Fixing {track}")
        with open(track, "rb") as f:
            content = list(f.read())
        content[20] = 0x01
        content[21] = 0x00
        with open(track, "wb") as f:
            f.write(bytes(content))
            print(f"Fixed: {track}")


wav = []
for path in paths:
    wav += get_wav(path)
print(f"Found {len(wav)} WAV files")
uns = get_unsupported(wav)
print(f"Found {len(uns)} unsupported WAV files")
fix_unspported(uns)
