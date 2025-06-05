import streamlit as st

# Ultra-fast page config
st.set_page_config(
    page_title="Bitcoin Budget App",
    page_icon="₿",
    layout="centered"
)

# Immediate render - no calculations
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; color: #f7931a;">₿ Bitcoin Budget</h1>
        <p style="font-size: 1.3rem; color: #666;">Modern envelope budgeting for Bitcoin users</p>
        <p style="font-size: 1.1rem; margin: 2rem 0;">
            📊 Track your sats • 📁 Manage spending • 🚀 Visualize future value
        </p>
    </div>
""", unsafe_allow_html=True)

# Big call-to-action button
if st.button("🚀 Open Bitcoin Budget App", type="primary", use_container_width=True):
    st.markdown("""
        <meta http-equiv="refresh" content="0;url=https://bitcoinbudget.streamlit.app/">
    """, unsafe_allow_html=True)
    st.success("Redirecting to the full app...")

# Key features
st.markdown("""
    ### ✨ Key Features
    - 🏦 **Account-based budgeting** - Track on-budget and off-budget accounts
    - 📁 **Category management** - Envelope budgeting with roll-over balances  
    - 💎 **Sats-first** - Everything denominated in satoshis
    - 📊 **Advanced reports** - Net worth projections with Bitcoin Power Law
    - 🔒 **Privacy-first** - Your data stays in your browser session
    
    ### 🎯 Example: The Power of Stacking
    Starting with **1,000,000 sats** and adding **250,000 sats/month**:
    - **20 years later**: 61,000,000 sats total stack
    - **Real purchasing power**: 7.8x stronger vs inflation
    - **The magic**: Time + scarcity + discipline = 🚀
""")

st.markdown("---")
st.markdown("**Ready to start tracking your Bitcoin journey?**")

# Another CTA
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎯 Launch Full App", type="secondary", use_container_width=True):
        st.balloons()
        st.markdown("Opening Bitcoin Budget...")
        st.markdown("""
            <script>
                window.open('https://bitcoinbudget.streamlit.app/', '_blank');
            </script>
        """, unsafe_allow_html=True) 