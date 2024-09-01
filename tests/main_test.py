import main
import xml.etree.ElementTree as ET
import pytest


def test_speaker():
    speaker = main.Speaker("1", "John")
    assert speaker.id == "1"
    assert speaker.name == "John"
    assert speaker.interventions == []


def test_speaker_add_intervention():
    speaker = main.Speaker("1", "John")
    speaker.add_intervention(num_words=10, duration_ms=1000)
    assert len(speaker.interventions) == 1
    assert speaker.interventions[0].num_words == 10
    assert speaker.interventions[0].duration_ms == 1000


def test_speaker_get_total_words():
    speaker = main.Speaker("1", "John")
    speaker.add_intervention(num_words=10, duration_ms=1000)
    speaker.add_intervention(num_words=20, duration_ms=2000)
    assert speaker.get_total_words() == 30


def test_speaker_get_total_duration():
    speaker = main.Speaker("1", "John")
    speaker.add_intervention(num_words=10, duration_ms=1000)
    speaker.add_intervention(num_words=20, duration_ms=2000)
    assert speaker.get_total_duration() == 3000


def test_speaker_get_words_per_minute():
    speaker = main.Speaker("1", "John")
    speaker.add_intervention(num_words=10, duration_ms=30000)
    assert speaker.get_words_per_minute() == 20


def test_intervention():
    intervention = main.Intervention(10, 1000)
    assert intervention.num_words == 10
    assert intervention.duration_ms == 1000


@pytest.fixture
def transcript_one_speaker():
    xml = """
<Trans>
  <Speakers>
    <Speaker id="spk1" name="Speaker 1" />
  </Speakers>
  <Episode>
    <Section>
      <Turn speaker="spk1" startTime="0" endTime="30.000">
        <Sync time="0" />
        One two three four five.
      </Turn>
    </Section>
  </Episode>
</Trans>
"""
    return ET.fromstring(xml)


@pytest.fixture
def transcript_two_speakers():
    xml = """
<Trans>
  <Speakers>
    <Speaker id="spk1" name="Speaker 1" />
    <Speaker id="spk2" name="Speaker 2" />
  </Speakers>
  <Episode>
    <Section>
      <Turn speaker="spk1" startTime="0" endTime="30.000">
        <Sync time="0" />
        One two three four five.
      </Turn>
    </Section>
  </Episode>
</Trans>
"""
    return ET.fromstring(xml)


@pytest.fixture
def transcript_no_speakers():
    xml = """
<Trans>
  <Episode>
    <Section>
    </Section>
  </Episode>
</Trans>
"""
    return ET.fromstring(xml)


@pytest.fixture
def transcript_no_episode():
    xml = """
<Trans>
    <Speakers />
</Trans>
"""
    return ET.fromstring(xml)


@pytest.fixture
def transcript_silence():
    xml = """
<Trans>
    <Speakers>
        <Speaker id="spk1" name="Speaker 1" />
    </Speakers>
    <Episode>
        <Section>
            <Turn startTime="10.000" endTime="20.000">
                <Sync time="10.000" />
              </Turn>
        </Section>
    </Episode>
</Trans>
"""
    return ET.fromstring(xml)


@pytest.fixture
def transcript_multiple_speaker():
    xml = """
<Trans>
    <Speakers>
        <Speaker id="spk1" name="Speaker 1" />
        <Speaker id="spk2" name="Speaker 2" />
    </Speakers>
    <Episode>
        <Section>
            <Turn speaker="spk2 spk1" startTime="10.000" endTime="20.000">
                <Sync time="10.000" />
                <Who nb="1" />One two three four five.
                <Who nb="2" />One two three.

                <Who nb="1"/>Six seven eight nine ten.
              </Turn>
        </Section>
    </Episode>
</Trans>
"""
    return ET.fromstring(xml)


def test_transcript_one_speaker(transcript_one_speaker):
    transcript = main.Transcript(transcript_one_speaker, "test.xml")
    assert len(transcript.speakers) == 1
    assert "spk1" in transcript.speakers
    speaker_one = transcript.speakers["spk1"]
    assert speaker_one.name == "Speaker 1"
    assert speaker_one.id == "spk1"


def test_transcript_two_speakers(transcript_two_speakers):
    transcript = main.Transcript(transcript_two_speakers, "test.xml")
    assert len(transcript.speakers) == 2
    assert "spk2" in transcript.speakers
    speaker_two = transcript.speakers["spk2"]
    assert speaker_two.name == "Speaker 2"
    assert speaker_two.id == "spk2"


# def test_transcript_string_representation(transcript_two_speakers):
#     transcript = main.Transcript(transcript_two_speakers, "test.xml")
#     assert (
#         str(transcript)
#         == """***
# Transcript: test.xml with 2 speakers
# """
#     )


def test_transcript_no_speaker(transcript_no_speakers, capsys):
    transcript = main.Transcript(transcript_no_speakers, "test.xml")
    assert len(transcript.speakers) == 0
    assert "No Speakers tag found\n" == capsys.readouterr().out


def test_transcript_no_episode(transcript_no_episode, capsys):
    transcript = main.Transcript(transcript_no_episode, "test.xml")
    transcript.parse_transcript()
    assert "No Episode tag found\n" == capsys.readouterr().out


def test_transcript_silence_duration(transcript_silence):
    transcript = main.Transcript(transcript_silence, "test.xml")
    transcript.parse_transcript()
    assert transcript.silence.get_total_duration() == 10000


def test_clean_duration():
    assert main.clean_duration("10.000") == 10000
    assert main.clean_duration("10.00") == 10000
    assert main.clean_duration("10.0") == 10000
    assert main.clean_duration("10.") == 10000
    assert main.clean_duration("10") == 10000
    assert main.clean_duration("10.5") == 10500


def test_transcript_parsing_one_speaker(transcript_one_speaker):
    transcript = main.Transcript(transcript_one_speaker, "test.xml")
    transcript.parse_transcript()
    speaker_one = transcript.speakers["spk1"]
    assert speaker_one.get_total_duration() == 30000
    assert speaker_one.get_total_words() == 5
    assert speaker_one.get_words_per_minute() == 10
    assert speaker_one.get_interventions_number() == 1


def test_transcript_parsing_two_speakers(transcript_two_speakers):
    transcript = main.Transcript(transcript_two_speakers, "test.xml")
    transcript.parse_transcript()
    speaker_two = transcript.speakers["spk2"]
    assert speaker_two.get_total_duration() == 0
    assert speaker_two.get_total_words() == 0
    assert speaker_two.get_words_per_minute() == 0
    assert speaker_two.get_interventions_number() == 0


def test_transcript_parsing_multiple(transcript_multiple_speaker):
    transcript = main.Transcript(transcript_multiple_speaker, "test.xml")
    transcript.parse_transcript()
    speaker_one = transcript.speakers["spk1"]
    speaker_two = transcript.speakers["spk2"]
    assert speaker_one.get_total_duration() == 10000
    assert speaker_one.get_total_words() == 3
    assert speaker_one.get_interventions_number() == 1
    assert speaker_two.get_total_duration() == 10000
    assert speaker_two.get_total_words() == 10
    assert speaker_two.get_interventions_number() == 1
