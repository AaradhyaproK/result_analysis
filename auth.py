import streamlit as st

class AuthenticationManager:
    def __init__(self, firebase_manager):
        self.fm = firebase_manager

    def show_login_page(self):
        st.markdown("""
        <div class="app-header">
            <h1>Student Result Pro</h1>
            <p>Advanced Analytics & Academic Tracking System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Centered Login Card
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
            
            with t1:
                with st.form("login"):
                    email = st.text_input("Email")
                    pwd = st.text_input("Password", type="password")
                    role = st.selectbox("Role", ["Teacher", "Student"])
                    if st.form_submit_button("Sign In", type="primary"):
                        success, result = self.fm.verify_user(email, pwd)
                        if success:
                            if result['role'] == role.lower():
                                st.session_state.user = result
                                st.session_state.logged_in = True
                                st.session_state.role = role.lower()
                                st.rerun()
                            else:
                                st.error(f"Role mismatch. Registered as '{result['role']}'.")
                        else:
                            st.error(result)
            
            with t2:
                with st.form("reg"):
                    # ... (Registration form logic) ...
                    pass