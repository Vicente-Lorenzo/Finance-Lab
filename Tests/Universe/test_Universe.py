from Library.Universe.Universe import UniverseAPI

def test_universe_constants():
    assert UniverseAPI.Database == "Quant"
    assert UniverseAPI.Schema == "Universe"

def test_universe_base_structure():
    structure = UniverseAPI.Structure()
    assert "CreatedAt" in structure
    assert "CreatedBy" in structure
    assert "UpdatedAt" in structure
    assert "UpdatedBy" in structure