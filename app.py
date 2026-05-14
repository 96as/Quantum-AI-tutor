import streamlit as st
import plotly.graph_objects as go
from mock_data import MOCK_RESULTS, DEFAULT_RESULT

st.set_page_config(page_title="QuantumAI", layout="wide")

st.markdown("""
<style>
  footer, header { visibility: hidden; }

  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse at 30% 40%, rgba(123,94,167,.45) 0%, transparent 60%),
      #0D0A1A;
    background-attachment: fixed;
  }

  [data-testid="column"] {
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 20px;
    padding: 20px 24px ;
  }

  .stTextInput input {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 12px;
    color: white;
    backdrop-filter: blur(12px);
  }
  .stTextInput input::placeholder {
    color: rgba(255,255,255,.3);
  }
  .stTextInput input:focus {
    border-color: rgba(167,139,219,.6);
    box-shadow: 0 0 0 3px rgba(123,94,167,.2);
  }

  .stButton button {
    background: rgba(123,94,167,.5);
    border: 1px solid rgba(167,139,219,.45);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(123,94,167,.4);
  }
  .stButton button:hover {
    background: rgba(123,94,167,.75);
    box-shadow: 0 4px 32px rgba(123,94,167,.6);
    border: 1px solid rgba(167,139,219,.6);
  }

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 24px;
  padding: 44px 52px;
  margin-bottom: 28px;
  overflow: hidden;
  position: relative;
">
  <div style="position:absolute; inset:0;
              background:linear-gradient(135deg,rgba(123,94,167,.12) 0%,rgba(26,140,110,.08) 100%);
              border-radius:24px; pointer-events:none;"></div>
  <p style="font-family:monospace; font-size:11px; letter-spacing:2px;
            color:rgba(255,255,255,.4); text-transform:uppercase; margin-bottom:14px;">
    QuantumAI · Al Faisal University
  </p>
  <h1 style="font-size:clamp(26px,4vw,42px); font-weight:800; line-height:1.1;
             margin-bottom:10px; color:white;">
    AI-Assisted <span style="color:#A78BDB;">Quantum</span> Programming
  </h1>
  <p style="font-size:15px; color:rgba(255,255,255,.5); max-width:500px;
            line-height:1.65; margin-bottom:24px;">
    Type a natural-language prompt — get verified Qiskit code with plain-language explanation.
  </p>
  <div style="display:flex; gap:10px;">
    <span style="font-family:monospace; font-size:10px; color:rgba(255,255,255,.5);
                 border:1px solid rgba(255,255,255,.15); padding:5px 13px; border-radius:100px;">Claude API</span>
    <span style="font-family:monospace; font-size:10px; color:rgba(255,255,255,.5);
                 border:1px solid rgba(255,255,255,.15); padding:5px 13px; border-radius:100px;">Qiskit Aer</span>
    <span style="font-family:monospace; font-size:10px; color:rgba(255,255,255,.5);
                 border:1px solid rgba(255,255,255,.15); padding:5px 13px; border-radius:100px;">Bug detection</span>
  </div>
</div>
""", unsafe_allow_html=True)

prompt = st.text_input("", placeholder='e.g. "Make me a Bell state"  or  "Grover\'s algorithm marking |011⟩"')

col_run, col_reset, _ = st.columns([1.4, 1, 6])
with col_run:
    run = st.button("Generate & Verify", type="primary", use_container_width=True)
with col_reset:
    if st.button("Reset", use_container_width=True):
        st.rerun()

if run and prompt:
    result = DEFAULT_RESULT
    for keyword, data in MOCK_RESULTS.items():
        if keyword in prompt.lower():
            result = data
            break

    st.divider()

    col_code, col_chart = st.columns(2)

    with col_code:
        st.markdown("**Generated Code**")
        st.code(result["code"], language="python")

    with col_chart:
        st.markdown("**Output Distribution**")
        states = list(result["actual_distribution"].keys())
        fig = go.Figure()
        fig.add_bar(name="Actual",   x=states, y=list(result["actual_distribution"].values()), marker_color="#1A8C6E")
        fig.add_bar(name="Expected", x=states, y=list(result["expected_distribution"].values()), marker_color="#A78BDB", opacity=0.55)
        fig.update_layout(
            barmode="overlay", height=310,
            yaxis=dict(tickformat=".0%", gridcolor="rgba(255,255,255,.08)", color="rgba(255,255,255,.6)"),
            xaxis=dict(color="rgba(255,255,255,.6)"),
            legend=dict(orientation="h", y=1.12, font=dict(color="rgba(255,255,255,.7)")),
            margin=dict(t=10, b=40, l=40, r=10),
            plot_bgcolor="rgba(255,255,255,.03)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    if result["verification_passed"]:
        st.success(f"✓  Verification passed — {result['verification_message']}")
    else:
        st.error(f"✗  Verification failed — {result['verification_message']}")

    for bug in result["bugs"]:
        st.warning(f"⚠️  Pattern flagged — {bug}")

    st.markdown("**Explanation**")
    st.info(result["explanation"])
