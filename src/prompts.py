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

import json
import os
from os import walk
from utils import num_tokens

# Every instance of this object within Prompt will be appended to the query sent
# to OpenAI as examples for how ChatGPT should responded.
class PromptExample:
    def __init__(self, prompt_example):
        self.example_input = {'role': 'user', 'content': prompt_example["example_input"] }
        self.example_output = {'role': 'assistant', 'content': prompt_example["example_output"]}

# This is an object representation of a custom prompt.
# The constructor takes a JSON encoded string and uses it to construct the Prompt.
# Each prompt contains the following:
#   - A model, which represents which model of ChatGPT should be used.
#   - A prompt name, which will be displayed to the user.
#   - Text containing instructions for how to modify the subtitle.
#   - (Optional) A set of examples for how ChatGPT should respond.
class Prompt:
    def __init__(self, prompt):
        obj = json.loads(prompt)
        self.name = obj["prompt_name"] # Name of prompt.
        self.instructions = os.linesep.join(obj["prompt_instructions"]) # Instructions for GPT.
        self.tokens = num_tokens(self.instructions)
        self.examples = [] # Example inputs and outputs to aid in instruction.
        if "prompt_examples" in obj:
            for example in obj["prompt_examples"]:
                self.examples.append(PromptExample(example))
        for example in self.examples:
            self.tokens += num_tokens(example.example_input)
            self.tokens += num_tokens(example.example_output)

# Instantiates a single Prompt object from a file.
def load_prompt(file):
    fp = open(file, "r")
    prompt = Prompt(fp.read())
    fp.close()
    return (prompt)

# Instantiates an array of Prompt objects from an array of filenames in string format.
def load_prompts(prompt_files):
    prompts = []
    for file in prompt_files:
        prompts.append(load_prompt(file))
    return (prompts)

# Instantiates a number of prompts from a directory.
def load_prompts_from_directory(dir):
    filenames = []
    for (directory_path, directory_name, files) in walk(dir):
        for file in files: 
            if file.endswith(".json"):
                filenames.append(directory_path + "\\" + file)
    return (load_prompts(filenames))
