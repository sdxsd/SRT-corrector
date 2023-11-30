#!/usr/bin/env python3

import srt

def process_subtitles(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
        subtitles = list(srt.parse(content))

    if subtitles:
        # Shift the content of each subtitle up by one position
        for i in range(len(subtitles) - 1, 0, -1):
            subtitles[i].content = subtitles[i - 1].content

        # Insert <blank sub> as the content of the first subtitle
        subtitles[0].content = "<blank sub>"

    # Convert back to srt format
    modified_subtitles = srt.compose(subtitles)

    # Write the modified subtitles to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(modified_subtitles)
# Example usage
process_subtitles('downfall-zoomer3.srt', 'downfall-zoomer-osync.srt')

