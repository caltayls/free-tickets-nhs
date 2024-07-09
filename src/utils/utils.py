import pandas as pd

def get_areas_from_county(user_row, location_df) -> pd.DataFrame:
  # create new locations column containing towns/cities within counties selected.
  user_counties = pd.DataFrame(user_row.location, columns=["County"])
  return location_df.merge(user_counties,  how="inner")["Built-up area"]


