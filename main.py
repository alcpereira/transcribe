import os
import xml.etree.ElementTree as ET
from typing import Dict, List
from dataclasses import dataclass


class Transcript:
    def __init__(self, root: ET.Element, filename: str):
        self.root = root
        self.filename = filename
        self.speakers: Dict[str, Speaker] = {}
        self.__add_all_speakers()
        self.silence = Speaker("silence", "Silence")

    def __repr__(self):
        decoration = "*" * 3 + "\n"
        output = decoration
        output += f"Transcript: {self.filename}\n"
        output += f"Speakers: {len(self.speakers)} speakers\n"
        for speaker in self.speakers.values():
            output += f"{speaker.name} ({speaker.id})\n"
            output += f"Total duration: {speaker.get_total_duration() / 1000} seconds\n"
            output += f"Total words: {speaker.get_total_words()}\n"
            output += f"Words per minute: {speaker.get_words_per_minute()}\n"
            output += decoration
        output += f"Silence: {len(self.silence.interventions)} interventions"
        output += f" pour une durée de {self.silence.get_total_duration() / 1000} secondes\n"
        output += decoration
        return output

    def __add_all_speakers(self):
        speakers_tag = self.root.find("Speakers")
        if speakers_tag is None:
            print("No Speakers tag found")
            return
        for speaker in speakers_tag.findall("Speaker"):
            self.speakers[speaker.attrib["id"]] = Speaker(speaker.attrib["id"], speaker.attrib["name"])

    def __parse_turn(self, turn: ET.Element) -> None:
        speaker_attribute = turn.attrib

        if "speaker" not in speaker_attribute:
            duration = clean_duration(turn.attrib["endTime"]) - clean_duration(turn.attrib["startTime"])
            self.silence.add_intervention(num_words=0, duration_ms=duration)
            return

        speakers_list = speaker_attribute["speaker"].split(" ")

        for speaker_id in speakers_list:
            duration = clean_duration(turn.attrib["endTime"]) - clean_duration(turn.attrib["startTime"])
            phrases = [i.strip() for i in turn.itertext() if i.strip()]
            num_words = 0
            for phrase in phrases:
                num_words += len(phrase.split(" "))
            self.speakers[speaker_id].add_intervention(num_words=num_words, duration_ms=duration)

    def parse_transcript(self):
        episode = self.root.find("Episode")
        if episode is None:
            print("No Episode tag found")
            return
        for section in episode.findall("Section"):
            for turn in section.findall("Turn"):
                self.__parse_turn(turn)
        pass


class Speaker:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.interventions: List[Intervention] = []

    def add_intervention(self, num_words, duration_ms):
        self.interventions.append(Intervention(num_words, duration_ms))

    def get_total_duration(self):
        return sum([intervention.duration_ms for intervention in self.interventions])

    def get_total_words(self):
        return sum([intervention.num_words for intervention in self.interventions])

    def get_words_per_minute(self):
        if self.get_total_duration() == 0:
            return 0
        return self.get_total_words() / (self.get_total_duration() / 60000)


@dataclass
class Intervention:
    num_words: int
    duration_ms: int


def clean_duration(duration: str) -> int:
    return int(float(duration) * 1000)


if __name__ == "__main__":
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    files = [f for f in os.listdir(data_folder) if f.endswith(".trico") or f.endswith(".trs")]

    # transcripts = []
    for file in files:
        with open(os.path.join(data_folder, file), "r", encoding="ISO-8859-1") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            transcript = Transcript(root, file)
            transcript.parse_transcript()
            print(transcript)
            # transcripts.append(Transcript(root, file))

    # print(transcripts)
