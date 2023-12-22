import os
import platform
import json

default_config = {
    "model": "gpt-4-1106-preview",
    "prompt_directory": "",
    "tokens_per_query": 150
}

class Config():
    def __init__(self): 
        config_path, config_dir = self.determine_config_path() 
        if (not os.path.exists(config_path)):
            self.generate_default_config(config_path, config_dir)
        with open(config_path) as f:     
            obj = json.loads(f.read())
        self.model = obj['model']
        self.prompt_directory = obj['prompt_directory']
        self.tokens_per_query = obj['tokens_per_query']    
            
    def generate_default_config(self, config_path, config_dir):
        print("No config file found. Do you want to generate and install a default config?")
        result = self.question("Config file will be stored in: {}. Proceed? (y/n) ".format(config_path))
        if result == True:
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            with open(config_path, "w") as f:
                default_config["prompt_directory"] = os.path.join(os.path.expanduser("~"), "prompts").replace("\\", "\\\\")
                print("Your prompt directory will be located here: {}".format(default_config['prompt_directory']))
                f.write(json.dump(default_config))
        elif result == False:
            print("Cannot continue without config. Program exiting.")
            exit()
            
    def determine_config_path(self):
        name = "subtitle-corrector"
        home = os.path.expanduser("~")
        if (platform.system() == "Linux"):
            config_dir = os.path.join(home, ".config", name)
            config_path = os.path.join(home, ".config", name, "config.json")
        elif (platform.system() == "Darwin"):
            config_dir = os.path.join(home, "Library", "Application Support", name) 
            config_path = os.path.join(home, "Library", "Application Support", name, "config.json") 
        elif (platform.system() == "Windows"):
            config_dir = os.path.join(home, "AppData", "Local", name)
            config_path = os.path.join(home, "AppData", "Local", name, "config.json")
        else:
            print("Unsupported OS, exiting.")
            exit()
        return (config_path, config_dir)
    
    def question(self, message):
        while True:
            result = input(message)
            if result in ['y', 'yes']:
                return (True)
            elif result in ['n', 'no']:
                return (False)
        