#!/usr/bin/env python3

import argparse
import openai
import srt
import sys
import os

ORAW_TEXT_UNIX = "./output/raw_SRT_text.txt"
OSRT_UNIX = "./output/output.srt"
subtitle_correction_prompt = '''You are going to help correct the subtitles for a talk given at a
programming school. You will be provided with an input, each newline is a new subtitle.
Your job is to remove redundant words, fix grammar, and make sure that sentences make sense in the context.
You are going to output the modified subtitles in the same format as it was given.
You MUST preserve the newlines.'''

# Parses the SRT file into raw text data delimited by newlines.
def srt_to_text(file_name):
    print("Formatting: " + file_name)
    srt_file = open(sys.argv[1])
    subtitles_list = list(srt.parse(srt_file.read()))
    ofile_raw_text = open(ORAW_TEXT_UNIX, "w")
    for sub in subtitles_list:
        ofile_raw_text.write(sub.content + "\n")
    print("Formatted: " + file_name)
    return (subtitles_list)

# Requires the user to manually access chatgpt and get the required output. Program will
# be paused until user confirms that the replacement subtitles are available.
# [deprecated]
def manual_process(subtitles_list):
    input("Press enter when processed data is placed into output/newContent.txt...")
    newContentFile = open("./input/newContent.txt", "r")
    newContentLines = newContentFile.readlines()
    i = 0
    for sub in subtitlesList:
        if (i > len(newContentLines) - 1):
            sub.content = sub.content
        else:
            sub.content = newContentLines[i]
            i += 1
    finalOutputFile = open(OSRT_UNIX, "w")
    finalOutputFile.write(srt.compose(subtitlesList))

# Queries ChatGPT with the stripped SRT data.
def query_chatgpt(question):
    openai.api_key = os.environ.get('OPENAI_KEY')
    client = openai.ChatCompletion()
    chat_log = [{
        'role': 'system',
        'content': "You are normal chatGPT",
    }]
    chat_log.append({'role': 'user', 'content': question})
    response = client.create(model='gpt-3.5-turbo', messages=chat_log)
    answer = response.choices[0]['message']['content']
    chat_log.append({'role': 'assistant', 'content': answer})
    return answer, chat_log

# Reads the raw SRT data and passes it to ChatGPT to be processed.
def auto_process():
    query = open(ORAW_TEXT_UNIX, "r")
    raw_text = query.read()
    answer, log = query_chatgpt(raw_text);

# Creates the argument parser.
# These python libraries are actually pretty cool.
def arg_parser_init():
    parser = argparse.ArgumentParser(
        prog="subtitle-corrector",
        description="Corrects subtitles by using ChatGPT",
        epilog="subtitle-corrector")
    parser.add_argument('filename', required=True)
    parser.add_argument('-m', '--manual', dest="manual_mode", required=False, default=False)
    return (parser)

# Main.
def main():
    parser = arg_parser_init()
    args = parser.parse_args()
    subtitles_list = srt_to_text(args.filename)
    if (args.manual_mode == True):
        manual_process(subtitles_list)
    else:
        auto_process()
main()
