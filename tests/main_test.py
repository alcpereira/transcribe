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
