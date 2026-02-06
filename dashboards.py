import streamlit as st
import datetime
from analyzer import AdvancedResultAnalyzer
from ui_renderers import *
from utils import flatten_student_data_for_export, convert_df_to_excel

def show_teacher_dashboard(fm):
    # Navigation Bar (Top)
    nav_options = ["📤 Upload", "📂 Saved", "🔍 Search", "🏛️ Overview", "🚪 Logout"]
    choice = st.radio("Navigation", nav_options, horizontal=True, label_visibility="collapsed")

    # Reset active file view when switching tabs
    if st.session_state.get('last_nav_choice') != choice:
        st.session_state.active_analysis_file = None
        st.session_state.last_nav_choice = choice

    if choice == "📤 Upload":
        st.subheader("Upload Result PDF")
        uploaded = st.file_uploader("Choose PDF", type="pdf")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            exam_tag = st.text_input("Exam Name", placeholder="e.g., SE Computer May 2024")
        with c2:
            department = st.selectbox("Department", ["Computer", "IT", "Mechanical", "Civil", "Electrical", "AIDS", "E&TC", "General Science"])
        with c3:
            year = st.selectbox("Year", ["FE", "SE", "TE", "BE"])
        
        if uploaded and exam_tag:
            analyzer = AdvancedResultAnalyzer()
            text = analyzer.extract_text_from_pdf(uploaded)
            if text:
                data = analyzer.parse_comprehensive_data(text)
                if data:
                    analyzer.students_data = data
                    st.success(f"Successfully processed {len(data)} student records")
                    
                    t1, t2, t3, t4, t5, t6 = st.tabs(["Overview", "Top Performers", "Failures", "Subject Analysis", "Detailed List", "Advanced Insights"]) 
                    with t1: render_overview_dashboard(analyzer, "upload_overview")
                    with t2: render_top_performers(analyzer, "upload_top")
                    with t3: render_failed_analysis(analyzer, "upload_fail")
                    with t4: render_subject_summary(analyzer, "upload_sub")
                    with t5: render_detailed_data(analyzer, "upload_detailed")
                    with t6: render_advanced_analytics(analyzer, "upload_adv")
                    
                    if st.button("💾 Save Data to Cloud", type="primary"):
                        summary = analyzer.get_result_summary()
                        fm.save_result_data(uploaded.name, exam_tag, department, year, data, st.session_state.user['name'], summary)
                else:
                    st.error("No data found")
        elif uploaded and not exam_tag:
            st.warning("⚠️ Please provide an Exam Name to proceed.")

    elif choice == "📂 Saved":
        if st.session_state.get('active_analysis_file'):
            f = st.session_state.active_analysis_file
            if st.button("← Back to List"):
                st.session_state.active_analysis_file = None
                st.rerun()
            
            st.markdown(f"### 📊 Analysis: {f.get('exam_tag', 'Unknown')}")
            analyzer = AdvancedResultAnalyzer()
            analyzer.students_data = f.get('students_data', [])
            
            t1, t2, t3, t4, t5, t6 = st.tabs(["Overview", "Top Performers", "Failures", "Subject Analysis", "Detailed List", "Advanced Insights"]) 
            with t1: render_overview_dashboard(analyzer, f"saved_{f['id']}_overview")
            with t2: render_top_performers(analyzer, f"saved_{f['id']}_top")
            with t3: render_failed_analysis(analyzer, f"saved_{f['id']}_fail")
            with t4: render_subject_summary(analyzer, f"saved_{f['id']}_sub")
            with t5: render_detailed_data(analyzer, f"saved_{f['id']}_detailed")
            with t6: render_advanced_analytics(analyzer, f"saved_{f['id']}_adv")
        else:
            st.subheader("Archived Results")
            files = fm.get_all_result_files()
            
            # --- FILTERS ---
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    search_query = st.text_input("🔍 Search Results", placeholder="Search by Exam Name...", key="saved_search")
                with c2:
                    dept_filter = st.selectbox("Filter by Dept", ["All", "Computer", "IT", "Mechanical", "Civil", "Electrical", "AIDS", "E&TC", "General Science"], key="saved_dept")
                with c3:
                    year_filter = st.selectbox("Filter by Year", ["All", "FE", "SE", "TE", "BE"], key="saved_year")

            # --- FILTER LOGIC ---
            filtered_files = []
            for f in files:
                tag = f.get('exam_tag', '').lower()
                fname = f.get('file_name', '').lower()
                q = search_query.lower().strip()
                
                if q and (q not in tag and q not in fname): continue
                if dept_filter != "All" and f.get('department', 'Uncategorized') != dept_filter: continue
                if year_filter != "All" and f.get('year', 'Unknown') != year_filter: continue
                filtered_files.append(f)

            if not filtered_files: 
                st.info("No results match your filters.")
            else:
                # --- GRID VIEW (2 per row) ---
                for i in range(0, len(filtered_files), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(filtered_files):
                            f = filtered_files[i + j]
                            with cols[j]:
                                with st.container(border=True):
                                    time_str = f.get('uploaded_at', datetime.datetime.now())
                                    if isinstance(time_str, datetime.datetime): time_str = time_str.strftime('%Y-%m-%d')
                                    summary = f.get('summary', {})
                                    
                                    st.markdown(f"""
                                    <div style="margin-bottom: 15px;">
                                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                                            <h4 style="margin: 0; color: #f8fafc; font-size: 1.1rem;">{f.get('exam_tag', 'N/A')}</h4>
                                            <span style="font-size: 0.75rem; color: #94a3b8; background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 12px;">{time_str}</span>
                                        </div>
                                        <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 15px;">
                                            <i class="fas fa-building" style="color: #818cf8;"></i> {f.get('department', 'N/A')} &nbsp;|&nbsp; <i class="fas fa-calendar" style="color: #818cf8;"></i> {f.get('year', 'N/A')}
                                        </div>
                                        <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 10px;">
                                            <div style="text-align: center;"><div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Students</div><div style="font-weight: 700; color: #f8fafc; font-size: 1rem;">{f.get('total_students', 0)}</div></div>
                                            <div style="text-align: center;"><div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Pass Rate</div><div style="font-weight: 700; color: #4ade80; font-size: 1rem;">{summary.get('pass_percentage', 0)}%</div></div>
                                            <div style="text-align: center;"><div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Avg SGPA</div><div style="font-weight: 700; color: #fbbf24; font-size: 1rem;">{summary.get('average_sgpa', 0)}</div></div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"📊 View Dashboard", key=f"btn_{f['id']}", use_container_width=True):
                                        st.session_state.active_analysis_file = f
                                        st.rerun()

    elif choice == "🔍 Search":
        st.subheader("Global Student Search")
        
        identifiers_map = fm.get_all_student_identifiers()
        search_options = [f"{name} | {prn}" for prn, name in identifiers_map.items()]
        
        final_selection_str = st.selectbox(
            "Search Student", 
            options=search_options,
            index=None,
            placeholder="🔍 Type Name or PRN to Search...",
            label_visibility="collapsed"
        )

        if final_selection_str:
            final_search_prn = final_selection_str.split(" | ")[-1]
            with st.spinner(f"Loading history..."):
                history_results = fm.get_student_history(final_search_prn) 
                analyzer = AdvancedResultAnalyzer()
                if history_results:
                    render_student_profile(history_results[0], analyzer)
                else:
                    st.error("Profile not found.")

    elif choice == "🏛️ Overview":
        render_college_overview(fm)

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.pop('id_token', None)
        st.session_state.pop('user_id', None)
        st.session_state.user = None
        st.rerun()

def show_student_dashboard(fm):
    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("Logout", key="student_logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.pop('id_token', None)
            st.session_state.pop('user_id', None)
            st.session_state.user = None
            st.rerun()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### <i class='fas fa-search'></i> Find Your Records", unsafe_allow_html=True)
    
    identifiers_map = fm.get_all_student_identifiers()
    search_options = [f"{name} | {prn}" for prn, name in identifiers_map.items()]
    
    final_selection_str = st.selectbox(
        "Confirm Identity", 
        options=search_options,
        index=None,
        placeholder="Select Your Profile..."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if final_selection_str:
        final_search_prn = final_selection_str.split(" | ")[-1]
        with st.spinner(f"Retrieving academic records..."):
            history_results = fm.get_student_history(final_search_prn)
            analyzer = AdvancedResultAnalyzer()
            if history_results:
                render_student_profile(history_results[0], analyzer)
            else:
                st.error("Profile data not found.")
