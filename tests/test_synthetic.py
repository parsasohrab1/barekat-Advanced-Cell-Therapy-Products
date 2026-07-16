"""Tests for synthetic data generation."""

from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data


def test_generate_patients():
    df = generate_cell_therapy_data(n_patients=50, seed=1)
    assert len(df) == 50
    assert "Patient_ID" in df.columns
    assert "Treatment_Response" in df.columns
    assert "CRS_Grade" in df.columns
    assert df["Treatment_Response"].isin([0, 1]).all()
    assert set(df["CAR_Type"].unique()).issubset({"CARv1", "CARv2", "CARv3"})
