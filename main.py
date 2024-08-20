import xml.etree.ElementTree as ET
import os

# Filter files that ends with .trico or .trs
files = [f for f in os.listdir() if f.endswith(".trico") or f.endswith(".trs")]


def get_speakers(turn):
    """Returns a list of speakers in the turn, if no speaker is found, returns ["silence"]"""
    if "speaker" in turn.attrib:
        speakers_list = turn.attrib["speaker"].split(" ")
        return speakers_list
    return ["silence"]


for file in files:
    print("Parsing file", file)
    with open(file, "r", encoding="ISO-8859-1") as f:
        tree = ET.parse(f)
        root = tree.getroot()

        episode = root.find("Episode")
        if episode is None:
            print("No Episode tag found")
            continue

        sections = episode.findall("Section")
        if sections is None:
            print("No Section tag found")
            continue

        for section in sections:
            for turn in section.findall("Turn"):
                print(get_speakers(turn))

            # for child in section:
            #     print(child.tag, child.attrib)


# The goal
# For each file separately
# Total time per speaker (including "silence")
# Number of time a speaker speaks
# Number of words per speaker (total) - Make it a function because this will be a bit changed later
# Bonus: Words/minute
# Visualization of the data
