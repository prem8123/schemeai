import requests
import streamlit as st

st.set_page_config(page_title="SchemeAI", page_icon="🎓", layout="wide")
st.title("🎓 SchemeAI")
st.caption("Scholarship & education scheme eligibility assistant")

API = st.sidebar.text_input("API URL", "http://127.0.0.1:8000")
language = st.sidebar.selectbox("Response language", ["en", "kn", "hi"])

with st.form("profile"):
    age = st.number_input("Age", 1, 100, 20)
    state = st.text_input("State", "Karnataka")
    education_level = st.selectbox("Education level", ["UG", "PG", "DIPLOMA"])
    course = st.text_input("Course", "BTech")
    category = st.selectbox("Category", ["", "GENERAL", "SC", "ST", "OBC"])
    income = st.number_input("Annual family income (INR)", 0.0, 10000000.0, 250000.0, step=10000.0)
    disability = st.checkbox("Person with disability")
    class12_percentile = st.number_input("Class XII percentile (optional)", 0.0, 100.0, 0.0)
    regular_course = st.selectbox("Regular course?", ["Unknown", "Yes", "No"])
    query = st.text_area("What are you looking for?", "Which scholarships may I be eligible for?")
    submitted = st.form_submit_button("Find scholarships")

if submitted:
    payload = {
        "age": age,
        "state": state,
        "education_level": education_level,
        "course": course or None,
        "category": category or None,
        "annual_family_income": income,
        "disability": disability,
        "class12_percentile": class12_percentile or None,
        "regular_course": None if regular_course == "Unknown" else regular_course == "Yes",
    }
    try:
        response = requests.post(
            f"{API}/recommend",
            params={"query": query, "language": language},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        for item in data["results"]:
            with st.container(border=True):
                st.subheader(item["scheme"]["name"])
                st.write(f"**Status:** {item['status']}  |  **Match score:** {item['score']:.0%}")
                for reason in item["reasons"]:
                    st.write("•", reason)
                if item["missing_information"]:
                    st.warning("Missing: " + ", ".join(item["missing_information"]))
                if item["scheme"].get("freshness", {}).get("stale"):
                    st.warning("This source may be stale; verify the current official source before applying.")
                st.write("**Benefit:**", item["scheme"]["benefit"])
                provenance = (item["scheme"].get("provenance") or [{}])[0]
                st.caption(
                    f"Authority: {item['scheme']['authority']} | "
                    f"Evidence: {provenance.get('document_title', 'Official source')} | "
                    f"Reference: {provenance.get('reference', 'N/A')} | "
                    f"Verified: {provenance.get('last_verified', 'N/A')}"
                )
                if provenance.get("official_url"):
                    st.link_button("Open official source", provenance["official_url"])
        st.info(data["disclaimer"])
    except Exception as exc:
        st.error(f"Could not reach SchemeAI API: {exc}")
