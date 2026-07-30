import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# Page Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your Smoothie!")

# Customer Name
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")

# Snowflake Session
session = cnx.session()

# Fetch fruit options with SEARCH_ON column
fruit_rows = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
    .collect()
)

# Create pandas dataframe
pd_df = pd.DataFrame(
    [
        {
            "FRUIT_NAME": row["FRUIT_NAME"],
            "SEARCH_ON": row["SEARCH_ON"]
        }
        for row in fruit_rows
    ]
)

# Create list for multiselect
fruit_options = pd_df["FRUIT_NAME"].tolist()

# Ingredient Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Process Order
if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    st.write("Ingredients Selected:", ingredients_string)

    # Display nutrition info
    for fruit_chosen in ingredients_list:

        st.subheader(f"🍓 {fruit_chosen}")

        try:
            # Get SEARCH_ON value
            search_on = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]

            # Use FRUIT_NAME if SEARCH_ON is empty
            if pd.isna(search_on) or str(search_on).strip() == "":
                search_value = fruit_chosen.lower()
            else:
                search_value = str(search_on).lower()

            # Debug information
            st.write("Fruit Chosen:", fruit_chosen)
            st.write("Search Value:", search_value)

            # API Call
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_value}"
            )

            if smoothiefroot_response.status_code == 200:

                fruit_data = smoothiefroot_response.json()

                if fruit_data:
                    st.dataframe(
                        data=fruit_data,
                        use_container_width=True
                    )
                else:
                    st.warning(
                        f"Sorry, no information available for {fruit_chosen}."
                    )

            else:
                st.warning(
                    f"API returned status code {smoothiefroot_response.status_code}"
                )

        except Exception as e:
            st.error(f"Error for {fruit_chosen}: {str(e)}")

    # Submit Order
    if st.button("Submit Order"):

        insert_sql = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (NAME_ON_ORDER, INGREDIENTS)
        VALUES
        ('{name_on_order}', '{ingredients_string}')
        """

        session.sql(insert_sql).collect()

        st.success(
            f"✅ Your Smoothie has been ordered, {name_on_order}!"
        )
