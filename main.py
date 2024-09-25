import os
import math
import xml.etree.ElementTree as ET
from typing import Dict, List
from dataclasses import dataclass
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import numpy as np
import seaborn as sns
import datetime
import argparse


REGEX_WHO = re.compile(r'<Who nb="(\d)+"\s?\/>(.*)', re.DOTALL)
ENCODING = "ISO-8859-1"


class Transcript:
    def __init__(self, root: ET.Element, filename: str):
        self.root = root
        self.filename = filename
        self.speakers: Dict[str, Speaker] = {}
        self.__add_all_speakers()
        self.silence = Speaker("silence", "Silence")
        self.start = 0.0
        self.end = 0.0

    def __repr__(self):  # pragma: no cover
        decoration = "*" * 10 + "\n"
        speaker_decoration = "-" * 5 + "\n"
        output = decoration
        output += f"Transcript: {self.filename}\n"
        output += f"Speakers: {len(self.speakers)} speakers\n"
        output += speaker_decoration
        for speaker in self.speakers.values():
            output += f"{speaker.name} ({speaker.id}) - {len(speaker.interventions)} interventions\n"
            output += f"Total duration: {(speaker.get_total_duration() / 1000):.2f} seconds\n"
            output += f"Total words: {speaker.get_total_words()}\n"
            output += f"Words per minute: {speaker.get_words_per_minute():.2f}\n"
            output += speaker_decoration
        output += f"Silence: {len(self.silence.interventions)} interventions"
        output += f" total duration: {self.silence.get_total_duration() / 1000} seconds\n"
        output += f"Total transcript duration: {(self.get_total_transcript_duration()):.2f} seconds\n"
        output += decoration
        return output

    def __add_all_speakers(self):
        speakers_tag = self.root.find("Speakers")
        if speakers_tag is None:
            print("No Speakers tag found")
            return
        for speaker in speakers_tag.findall("Speaker"):
            speaker_name = clean_speaker_name(speaker.attrib["name"], speaker.attrib["id"])
            self.speakers[speaker.attrib["id"]] = Speaker(speaker.attrib["id"], speaker_name)

    def __parse_turn(self, turn: ET.Element) -> None:
        speaker_attribute = turn.attrib

        if "speaker" not in speaker_attribute:
            self.silence.add_intervention(
                num_words=0,
                start_time_ms=clean_duration(turn.attrib["startTime"]),
                end_time_ms=clean_duration(turn.attrib["endTime"]),
            )
            return

        speakers_list = speaker_attribute["speaker"].split(" ")

        if len(speakers_list) == 1:
            speaker_id = speakers_list[0]
            num_words = len("".join(turn.itertext()).strip().split(" "))
            self.speakers[speaker_id].add_intervention(
                num_words=num_words,
                start_time_ms=clean_duration(turn.attrib["startTime"]),
                end_time_ms=clean_duration(turn.attrib["endTime"]),
            )
        else:
            pass
            words_holder = [
                {
                    "words": 0,
                    "speaker_id": i,
                }
                for i in speakers_list
            ]
            for who in turn.findall("Who"):
                byte_string = ET.tostring(who).decode(ENCODING)
                match = REGEX_WHO.match(byte_string)
                if match is None:
                    raise ValueError("Failed regex")
                [speaker_number, text] = match.groups()
                speaker_number = int(speaker_number) - 1
                words_holder[speaker_number]["words"] += len(text.strip().split(" "))
            for words in words_holder:
                self.speakers[words["speaker_id"]].add_intervention(
                    num_words=words["words"],
                    start_time_ms=clean_duration(turn.attrib["startTime"]),
                    end_time_ms=clean_duration(turn.attrib["endTime"]),
                )

    def get_total_transcript_duration(self):
        return self.end - self.start

    def parse_transcript(self):
        episode = self.root.find("Episode")
        if episode is None:
            print("No Episode tag found")
            return
        for section in episode.findall("Section"):
            if float(section.attrib["endTime"]) > self.end:
                self.end = float(section.attrib["endTime"])

            for turn in section.findall("Turn"):
                self.__parse_turn(turn)
        pass


class Speaker:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.interventions: List[Intervention] = []

    def add_intervention(self, num_words, start_time_ms, end_time_ms):
        self.interventions.append(Intervention(num_words, start_time_ms, end_time_ms))

    def get_total_duration(self):
        """Return the total duration of all interventions in milliseconds"""
        return sum([intervention.duration_ms for intervention in self.interventions])

    def get_total_words(self):
        return sum([intervention.num_words for intervention in self.interventions])

    def get_words_per_minute(self):
        if self.get_total_duration() == 0:
            return 0
        return self.get_total_words() / (self.get_total_duration() / 60000)

    def get_interventions_number(self):
        return len(self.interventions)


@dataclass
class Intervention:
    num_words: int
    start_time_ms: float
    end_time_ms: float

    @property
    def duration_ms(self) -> int:
        return int(self.end_time_ms - self.start_time_ms)


def clean_duration(duration: str) -> int:
    return int(float(duration) * 1000)


def clean_speaker_name(name: str, id: str) -> str:
    if name == "" or "???" in name:
        return id.replace("spk", "speaker#")
    return name


def draw_pie_chart(transcript: Transcript) -> None:  # pragma: no cover
    labels = ["Silence"]
    sizes = [transcript.silence.get_total_duration()]
    for speaker in transcript.speakers.values():
        if speaker.get_total_duration() < 100:
            continue
        labels.append(speaker.name)
        sizes.append(speaker.get_total_duration())
    _, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
    ax1.axis("equal")
    plt.title(f"Duration of {transcript.filename}")
    plt.show()


def draw_speakers_timeline_chart(transcript: Transcript, save=False) -> None:  # pragma: no cover
    dt = 1
    t = np.arange(0.0, transcript.get_total_transcript_duration(), dt)
    speakers = [i for i in transcript.speakers.values() if i.get_interventions_number() > 10]
    fig, axs = plt.subplots(nrows=len(speakers), sharex=True, figsize=(12, len(speakers) * 0.5))
    fig.suptitle(transcript.filename)
    colors = sns.color_palette("pastel", len(speakers))
    for i, speaker in enumerate(speakers):
        x = np.zeros(len(t))
        for intervention in speaker.interventions:
            start = math.floor(intervention.start_time_ms / 1000)
            end = math.floor(intervention.end_time_ms / 1000)
            x[start:end] = 1

        ax = axs[i]

        ax.set_title(speaker.name, fontsize=8, loc="left", pad=0)
        ax.fill_between(t, 0, x, color=colors[i], step="pre", alpha=0.9, where=(x > 0))

        # X axis
        ax.set_xlim(0, t[-1])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: str(datetime.timedelta(seconds=int(x)))))
        ax.xaxis.set_major_locator(MultipleLocator(60 * 10))

        # Y axis
        ax.axes.get_yaxis().set_visible(False)
        ax.set_ylim(0, 0.1)

    plt.xticks(fontsize=8)
    plt.subplots_adjust(hspace=1)

    if save:
        plt.savefig(f"charts/{transcript.filename}.png", dpi=300, bbox_inches="tight")
    else:
        plt.show()


if __name__ == "__main__":
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    files = [f for f in os.listdir(data_folder) if f.endswith(".trico") or f.endswith(".trs")]

    parser = argparse.ArgumentParser(description="Process transcript files.")
    parser.add_argument("--draw-timeline", action="store_true", help="Draw speakers timeline chart")
    parser.add_argument("--save-timeline", action="store_true", help="Save speakers timeline chart")
    parser.add_argument("--draw-piechart", action="store_true", help="Draw speakers piechart")
    args = parser.parse_args()

    for file in files:
        with open(os.path.join(data_folder, file), "r", encoding=ENCODING) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            transcript = Transcript(root, file)
            transcript.parse_transcript()

            print(transcript)

            if args.draw_timeline:
                draw_speakers_timeline_chart(transcript)
            if args.save_timeline:
                draw_speakers_timeline_chart(transcript, save=True)
            if args.draw_piechart:
                draw_pie_chart(transcript)
