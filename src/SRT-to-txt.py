#!/usr/bin/env python3

import openai
import srt
import sys
import os

ORAW_TEXT_UNIX = "../output/raw_SRT_text.txt"
OSRT_UNIX = "../output/output.srt"
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
def manual_process(subtitles_list):
    input("Press enter when processed data is placed into output/newContent.txt...")
    newContentFile = open("../input/newContent.txt", "r")
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


def main():
    if (len(sys.argv) < 3):
        print("Please enter the path to a valid SRT file & the mode you want to use.")
    subtitles_list = srt_to_text(sys.argv[1])
    if (sys.argv[2] == 'a'):
        answer, log = query_chatgpt("This is a test, please respond with ok.")
        print
    elif (sys.argv[2] == 'm'):
        manual_process(subtitles_list)
    else:
        print("Please enter either a or m to indicate whether you will use the automatic or manual process")

main()
