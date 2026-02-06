import streamlit as st
from styles import apply_custom_styles
from firebase_manager import FirebaseManager
from auth import AuthenticationManager
from dashboards import show_teacher_dashboard, show_student_dashboard

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
   page_title="Student Result Analyzer Pro",
   page_icon="🎓",
   layout="wide",
   initial_sidebar_state="collapsed"
)

# Apply CSS Styles
apply_custom_styles()

# -----------------------------------------------------------------------------
# 2. MAIN APPLICATION FLOW
# -----------------------------------------------------------------------------
def main():
   if 'logged_in' not in st.session_state:
       st.session_state.logged_in = False
       st.session_state.user = None
   
   fm = FirebaseManager()
   auth = AuthenticationManager(fm)
   
   if not st.session_state.logged_in:
       auth.show_login_page()
   else:
       if st.session_state.role == 'teacher':
           show_teacher_dashboard(fm)
       else:
           show_student_dashboard(fm)

   # Footer
   st.markdown("""
   <div class="footer">
       <p>Developed by <span style="color: #818cf8; font-weight: 600;">Sakshi</span> &nbsp;|&nbsp; Student Result Analyzer Pro</p>
   </div>
   """, unsafe_allow_html=True)

if __name__ == "__main__":
   main()
