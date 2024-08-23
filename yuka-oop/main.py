import os
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET


# help = idk python fix it pls

class Transcript:
    def __init__(self, root: ET.Element, fileName: str):
        self.root = root
        self.fileName = fileName

        self.find_all_speakers() # help
        # print(f"Total of speakers: {len(self.speakers)}")

    def find_all_speakers(self):
        self.speakers = []
# for i, spk in enumerate(speakers):
        for i, speaker in enumerate(self.root.find("Speakers").findall("Speaker")): # help
            self.speakers.append(Speaker(self.root, i, speaker.attrib["id"]))


class Speaker:
    def __init__(self, root: ET.Element, id: str, name: str):
        self.root = root
        self.id = id
        self.name = name

        self.set_stats() # bad naming ik
        # print(self.stats)
        

    def set_stats(self):
        self.stats = [0.0, 0, 0, 0]  # [Total time (s), Number of turns, Total words, Words per minute]

        episode = self.root.find("Episode")
        sections = episode.findall("Section")

        for section in sections:
            for turn in section.findall("Turn"):
                attrib = turn.attrib

                if not "speaker" in attrib: # early continue 😎
                    continue

                for speaker in attrib["speaker"].split(' '):
                    if speaker == self.name:
                        delta = float(attrib["endTime"]) - float(attrib["startTime"])

                        self.stats[0] += delta
                        self.stats[1] += 1
                        self.stats[2] += self.number_of_words_per_turn(turn, attrib["startTime"])

                self.calculate_words_per_minute()

                # self.calculate_words_per_minute(self.stats[0], self.stats[2])

    def number_of_words_per_turn(self, turn, t):
        speaks = [i.strip() for i in turn.itertext() if i.strip()]

        wordCount = 0

        for i, speak in enumerate(speaks):
            if self.id == i:
                wordCount += len(speak.split(' '))

        return wordCount
    
    def calculate_words_per_minute(self):
        self.stats[3] = self.stats[2] / (self.stats[0] / 60) if self.stats[2] != 0 else 0 # ZeroDivisionError
    
    # def calculate_words_per_minute(self, totaltime, words):
    #     self.stats[3] = words / (totaltime / 60) if words != 0 else 0 # ZeroDivisionError


files = [f for f in os.listdir("..") if f.endswith(".trico") or f.endswith(".trs")]


transcripts = [] # storing them

class App:
    def __init__(self):
        for file in files:
            # print("\nParsing file", file)
            with open("../" + file, "r", encoding="ISO-8859-1") as f: # ("../" + file) is a bit shit i guess
                tree = ET.parse(f)
                root = tree.getroot()

                episode = root.find("Episode")
                if episode is None:
                    print("No Episode tag found")
                    continue

                transcripts.append(Transcript(root, file))


if __name__ == "__main__":
    App() # initializer (you will say thats dumb)


for transcript in transcripts:
    speakerCount = len(transcript.speakers)

    x = np.arange(speakerCount) + 1
    y = [stats[2] for stats in [speaker.stats for speaker in transcript.speakers]]

    plt.plot(x, y, color= "green")
    plt.xlabel('Speaker')
    plt.ylabel('Word count')

    plt.title(transcript.fileName)

    plt.show()