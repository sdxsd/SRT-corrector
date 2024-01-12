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

from query import QuerySegment
from openai import AsyncOpenAI
from parsing import load_subs
from config import Config
import asyncio
import utils

SEG_DELAY = 70

class SubtitleCorrector:
    def __init__(self, prompt):
        self.client = AsyncOpenAI() # OpenAI client used to communicate with the API.
        self.config = Config() # Config object which contains configuration options.
        self.config.prompt = prompt # Object containing instructions for how GPT should modify the subs.
        self.cost = 0.0 # Total cost of processing the subtitle.
        self.successful_queries = 0 # Number of successfully returned queries.
        self.failed_queries = 0 # Number of unrecoverably failed queries.
        self.responses = "" # Final response data.

    async def process_subs(self, subtitle_file):
        query_segments = []
        slist = utils.parse_subtitle_file(subtitle_file)
        segments = load_subs(slist, self.config.tokens_per_query, 1, self.config.model)
        for segment in segments:
            query_segments.append(QuerySegment(segment, self.client, self.config))
        for query_seg in query_segments:
            if (query_seg != query_segments[0]):
                print(f"Sleeping for {SEG_DELAY} seconds before processing next segment...")
                await asyncio.sleep(SEG_DELAY)
            success, fail, seg_cost, responses = await query_seg.run()
            self.cost += seg_cost
            self.successful_queries += success
            self.failed_queries += fail
            self.responses += responses
        utils.exit_message(self.cost, self.successful, self.failed)
        return (utils.replace_sub_content(''.join(responses).splitlines(), slist))

def correct_subtitles(subtitle_file, prompt, outputfile="output.srt"):
    subtitlecorrector = SubtitleCorrector(prompt)
    full_output = asyncio.run(subtitlecorrector.process_subs(subtitle_file))
    with open(outputfile, "w") as ofile:
        ofile.write(full_output)
