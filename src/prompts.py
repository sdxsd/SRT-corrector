import json
import os
from os import walk

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
        self.name = obj["prompt_name"]
        self.instructions = os.linesep.join(obj["prompt_instructions"])
        self.examples = []
        if "prompt_examples" in obj:
            for example in obj["prompt_examples"]:
                self.examples.append(PromptExample(example))

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