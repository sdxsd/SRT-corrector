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

from parsing import load_subs
from error import resend_failed_queries
from query import Query, QueryContent
from openai import AsyncOpenAI
from config import Config
from os import linesep
import asyncio
import utils

class SubtitleCorrector:
    def __init__(self, prompt):
        self.client = AsyncOpenAI() # OpenAI client used to communicate with the API.
        self.config = Config() # Config object which contains configuration options.
        self.prompt = prompt # Object containing instructions for how GPT should modify the subs.
        self.prompt_tcount = utils.num_tokens(self.prompt.instructions) # Token count of the instructions.

    def prepare_queries(self, slist):
        query_text = ""
        queries = []
        query_tasks = []
        idx = 0
        for sub in slist:
            query_text += (linesep.join([str(sub.index), sub.content]) + linesep)
            token_count = utils.num_tokens(query_text)
            if (token_count > self.config.tokens_per_query or (slist[-1].index == sub.index)):
                query_content = QueryContent(self.prompt, query_text, self.config, token_count + self.prompt_tcount)
                queries.append(Query(idx, self.client, query_content))
                query_tasks.append(asyncio.create_task(queries[idx].run()))
                query_text = ""
                idx += 1
        return (queries, query_tasks)

    async def process_subs(self, subtitle_file):
        slist = utils.parse_subtitle_file(subtitle_file)
        segments = load_subs(slist, self.config.tokens_per_query, 1, self.config.model)
        exit()
        queries, query_tasks = self.prepare_queries(slist)
        failed_queries = await asyncio.gather(*query_tasks, return_exceptions=True)
        await resend_failed_queries(failed_queries)
        successful, failed, responses = utils.assemble_queries(queries)
        print(f"({successful}) Successful ({failed}) Failed")
        print("All queries resolved.")
        print(f"Estimated cost: €{utils.calculate_cost(queries, self.config.model)}")
        return (utils.replace_sub_content(''.join(responses).splitlines(), slist))

def correct_subtitles(subtitle_file, prompt, outputfile="output.srt"):
    subtitlecorrector = SubtitleCorrector(prompt)
    full_output = asyncio.run(subtitlecorrector.process_subs(subtitle_file))
    with open(outputfile, "w") as ofile:
        ofile.write(full_output)
