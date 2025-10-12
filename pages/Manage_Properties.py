import streamlit as st
from services.db import fetch_all_properties, delete_property

st.subheader("⚙️ Manage Properties")

props = fetch_all_properties()
if props:
    selected = st.selectbox("Select a property to delete", [p.address for p in props])
    if st.button("🗑️ Delete Selected Property"):
        delete_property(selected)
        st.warning(f"{selected} deleted.")
        st.rerun()
else:
    st.info("No properties available to delete.")