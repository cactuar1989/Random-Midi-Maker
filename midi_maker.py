import random
from midiutil import MIDIFile


#
#
# Global Settings
#
filename = 'random.mid'
solo = True # includes different patterns
song_scale = 'augmented' # See choices from scale_intervals below
song_key = 'e' # See choices from key_start below
length = 10*4 # In beats
tempo = 100 # In BPM
volume = 127 # 0-127, as per the MIDI standard
channel = 0 # Channel 10 reserved for percussion
string_skipping = False # Possible notes chosen from 2 strings above/below if True
check_scale = True # True will keep notes within scale chosen
make_arpeggio = False # True will use scale notes in order without duplicates

track_name = 'Guitar'
instrument = 30 # See https://en.wikipedia.org/wiki/General_MIDI for numbers
lowest_note = 40 # E standard 6 string starts at 40, 35 for 7 string
highest_note = 60 # E standard 6 string ends at 88

track = 0
max_reach = 5 # Max spacing between frets considered 'possible'
durations = [0.125, 0.25, 0.5] # Possible note durations in beats, 1 = quarter note
# Starting MIDI note for each key, used in scale generation
key_start = {
    'A': 21,
    'A#':22,
    'B': 23,
    'C': 24,
    'C#':25,
    'D': 26,
    'D#':27,
    'E': 28,
    'F': 29,
    'F#':30,
    'G': 31
}
# Scale intervals, valid options for 'song_scale' setting
scale_intervals = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'pentatonic major': [0, 2, 4, 7, 9],
    'blues major': [0, 3, 5, 6, 7, 9],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic minor': [0, 2, 3, 5, 7, 8, 11],
    'pentatonic minor': [0, 3, 5, 7, 10],
    'blues minor': [0, 3, 5, 6, 7, 10],
    'augmented': [0, 3, 4, 7, 8, 11],
    'be-bop': [0, 2, 4, 5, 7, 9, 10, 11],
    'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'whole-half': [0, 2, 3, 5, 6, 8, 9, 11],
    'half-whole': [0, 1, 3, 4, 6, 7, 9, 10],
    'whole tone': [0, 2, 4, 6, 8, 10],
    'augmented fifth': [0, 2, 4, 5, 7, 8, 9, 11],
    'major arpeggio': [0, 4, 7],
    'minor arpeggio': [0, 3, 7],
    'augmented arpeggio': [0, 4, 8],
    'diminished arpeggio': [0, 3, 6, 9]
}
note_patterns = [
    [1, 1, 1, -2],
    [1, 1, -1],
    [-1, -1, -1, 2],
    [-1, -1, 1],
    [7, -7]
]


#
#
# Functions
#
def trim_scale(scale):
    trimmed_scale = []
    for note in scale:
        if note >= lowest_note and note <= highest_note:
            trimmed_scale.append(note)
    return trimmed_scale


def get_scale(scale, key):
    # Piano lowest pitch is 21 (A0), highest is 108 (C8)
    # Six octaves will cover full guitar
    if key.upper() not in key_start:
        print(f'Unknown key: {key}. Defaulting to C.')
        key = 'C'
    octaves = 6
    start = key_start[key.upper()] # Use upper case key
    intervals = []
    notes_in_scale = []
    if scale.lower() not in scale_intervals:
        print(f'Unknown scale: {scale}. Defaulting to harmonic minor.')
        scale = 'harmonic minor'
    intervals = scale_intervals[scale]
    for octave in range(octaves):
        for interval in intervals:
            notes_in_scale.append(start + interval)
        start += 12
    notes_in_scale = trim_scale(notes_in_scale)
    return notes_in_scale


def get_notes(position, scale):
    # Get reachable notes on same string
    notes = []
    if string_skipping:
        strings = [-10, -5, 0, +5, +10] # Two string below, above, and current string
    else:
        strings = [-5, 0, 5] # No string skipping
    for string in strings:
        for fret in range(position - max_reach + string, position + max_reach + string):
            # Only add note if within bounds of the neck
            if fret <= highest_note and fret >= lowest_note:
                if check_scale:
                    if fret in scale and fret not in notes:
                        notes.append(fret)
    return notes


def arpeggio(position, scale):
    # Find where we were in the scale last note
    try:
        i = scale.index(position)
    except ValueError:
        # If we weren't in scale randomly pick one
        in_scale = False
        while not in_scale:
            position = random.choice(scale)
            if position <= highest_note and position >= lowest_note:
                i = scale.index(position)
                in_scale = True
    # Randomly move up or down scale
    shift = random.choice([-2,-1,1,2])
    if (i + shift) >= len(scale):
        i = i - len(scale)
    pitch = scale[i + shift]
    # Check if we are within the guitar's pitch range
    if pitch > highest_note or pitch < lowest_note:
        pitch = scale[i - shift]
    return pitch


def shred_run(position, scale, num_notes, direction):
    # print(direction)
    notes = []
    # check if position is in notes choice
    if position not in notes:
        # if it wasn't, pick a random notes
        position = random.choice(scale)
    # Find where we were in the scale last note
    i = scale.index(position)
    for num in range(num_notes):
        try:
            notes.append(scale[i + direction])
        except:
            # go the other direction if you hit the end of the scale
            direction = direction * -1
            notes.append(scale[i + direction])
        i = i + direction
        # print(notes)
    return notes


def insert_pattern(starting_position, notes, pattern, num_repeats):
    # print(f'Calling insert_pattern({starting_position}, notes, {pattern}, {num_repeats})')
    pattern_out = []
    # check if position is in notes choice
    if starting_position not in notes:
        # if it wasn't, pick a random notes
        starting_position = random.choice(notes)
    index = notes.index(starting_position)
    for repeat in range(num_repeats):
        for shift in pattern:
            try:
                pattern_out.append(notes[index])
                index = index + shift
            except:
                shift = shift * -1
                index = index + shift
    # print(f'pattern_out | {pattern_out}')
    return pattern_out


def make_solo(length=4, song_scale='harmonic minor', song_key='C'):
    time = 0 # In beats
    midi = MIDIFile(1) # One track, defaults to format 1 (tempo track automatically created)
    midi.addTempo(track, time, tempo)
    midi.addTrackName(track, time, track_name)
    midi.addProgramChange(track, channel, time, instrument) # Changes instrument
    previous_note = random.randint(lowest_note, lowest_note) # Start randomly between (low, high)
    scale = get_scale(song_scale, song_key)
    while time < length:
        # pick starting note near position
        notes = get_notes(previous_note, scale)
        previous_note = random.choice(notes)
        # pick from list of patterns randomly
        fx = random.choice([0, 1, 2, 3])
        # fx = 2
        if fx == 0:
            # add a single direction shred section
            direction = random.choice([-1, 1])
            duration = random.choice([0.125, 0.25])
            num_notes = random.randint(2, 20)
            notes = shred_run(previous_note, scale, num_notes, direction)
            for note in notes:
                midi.addNote(track, channel, note, time, duration, volume)
                time = time + duration
                previous_note = note
        if fx == 1:
            # add a sweep
            if 'major' in song_scale.lower():
                # use major arp
                sweep_scale = 'major arpeggio'
            else:
                # use minor arp
                sweep_scale = random.choice(['minor arpeggio','augmented arpeggio','diminished arpeggio'])
            sweep_notes = get_scale(sweep_scale, song_key)
            direction = random.choice([-1, 1])
            duration = random.choice([0.125, 0.25])
            num_notes = random.randint(2, 12)
            notes = shred_run(previous_note, sweep_notes, num_notes, direction)
            for note in notes:
                midi.addNote(track, channel, note, time, duration, volume)
                time = time + duration
                previous_note = note
            # sweep reverse direction
            direction = direction * -1
            notes = shred_run(previous_note, sweep_notes, num_notes, direction)
            for note in notes:
                midi.addNote(track, channel, note, time, duration, volume)
                time = time + duration
                previous_note = note
        if fx == 2:
            # repeated pattern
            num_repeats = random.randint(2, 6)
            pattern = random.choice(note_patterns)
            # pattern = [7,-7]
            duration = random.choice([0.125, 0.25])
            notes = insert_pattern(previous_note, scale, pattern, num_repeats)
            for note in notes:
                midi.addNote(track, channel, note, time, duration, volume)
                time = time + duration
                previous_note = note
        if fx == 3:
            # held note
            duration = random.choice([.5, 1, 1.25, 1.5, 1.75, 2])
            note = random.choice(notes)
            midi.addNote(track, channel, note, time, duration, volume)
            time = time + duration
    return midi


def make_midi(length=4, song_scale='harmonic minor', song_key='C'):
    time = 0 # In beats
    midi = MIDIFile(1) # One track, defaults to format 1 (tempo track automatically created)
    midi.addTempo(track, time, tempo)
    midi.addTrackName(track, time, track_name)
    midi.addProgramChange(track, channel, time, instrument) # Changes instrument
    previous_note = random.randint(lowest_note, lowest_note + 7) # Start randomly between (low, high)
    scale = get_scale(song_scale, song_key)
    # print(scale)
    while time < length:
        # 8=D
        if make_arpeggio:
            pitch = arpeggio(previous_note, scale)
        else:
            notes = get_notes(previous_note, scale)
            pitch = random.choice(notes)
        # duration = random.choice(durations)
        duration = 0.25
        midi.addNote(track, channel, pitch, time, duration, volume)
        previous_note = pitch
        time = time + duration
    return midi


def main():
    if solo:
        midi = make_solo(length, song_scale, song_key)
    else:
        midi = make_midi(length, song_scale, song_key)
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)


if __name__ == '__main__':
    main()