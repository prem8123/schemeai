import os
import requests
import streamlit as st

st.set_page_config(page_title="SchemeAI",page_icon="🎓",layout="wide")
st.title("🎓 SchemeAI")
st.caption("Scholarship & education scheme eligibility assistant")
API=st.sidebar.text_input("API URL",os.getenv("SCHEMEAI_API_URL","http://127.0.0.1:8000"))
API_KEY=st.sidebar.text_input("API key (optional)",type="password")
language=st.sidebar.selectbox("Response language",["en","kn","hi"])

with st.form("profile"):
    age=st.number_input("Age",1,100,20)
    state=st.text_input("State","Karnataka")
    education_level=st.selectbox("Education level",["XI","XII","UG","PG","DIPLOMA"])
    course=st.text_input("Course","BTech")
    category=st.selectbox("Category",["","GENERAL","SC","ST","OBC"])
    income=st.number_input("Annual family income (INR)",0.0,10000000.0,250000.0,step=10000.0)
    gender=st.selectbox("Gender",["","MALE","FEMALE","OTHER"])
    disability=st.checkbox("Person with disability")
    disability_percentage=st.number_input("Disability percentage",0.0,100.0,0.0,step=1.0,disabled=not disability)
    class12_percentile=st.number_input("Class XII percentile (optional)",0.0,100.0,0.0)
    regular_course=st.selectbox("Regular course?",["Unknown","Yes","No"])
    is_diploma=st.selectbox("Diploma student?",["Unknown","Yes","No"])
    gap_after_class12=st.selectbox("Gap after Class XII?",["Unknown","Yes","No"])
    receives_other=st.selectbox("Receiving another scholarship/fee reimbursement?",["Unknown","Yes","No"])
    admission_qhei=st.selectbox("Admitted to an eligible QHEI?",["Unknown","Yes","No"])
    working_part_time=st.selectbox("Working professional in a part-time programme?",["Unknown","Yes","No"])
    query=st.text_area("What are you looking for?","Which scholarships may I be eligible for?")
    submitted=st.form_submit_button("Find scholarships")

def optional_bool(value): return None if value=="Unknown" else value=="Yes"

if submitted:
    payload={"age":age,"state":state,"education_level":education_level,"course":course or None,"category":category or None,"annual_family_income":income,"gender":gender or None,"disability":disability,"disability_percentage":disability_percentage if disability else None,"class12_percentile":class12_percentile or None,"regular_course":optional_bool(regular_course),"is_diploma":optional_bool(is_diploma),"gap_after_class12":optional_bool(gap_after_class12),"receives_other_scholarship":optional_bool(receives_other),"admission_in_qhei":optional_bool(admission_qhei),"working_professional_part_time":optional_bool(working_part_time)}
    headers={"X-API-Key":API_KEY} if API_KEY else {}
    try:
        response=requests.post(f"{API}/recommend",params={"query":query,"language":language},json=payload,headers=headers,timeout=30)
        response.raise_for_status()
        data=response.json()
        for item in data["results"]:
            with st.container(border=True):
                st.subheader(item["scheme"]["name"])
                st.write(f"**Status:** {item['status']} | **Evidence completeness:** {item['score']:.0%}")
                for reason in item["reasons"]: st.write("•",reason)
                if item["missing_information"]: st.warning("Missing: "+", ".join(item["missing_information"]))
                freshness=item["scheme"].get("freshness") or {}
                if freshness.get("stale"): st.warning("This source may be stale; verify the current official source before applying.")
                st.write("**Benefit:**",item["scheme"]["benefit"])
                provenance=(item["scheme"].get("provenance") or [{}])[0]
                st.caption(f"Authority: {item['scheme']['authority']} | Evidence: {provenance.get('document_title','Official source')} | Reference: {provenance.get('reference','N/A')} | Verified: {provenance.get('last_verified','N/A')}")
                if provenance.get("official_url"): st.link_button("Open official source",provenance["official_url"])
        st.info(data["disclaimer"])
    except requests.RequestException as exc: st.error(f"Could not reach SchemeAI API: {exc}")
    except (KeyError,ValueError) as exc: st.error(f"SchemeAI returned an invalid response: {exc}")
