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

from openai import AsyncOpenAI
import asyncio
import os
import exceptions
import prompts as prompts
import srt
import utils
from config import Config
from query import Query, QueryContent, QueryException

class SubtitleCorrector:
    def __init__(self, chosen_prompt):
        self.client = AsyncOpenAI()
        self.config = Config()
        self.chosen_prompt = chosen_prompt
        self.queries = []
        self.failed_queries = []

    # Replaces the "content" variable of the original subtitle block list
    # using the sum of the responses from GPT.
    def replace_sub_content(self, rawlines, slist):
        i = 0
        for sub in slist:
            sub.content = ""
            digit_encountered = False
            while (i < len(rawlines)):
                if (rawlines[i].rstrip().isdigit() is True):
                    if (digit_encountered is True):
                        digit_encountered = False
                        break
                    else:
                        digit_encountered = True
                else:
                    sub.content += ((" " if sub.content else "") + (rawlines[i] if rawlines[i].rstrip() != "" else ""))
                i += 1
        return (srt.compose(slist))

    # This function creates a list of queries (tasks)
    # which will later be executed by asyncio.gather()
    def prepare_queries(self, slist):
        query_text = ""
        query_tasks = []
        idx = 0
        for sub in slist:
            query_text += (os.linesep.join([str(sub.index), sub.content]) + os.linesep)
            token_count = utils.num_tokens(query_text)
            if (token_count > self.config.tokens_per_query or (slist[-1].index == sub.index)):
                query_content = QueryContent(self.chosen_prompt, query_text, self.config, token_count)
                self.queries.append(Query(idx, self.client, query_content))
                query_tasks.append(asyncio.create_task(self.queries[idx].run()))
                query_text = ""
                idx += 1
        return (query_tasks)

    def assemble_queries(self):
        responses = ""
        for query in self.queries:
            responses += query.response
        return (responses)

    # raw subtitle data -> array of sub blocks -> array of tasks to be executed -> modified subtitle data -> ??? -> profit
    async def process_subs(self, subtitle_file):
        failed_queries = []
        with open(subtitle_file, encoding="utf-8") as f:
            slist = list(srt.parse(f))
        print(f"Parsed: {subtitle_file}")
        query_tasks = self.prepare_queries(slist)
        try:
            await asyncio.gather(*query_tasks)
        except QueryException as e:
            failed_queries.append(e)
        exceptions.handle_failed_queries(self.failed_queries)
        responses = self.assemble_queries()
        print(f"All responses received.{os.linesep}Estimated cost: €{self.calculate_cost()}")
        return (self.replace_sub_content(''.join(responses).splitlines(), slist))

# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, prompt, outputfile="output.srt"):
    subtitlecorrector = SubtitleCorrector(prompt)
    full_output = asyncio.run(subtitlecorrector.process_subs(subtitle_file))
    with open(outputfile, "w") as ofile:
        ofile.write(full_output)
