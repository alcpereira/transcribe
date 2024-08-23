import os
# import collections
import xml.etree.ElementTree as ET


# help = idk python fix it pls


class Transcript:
    def __init__(self, root: ET.Element):
        self.root = root

        self.find_all_speakers() # help
        # print(len(self.speakers))

    def find_all_speakers(self):
        self.speakers = []

        for speaker in self.root.find("Speakers").findall("Speaker"): # help
            self.speakers.append(Speaker(self.root, speaker.attrib["id"]))


class Speaker:
    def __init__(self, root: ET.Element, id: str):
        self.root = root
        self.id = id

        self.numberOfTurns = 0
        self.totalTime = 0
        self.words = []

        self.set_infos() # bad naming ik
        
        # print(self.numberOfTurns)
        # print(self.totalTime)
        # print(len(self.words))
        
        # speakers = collections.defaultdict(lambda: [0.0, 0, 0])  # [Total time, Number of turns, Total words]

    def set_infos(self):
        """Counts the number of words in the turn."""

        episode = self.root.find("Episode")
        sections = episode.findall("Section")

        for section in sections:
            for turn in section.findall("Turn"):
                attrib = turn.attrib

                if not "speaker" in attrib: # early continue 😎
                    continue

                for speaker in attrib["speaker"].split(' '):
                    if speaker == self.id:
                        delta = float(attrib["endTime"]) - float(attrib["startTime"])

                        self.totalTime += delta
                        self.numberOfTurns += 1
                        self.get_words(turn)

    def get_words(self, turn):
        speaks = [i.strip() for i in turn.itertext() if i.strip()]

        if len(speaks) != 0: # does it work in py ?? (help)
            return

        for speak in speaks:
            for word in speak.split(' '):
                self.words.append(word)


files = [f for f in os.listdir("..") if f.endswith(".trico") or f.endswith(".trs")]


transcripts = [] # storing them

class App:
    def __init__(self):
        for file in files:
            print("\nParsing file", file)
            with open("../" + file, "r", encoding="ISO-8859-1") as f: # ("../" + file) is a bit shit i guess
                tree = ET.parse(f)
                root = tree.getroot()

                episode = root.find("Episode")
                if episode is None:
                    print("No Episode tag found")
                    continue

                # sections = episode.findall("Section")
                # if sections is None:
                #     print("No Section tag found")
                #     continue

                transcripts.append(Transcript(root)) # , sections or not ??


App() # initializer (you will say thats dumb)


# idk if i should add anything else
# i cant graph things
# if need anything else pls lmk

# bb