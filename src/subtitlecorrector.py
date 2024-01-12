#!/usr/bin/env python3

# SUBTITLE-CORRECTOR IS LICENSED UNDER THE GNU GPLv3
# Copyright (C) 2023 Will Maguire

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

# The definition of Free Software is as follows:
# 	- The freedom to run the program, for any purpose.
# 	- The freedom to study how the program works, and adapt it to your needs.
# 	- The freedom to redistribute copies so you can help your neighbor.
# 	- The freedom to improve the program, and release your improvements
#   - to the public, so that the whole community benefits.

# A program is free software if users have all of these freedoms.

from parsing import Segment, Chunk, Block, Tiers
from query import QuerySegment
from openai import AsyncOpenAI
from config import Config
import asyncio
import utils

SEG_DELAY = 1

class SubtitleCorrector:
    def __init__(self, prompt, subtitle_file):
        self.client = AsyncOpenAI() # OpenAI client used to communicate with the API.
        self.config = Config() # Config object which contains configuration options.
        self.config.prompt = prompt # Object containing instructions for how GPT should modify the subs.
        self.subtitle_file = subtitle_file
        self.subs = utils.parse_subtitle_file(self.subtitle_file) # List of Sub objects.
        self.segments = self.load_subs() # An array of Segment objects parsed from the subtitle_file.
        self.cost = 0.0 # Total cost of processing the subtitle.
        self.successful_queries = 0 # Number of successfully returned queries.
        self.failed_queries = 0 # Number of unrecoverably failed queries.
        self.responses = "" # Final response data.

    # Loads a whole sub file as an array of Segment objects.
    def load_subs(self):
        segments = []
        chunks = []
        blocks = []
        for sub in self.subs:
            blocks.append(Block(sub))
            if (sum(map(lambda b: b.tokens, blocks)) >= self.config.tokens_per_query):
                chunks.append(Chunk(blocks))
                blocks.clear()
            if (sum(map(lambda c: c.tokens, chunks)) >= Tiers[self.config.tier][self.config.model]['TPM']):
                segments.append(Segment(chunks))
                chunks.clear()
        chunks.append(Chunk(blocks))
        segments.append(Segment(chunks))
        return (segments)

    # Returns modified subtitle data.
    async def run(self):
        query_segments = []
        for segment in self.segments:
            query_segments.append(QuerySegment(segment, self.client, self.config))
        for query_seg in query_segments:
            print("Entering new segment.")
            if (query_seg != query_segments[0]):
                print(f"Sleeping for {SEG_DELAY} seconds before processing next segment...")
                await asyncio.sleep(SEG_DELAY)
            result = await query_seg.run()
            self.responses += result
        utils.exit_message(query_segments, self.config.model)
        return (utils.replace_sub_content(''.join(self.responses).splitlines(), self.subs))

def correct_subtitles(subtitle_file, prompt, outputfile="output.srt"):
    subcorrector = SubtitleCorrector(prompt, subtitle_file)
    full_output = asyncio.run(subcorrector.run())
    with open(outputfile, "w") as ofile:
        ofile.write(full_output)
