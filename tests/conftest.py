import copy

import pytest

from valcopilot.sample import SAMPLE
from valcopilot.workbook import read_workbook, write_workbook


@pytest.fixture
def sample_xlsx(tmp_path):
    return write_workbook(tmp_path / "sample.xlsx", sample=True)


@pytest.fixture
def sample_inputs(sample_xlsx):
    return read_workbook(sample_xlsx)


@pytest.fixture
def sample_data():
    return copy.deepcopy(SAMPLE)
