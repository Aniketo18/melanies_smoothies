import streamlit as st
from snowflake.snowpark.functions import col
import requests 


# Page Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your Smoothie!")

# Customer Name
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)
cnx=st.connection("snowflake")
# Snowflake Session
session = cnx.session()
# Fetch fruit options
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .collect()
)

# Convert to Python list
fruit_options = [row["FRUIT_NAME"] for row in fruit_df]

# Ingredient Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=6
)

# Process Order
if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    st.write("Ingredients Selected:", ingredients_string)

    # Display fruit nutrition information
    for fruit in ingredients_list:

        st.subheader(f"🍓 {fruit}")

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
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
                        f"Sorry, no information available for {fruit}."
                    )

            else:
                st.warning(
                    f"Sorry, no information available for {fruit}."
                )

        except Exception:
            st.warning(
                f"Sorry, no information available for {fruit}."
            )

    # Submit button
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
 
