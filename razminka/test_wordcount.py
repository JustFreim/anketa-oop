import pytest

from wordcount import chastota


@pytest.fixture
def fayl_s_tekstom(tmp_path):
    put = tmp_path / "text.txt"
    put.write_text("Мама мыла раму. Рама, мама, рама!", encoding="utf-8")
    return put


def test_mama_i_rama_po_dva_raza(fayl_s_tekstom):
    stat = chastota(fayl_s_tekstom)
    assert stat["мама"] == 2
    assert stat["рама"] == 2


def test_net_znakov_prepinaniya_v_klyuchah(fayl_s_tekstom):
    stat = chastota(fayl_s_tekstom)
    assert "рама," not in stat
    assert "раму." not in stat


def test_chetyre_raznyh_slova(fayl_s_tekstom):
    assert len(chastota(fayl_s_tekstom)) == 4
