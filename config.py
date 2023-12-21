import os
import platform
import json

default_config = '''{
    "model": "gpt-4-1106-preview",
    "prompt_directory": "$PD$",
    "tokens_per_query": 150
}'''

class Config():
    def __init__(self): 
        config_path, config_dir = self.determine_config_path() 
        if (not os.path.exists(config_path)):
            self.generate_default_config(config_path, config_dir)
        fp = open(config_path)
        obj = json.loads(fp.read())
        self.model = obj['model']
        self.prompt_directory = obj['prompt_directory']
        self.tokens_per_query = obj['tokens_per_query']
            
    def generate_default_config(self, config_path, config_dir):
        print("No config file found. Do you want to generate and install a default config?")
        while True:
            result = input("Config file will be stored in: {}. Proceed? (y/n) ".format(config_path))
            if result in ['y', 'yes']:
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
                fp = open(config_path, "w")
                fp.write(default_config.replace('$PD$', os.path.join(config_dir, "prompts").replace("\\", "\\\\")))
                fp.close()
                break
            elif result in ['n', 'no']:
                print("Cannot continue without config. Program exiting.")
                exit()
            
    def determine_config_path(self):
        name = "subtitle-corrector"
        home = os.path.expanduser("~")
        if (platform.system() == "Linux"):
            config_dir = os.path.join(home, ".config", name)
            config_path = os.path.join(home, ".config", name, "config.json")
        if (platform.system() == "Darwin"):
            config_dir = os.path.join(home, "Library", "Application Support", name) 
            config_path = os.path.join(home, "Library", "Application Support", name, "config.json") 
        if (platform.system() == "Windows"):
            config_dir = os.path.join(home, "AppData", "Local", name)
            config_path = os.path.join(home, "AppData", "Local", name, "config.json")
        return (config_path, config_dir)
        