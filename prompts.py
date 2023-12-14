import json
import os

# Every instance of this object within Prompt will be appended to the query sent
# to OpenAI as examples for how ChatGPT should responded.
class PromptExample:
    def __init__(self, prompt_example):
        self.example_input =  {'role': 'example_user', 'content': prompt_example["example_input"] }
        self.example_output = {'role': 'example_assistant', 'content': prompt_example["example_output"]}

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
        self.model = obj["prompt_model"]
        self.prompt_name = obj["prompt_name"]
        self.prompt_instructions = os.linesep.join(obj["prompt_instructions"])
        self.prompt_examples = []
        if (obj["prompt_examples"]):
            for example in obj["prompt_examples"]:
                self.prompt_examples.append(PromptExample(example))

# Instantiates an array of Prompt objects from an array of filenames in string format.
def load_prompts(prompt_files):
    prompts = []
    for file in prompt_files:
        fp = open(file, "r")
        prompts.append(Prompt(fp.read()))
        fp.close()
    return (prompts)
        
        
        