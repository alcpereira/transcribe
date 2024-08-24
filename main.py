import xml.etree.ElementTree as ET
import os
import collections

# Filter files that ends with .trico or .trs
files = [f for f in os.listdir() if f.endswith(".trico") or f.endswith(".trs")]


def get_speaks(turn):
    return [i.strip() for i in turn.itertext() if i.strip()]


def get_speakers(turn):
    """Returns a list of speakers in the turn, if no speaker is found, returns ["silence"]"""
    if "speaker" in turn.attrib:
        speakers_list = turn.attrib["speaker"].split(" ")
        return speakers_list
    return ["silence"]


def get_speaker_words(speaks, speakers, speaker):
    for i in range(0, len(speakers)):
        spk = speakers[i]
        if speaker == spk:
            return speaks[i]

    return "test"


def count_words(turn):
    """Counts the number of words in the turn."""
    if "speaker" not in turn.attrib:
        return 0
    speaks = get_speaks(turn)
    if len(speaks) == 0:
        return 0
    return len(speaks[0].split(" "))  # [0] is hardcode


if __name__ == "__main__":
    for file in files:
        print("\nParsing file", file)
        with open(file, "r", encoding="ISO-8859-1") as f:
            tree = ET.parse(f)
            root = tree.getroot()

            speakers = collections.defaultdict(lambda: [0.0, 0, 0])  # [Total time, Number of turns, Total words]

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
                    time = float(turn.attrib["endTime"]) - float(turn.attrib["startTime"])
                    num_words = count_words(turn)
                    for speaker in get_speakers(turn):
                        speakers[speaker][0] += time
                        speakers[speaker][1] += 1
                        speakers[speaker][2] += num_words

            print(speakers)
            # for child in section:
            #     print(child.tag, child.attrib)
