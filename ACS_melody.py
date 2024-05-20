"""Auto-completion Systems: Music helper library

"""
import io

import mido
from python_ta.contracts import check_contracts
import pygame


@check_contracts
class Melody:
    """A class representing a melody.

    Instance Attributes:
    - name: the name of the melody
    - notes: a sequence of notes representing the melody.
        A *note* is a tuple of two integers:
          - the first is an integer between 21 and 108, representing the pitch
          - the second is an integer representing the duration of the note,
            in milliseconds

    Note: you can find a chart showing the conversion between integers and
    standard note names at http://newt.phys.unsw.edu.au/jw/notes.html.

    Representation Invariants:
    - self.name != ''
    - self.notes != []
    - all(21 <= note[0] <= 108 for note in self.notes)
    - all(note[1] > 0 for note in self.notes)
    """
    name: str
    notes: list[tuple[int, int]]

    def __init__(self, name: str, notes: list[tuple[int, int]]) -> None:
        """Initialize a new melody with the given name and notes."""
        self.name = name
        self.notes = notes

    def play(self) -> None:
        """Play this melody (make sure your computer's speakers are on!)."""
        play_midi_sequence(self.notes)

    def __repr__(self) -> str:
        """Return a string representation of this melody."""
        return f'Melody(name={repr(self.name)}, notes={self.notes})'


def play_midi_sequence(notes: list[tuple[int, int]]) -> None:
    """Given a list of notes, create a MIDI file and play it.
    """
    f = create_midi_file(notes)
    play_midi_file(f)


def play_midi_file(midi_file: io.BytesIO) -> None:
    """Given a file (or file-like) MIDI object, play it using pygame.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def create_midi_file(notes: list[tuple[int, int]]) -> io.BytesIO:
    """Create a MIDI file from the given list of notes.

    Notes are played with piano instrument.
    """
    byte_stream = io.BytesIO()

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for note, t in notes:
        track.append(mido.Message('note_on', note=note, velocity=64))
        track.append(mido.Message('note_off', note=note, time=t))

    mid.save(file=byte_stream)

    return io.BytesIO(byte_stream.getvalue())
