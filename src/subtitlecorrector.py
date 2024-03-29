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

from parsing import Segment, Chunk, Block
from query import QuerySegment
from openai import AsyncOpenAI
from config import Config
from const import Tiers
import asyncio
import utils
import time

SEG_DELAY = 70

# Program flow:
# First the .SRT gets read in and parsed into one or multiple Segment objects
# depending on the size of the file and the 'tier' of the organisation.
# Next a list of QuerySegment objects are created from the Segment objects.
# The QuerySegment object contains multiple Query objects which have a method called run().
# The method run() sends the actual request to the API and receives the response back.
# In addition it checks whether the response contains an equal amount of Block objects as the input.
# Both the input and the response are represented as Chunk objects, this type of object
# contains an array of Block objects which are a class representation of a single entry in a subtitle file.
# The QuerySegment object also contains a run() method which will asynchronously execute the run() method
# in each of the Query objects it contains.
# If a Query fails during execution of the run() method, it will raise a QueryException.
# Queries are run() asynchronously through the asyncio.gather() function, which returns a list containing
# the return values of each of the functions it has executed. In addition, if a given task raises an exception
# this exception will be included in the resulting list.
# If every Query executes run() successfully then the list returned by asyncio.gather() will consist only
# of a number of True values equivalent to the number of queries sent, but if a Query fails in its execution
# of run(), then it will also contain QueryException objecs.
# If present, these QueryException objects will be placed into their own list and sent to the
# resend_failed_queries() function, which will then attempt to fix whatever error may have occurred and
# then resend them. Queries will be continuously resent until they have failed too many times, or have succeeded.
# If a Query fails enough times to be considered "unfixable" then the Query will return its original input.
# This ensures that regardless of failure, a valid output .SRT will be created. This ensures
# that no amount of API usage is wasted.
# Finally the output will be converted to a singular string and written to the given outputfile.

class SubtitleCorrector:
    def __init__(self, prompt, subtitle_file):
        self.client = AsyncOpenAI() # OpenAI client used to communicate with the API.
        self.config = Config(prompt) # Config object which contains configuration options.
        self.subtitle_file = subtitle_file # Path to original input file.
        self.subs = utils.parse_subtitle_file(self.subtitle_file) # List of Sub objects.
        self.segments = self.load_subs() # An array of Segment objects parsed from the subtitle_file.
        self.cost = 0.0 # Total cost of processing the subtitle.
        self.successful_queries = 0 # Number of successfully returned queries.
        self.failed_queries = 0 # Number of unrecoverably failed queries.
        self.responses = [] # Final response data.

    # Loads a whole sub file as an array of Segment objects.
    # The function first converts each sub into a Block object and places it into an array.
    # Each Block has a number representing the amount of tokens it contains. When the sum total of
    # the token count of each block in the array exceeds the amount of tokens to send per
    # API request, the tokens are placed into a new Chunk object.
    # Each Chunk object also has a variable containing the number of tokens the object contains,
    # hence when the sum of the tokens in the Chunk array exceeds the amount to send in a "Segment"
    # these Chunks are placed in a new Segment object. If this value is never exceeded, the Chunk array
    # is nonetheless placed into a new Segment object at the end of the function.
    # It is rare for a file to require the creation of multiple Segments.
    # One shall generally suffice.
    def load_subs(self):
        segments = []
        chunks = []
        blocks = []
        for sub in self.subs:
            blocks.append(Block(sub.index, sub.content))
            if (utils.sum_tokens(blocks) >= self.config.tokens_per_query):
                chunks.append(Chunk(blocks.copy())) # Use .copy because otherwise it will be passed as pointer.
                blocks.clear()
            # This condition should only return true in such a case that sending a whole file asynchronously would exceed the rate limit.
            # Rate limit is determined by the organisation's tier and the model being used (See config.py).
            # You can find the rate limit info in const.py.
            if (utils.sum_tokens(chunks) >= Tiers[self.config.tier][self.config.model]['TPM']):
                segments.append(Segment(chunks.copy()))
                chunks.clear()
        chunks.append(Chunk(blocks)) # Places remaining Blocks into new Chunk.
        segments.append(Segment(chunks)) # Places remaining Chunks into new Segment.
        return (segments)

    # Returns modified subtitle data.
    async def run(self):
        sleep_time = 0
        # Constructs an array of QuerySegment objects from a given array of Segments.
        query_segments = list(map(lambda x: QuerySegment(x, self.client, self.config), self.segments))
        # Runs each QuerySegment object iteratively in order to process the entire file.
        for query_seg in query_segments:
            print("Entering new segment.")
            time.sleep(sleep_time)
            self.responses += await query_seg.run() # Appends array of Chunk objects to self.responses.
            sleep_time = SEG_DELAY
        utils.exit_message(query_segments, self.config.model)
        # Return a valid subtitle file from an array of Chunk objects.
        return (utils.subs_from_chunks(self.responses, self.subs))

# Constructs and runs the SubtitleCorrector class and writes the output to a file.
# This function is called in SRT-tui.py and SRT-gui.py
def correct_subtitles(subtitle_file, prompt, outputfile="output.srt"):
    subcorrector = SubtitleCorrector(prompt, subtitle_file)
    full_output = asyncio.run(subcorrector.run())
    with open(outputfile, "w", encoding="utf-8") as ofile:
        ofile.write(full_output)
