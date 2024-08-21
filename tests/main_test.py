import main
import xml.etree.ElementTree as ET


def test_get_speakers_single():
    trs_file = """
    <Turn speaker="spk1" startTime="33.121" endTime="36.835">
    <Sync time="33.121"/>
    Test test
    </Turn>"""
    turn = ET.fromstring(trs_file)
    assert main.get_speakers(turn) == ["spk1"]


def test_get_speakers_multiple():
    trs_file = """
    <Turn speaker="spk3 spk1" startTime="33.121" endTime="36.835">
    <Sync time="33.121"/>
    Test test
    </Turn>"""
    turn = ET.fromstring(trs_file)
    assert main.get_speakers(turn) == ["spk3", "spk1"]


def test_get_speakers_no_speaker():
    trs_file = """
    <Turn startTime="33.121" endTime="36.835">
    <Sync time="33.121"/>
    Test test
    </Turn>"""
    turn = ET.fromstring(trs_file)
    assert main.get_speakers(turn) == ["silence"]


def test_count_words_multiple_words():
    trs_file = """
    <Turn speaker="spk1" startTime="33.121" endTime="36.835">
    <Sync time="33.121"/>
    Test test
    </Turn>"""
    turn = ET.fromstring(trs_file)
    assert main.count_words(turn) == 2


def test_count_words_multiple_speakers():
    trs_file = """
    <Turn speaker="spk1 spk2" startTime="171.469" endTime="172.067">
    <Sync time="171.469"/>
    <Who nb="1"/>
    Test test 
    <Who nb="2"/>
    Test test test
    </Turn>"""
    turn = ET.fromstring(trs_file)

    speakers = main.get_speakers(turn)
    speaks = main.get_speaks(turn)

    for speaker in speakers:
        speaker_words = main.get_speaker_words(speaks, speakers, speaker)
        assert speaker_words == "Test test" or speaker_words == "Test test test"
        

test_count_words_multiple_speakers()