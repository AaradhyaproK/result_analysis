import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import defaultdict
from utils import convert_df_to_excel

def render_student_profile(student_history, analyzer):
    # PROFESSIONAL PROFILE CARD
    st.markdown(f"""
    <div class="profile-hero">
        <div class="profile-avatar"><i class="fas fa-user-graduate"></i></div>
        <div class="profile-info">
            <h2>{student_history['Name']}</h2>
            <p><i class="fas fa-id-card"></i> {student_history['PRN']} &nbsp;|&nbsp; <i class="fas fa-user"></i> {student_history['Mother']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if len(student_history['Results']) > 0:
        results_df = pd.DataFrame(student_history['Results'])
        
        # EXCEL EXPORT FOR STUDENT HISTORY
        c1, c2 = st.columns([8, 2])
        with c2:
            excel_data = convert_df_to_excel(results_df)
            st.download_button(
                label="📥 Download History (Excel)",
                data=excel_data,
                file_name=f"{student_history['Name']}_History.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_student_history"
            )

        # PREDICTION & FAILURE ALERTS
        predicted_sgpa = analyzer.predict_next_sgpa(student_history)
        
        failed_subjects_list = []
        for result in student_history['Results']:
            for sub in result.get('Subjects', []):
                grade = sub.get('Grade', '').upper()
                if grade in ['F', 'FF', 'FAIL']:
                    failed_subjects_list.append({
                        'Exam': result['Exam'],
                        'Subject': sub.get('Course Name', 'Unknown'),
                        'Grade': grade
                    })

        # Helper to render prediction card
        def render_prediction_card():
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #818cf8; height: 100%; display: flex; align-items: center;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="metric-icon" style="background: rgba(129, 140, 248, 0.2); color: #818cf8;"><i class="fas fa-crystal-ball"></i></div>
                    <div>
                        <div class="metric-label">AI Prediction (Next SGPA)</div>
                        <div class="metric-value">{predicted_sgpa}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 5px;">Based on performance trend</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Helper to render failure card
        def render_failure_card():
            fail_items = "".join([f"""
                <div style="display: flex; justify-content: space-between; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; margin-bottom: 6px;">
                    <span style="color: #e2e8f0; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%;" title="{item['Subject']}">{item['Subject']}</span>
                    <span style="color: #f87171; font-weight: 700; font-size: 0.85rem;">{item['Grade']} <span style="color: #64748b; font-weight: 400; font-size: 0.7rem;">({item['Exam'].split(' ')[0]})</span></span>
                </div>""" for item in failed_subjects_list])
            
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #f87171; background: rgba(248, 113, 113, 0.05); height: 100%;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <i class="fas fa-exclamation-triangle" style="color: #f87171;"></i>
                    <h5 style="color: #f87171; margin: 0; font-size: 1rem;">Subject Failure Alerts</h5>
                </div>
                <div style="max-height: 120px; overflow-y: auto; padding-right: 5px;">{fail_items}</div>
            </div>
            """, unsafe_allow_html=True)

        if predicted_sgpa is not None and failed_subjects_list:
            c1, c2 = st.columns(2)
            with c1: render_prediction_card()
            with c2: render_failure_card()
        elif predicted_sgpa is not None:
            render_prediction_card()
        elif failed_subjects_list:
            render_failure_card()
        
        if not results_df.empty:
            st.markdown("### <i class='fas fa-chart-line'></i> Academic Progression", unsafe_allow_html=True)
            
            # SUBJECT GRADE PERFORMANCE (Height based)
            grade_point_map = {
                'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'P': 4, 
                'F': 3, 'FF': 3, 'FAIL': 3, 'Fail': 3, 'AB': 2, 'ABS': 2, 'IC': 2
            }
            
            subject_data = []
            for result in student_history['Results']:
                exam = result.get('Exam', '')
                for sub in result.get('Subjects', []):
                    name = sub.get('Course Name', sub.get('Course Code', 'Unknown'))
                    grade = sub.get('Grade', 'IC').strip()
                    gp = grade_point_map.get(grade, 0)
                    subject_data.append({
                        'Course Name': name,
                        'Grade': grade,
                        'Grade Point': gp,
                        'Exam': exam
                    })
            
            perf_df = pd.DataFrame(subject_data)

            if not perf_df.empty:
                st.markdown("#### <i class='fas fa-chart-bar'></i> Subject Performance Analysis", unsafe_allow_html=True)
                
                grade_colors = {
                    'O': '#27ae60', 'A+': '#2ecc71', 'A': '#58d68d', 
                    'B+': '#3498db', 'B': '#5dade2', 'C': '#aed6f1', 
                    'P': '#bdc3c7', 'F': '#ef4444', 'FF': '#ef4444', 
                    'Fail': '#ef4444', 'AB': '#94a3b8', 'ABS': '#94a3b8', 'IC': '#94a3b8'
                }
                
                fig_trend = px.bar(
                    perf_df, x='Course Name', y='Grade Point', color='Grade', 
                    title='Subject Grades (Height indicates performance)',
                    hover_data=['Exam', 'Grade'],
                    color_discrete_map=grade_colors,
                    template="plotly_dark",
                    barmode='group'
                )
                fig_trend.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)",
                    bargap=0.15,
                    yaxis=dict(
                        tickmode='array',
                        tickvals=[2, 3, 4, 5, 6, 7, 8, 9, 10],
                        ticktext=['AB', 'Fail', 'Pass', 'C', 'B', 'B+', 'A', 'A+', 'O'],
                        title='Grade'
                    )
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # SGPA LINE CHART
            fig = px.line(results_df, x='Exam', y='SGPA', markers=True, title="SGPA Growth", range_y=[0, 10], template="plotly_dark")
            fig.update_traces(line_color='#00d4ff')
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### <i class='fas fa-layer-group'></i> Semester Snapshots", unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, result in enumerate(student_history['Results']):
                with cols[idx % 3]:
                    status_color = "#4ade80" if result['Result'] == 'Pass' else "#f87171"
                    bg_color = "rgba(74, 222, 128, 0.1)" if result['Result'] == 'Pass' else "rgba(248, 113, 113, 0.1)"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 20px; border-left: 4px solid {status_color}; margin-bottom: 15px;">
                        <div style="font-weight: 700; font-size: 0.9rem; color: #e2e8f0; margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{result['Exam']}">{result['Exam']}</div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                            <div>
                                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">SGPA</div>
                                <div style="font-size: 1.6rem; font-weight: 800; color: {status_color}; line-height: 1;">{result['SGPA']}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Result</div>
                                <div style="font-size: 0.9rem; font-weight: 600; color: #f8fafc; background: {bg_color}; padding: 2px 8px; border-radius: 4px;">{result['Result']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("### <i class='fas fa-file-contract'></i> Detailed Transcripts", unsafe_allow_html=True)
            for i, result in enumerate(student_history['Results']):
                with st.expander(f"{result['Exam']} (SGPA: {result['SGPA']})"):
                    c1, c2 = st.columns([3, 1])
                    with c1: st.markdown(f"**Seat No:** `{result['Seat']}`")
                    with c2: st.markdown(f"**Credits:** `{result['Credits']}`")
                    
                    if result['Subjects']:
                        sub_df = pd.DataFrame(result['Subjects'])
                        st.dataframe(sub_df, use_container_width=True, hide_index=True)
                        
                        # EXCEL EXPORT FOR INDIVIDUAL SEMESTER
                        sem_excel = convert_df_to_excel(sub_df)
                        st.download_button(
                            label=f"📥 Download Transcript",
                            data=sem_excel,
                            file_name=f"{student_history['Name']}_{result['Exam']}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_sem_{i}"
                        )
    else:
        st.info("No detailed result history available.")

def render_overview_dashboard(analyzer, key_prefix="overview"):
    st.markdown("### <i class='fas fa-tachometer-alt'></i> Performance Overview", unsafe_allow_html=True)
    summary = analyzer.get_result_summary()
    
    # CUSTOM HTML METRIC CARDS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon"><i class="fas fa-users"></i></div><div class="metric-label">Total Students</div><div class="metric-value">{summary['total_students']}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color: #4ade80; background: rgba(74, 222, 128, 0.15);"><i class="fas fa-check-circle"></i></div><div class="metric-label">Passed</div><div class="metric-value">{summary['passed_students']}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color: #f87171; background: rgba(248, 113, 113, 0.15);"><i class="fas fa-times-circle"></i></div><div class="metric-label">Failed</div><div class="metric-value">{summary['failed_students']}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color: #fbbf24; background: rgba(251, 191, 36, 0.15);"><i class="fas fa-chart-bar"></i></div><div class="metric-label">Avg SGPA</div><div class="metric-value">{summary['average_sgpa']}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        valid_students = [s for s in analyzer.students_data if s.get('Has Valid SGPA')]
        sgpas = [s['SGPA'] for s in valid_students]
        if sgpas:
            fig = px.histogram(x=sgpas, nbins=20, title="SGPA Distribution", color_discrete_sequence=['#00d4ff'], template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        labels = ['Pass', 'Fail']
        values = [summary['passed_students'], summary['failed_students']]
        fig = px.pie(values=values, names=labels, title="Pass/Fail Ratio", color=labels, color_discrete_map={'Pass':'#00ff9d', 'Fail':'#ff4b4b'}, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Export Summary Data
    summary_df = pd.DataFrame([summary])
    excel_data = convert_df_to_excel(summary_df)
    st.download_button(
        label="📥 Download Overview Stats",
        data=excel_data,
        file_name="Class_Overview.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_overview"
    )

def render_top_performers(analyzer, key_prefix="top"):
    st.markdown("### <i class='fas fa-trophy'></i> Top Performers", unsafe_allow_html=True)
    top_students = analyzer.get_top_students(50) 
    if top_students:
        df = pd.DataFrame(top_students)
        display_cols = ['Seat No', 'Name', 'SGPA', 'Result Status', 'Passed Subjects']
        st.dataframe(df[display_cols].head(10), use_container_width=True)
        
        # EXPORT
        excel_data = convert_df_to_excel(df[display_cols])
        st.download_button(
            label="📥 Download Top Performers List (Excel)",
            data=excel_data,
            file_name="Top_Performers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_dl_top"
        )

def render_failed_analysis(analyzer, key_prefix="fail"):
    st.markdown("### <i class='fas fa-user-times'></i> Failure Analysis", unsafe_allow_html=True)
    failed = analyzer.get_failed_students()
    if not failed:
        st.success("🎉 All students passed!")
        return
    df = pd.DataFrame(failed)
    display_cols = ['Seat No', 'Name', 'SGPA_Raw', 'Passed Subjects']
    st.dataframe(df[display_cols], use_container_width=True)

    # EXPORT
    excel_data = convert_df_to_excel(df[display_cols])
    st.download_button(
        label="📥 Download Failed Students List (Excel)",
        data=excel_data,
        file_name="Failed_Students.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_fail"
    )

def render_subject_summary(analyzer, key_prefix="sub"):
    st.markdown("### <i class='fas fa-book'></i> Subject-wise Grade Distribution", unsafe_allow_html=True)
    
    summary_list = analyzer.get_subject_grade_summary()
    if not summary_list:
        st.info("No detailed subject data available.")
        return
        
    df = pd.DataFrame(summary_list)
    if 'Failure Rate (%)' in df.columns:
        df = df.sort_values(by='Failure Rate (%)', ascending=False)
    
    # Student Filter
    student_names = ["All Students"] + sorted(list(set([s.get('Name', 'Unknown') for s in analyzer.students_data])))
    selected_student = st.selectbox("Filter Subjects by Student", student_names, key=f"{key_prefix}_student_filter")
    
    if selected_student != "All Students":
        student = next((s for s in analyzer.students_data if s.get('Name') == selected_student), None)
        if student:
            student_subjects = [sub.get('Course Name') for sub in student.get('Subjects', [])]
            df = df[df['Course Name'].isin(student_subjects)]
    
    st.markdown("#### <i class='fas fa-sort-amount-down'></i> Critical Subjects (Highest Failure Rates)", unsafe_allow_html=True)
    
    # Dynamic column selection
    cols = [c for c in ['Course Name', 'Total Students', 'O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'Failure Rate (%)'] if c in df.columns]
    st.dataframe(df[cols].head(10), use_container_width=True)

    st.markdown("---")
    
    # Chart
    plot_grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
    plot_grades = [g for g in plot_grades if g in df.columns]
    
    if plot_grades:
        plot_df_source = df[['Course Name'] + plot_grades].copy()
        plot_df_long = plot_df_source.melt(id_vars=['Course Name'], value_vars=plot_grades, var_name='Grade', value_name='Count')
        plot_df_long = plot_df_long[plot_df_long['Count'] > 0]
        
        grade_colors = {
            'O': '#27ae60', 'A+': '#2ecc71', 'A': '#58d68d', 
            'B+': '#3498db', 'B': '#5dade2', 'C': '#aed6f1', 
            'P': '#bdc3c7', 'F': '#ef4444'
        }

        top_subjects_list = df['Course Name'].tolist()[:15]
        plot_df_long_filtered = plot_df_long[plot_df_long['Course Name'].isin(top_subjects_list)]

        if not plot_df_long_filtered.empty:
            fig = px.bar(
                plot_df_long_filtered, x='Course Name', y='Count', color='Grade',
                category_orders={"Grade": plot_grades},
                color_discrete_map=grade_colors,
                title="Grade Count by Course Name (Top 15 Subjects)",
                template="plotly_dark"
            )
            fig.update_layout(
                xaxis={'categoryorder': 'array', 'categoryarray': top_subjects_list}, 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
    # Export
    excel_data = convert_df_to_excel(df)
    st.download_button(
        label="📥 Download Subject Analysis",
        data=excel_data,
        file_name="Subject_Analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_sub"
    )

    st.markdown("---")
    st.markdown("### 🔬 Individual Subject Analysis", unsafe_allow_html=True)
    
    subject_names = sorted(df['Course Name'].unique().tolist())
    if subject_names:
        selected_subject = st.selectbox("Select Subject to Analyze", subject_names, key=f"{key_prefix}_subject_select")
    else:
        selected_subject = None
    
    if selected_subject:
        # Filter data for selected subject
        sub_stats = df[df['Course Name'] == selected_subject].iloc[0]
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="metric-box"><div class="metric-label">Total Students</div><div class="metric-value">{sub_stats['Total Students']}</div></div>""", unsafe_allow_html=True)
        
        passed = sub_stats['Total Students'] - sub_stats['F']
        pass_rate = (passed / sub_stats['Total Students'] * 100) if sub_stats['Total Students'] > 0 else 0
        with c2: st.markdown(f"""<div class="metric-box"><div class="metric-label">Pass Rate</div><div class="metric-value">{pass_rate:.1f}%</div></div>""", unsafe_allow_html=True)
        
        with c3: st.markdown(f"""<div class="metric-box"><div class="metric-label">Failures</div><div class="metric-value">{sub_stats['F']}</div></div>""", unsafe_allow_html=True)
        
        # Find highest grade achieved
        grades_order = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P']
        highest_grade = 'N/A'
        for g in grades_order:
            if g in sub_stats and sub_stats[g] > 0:
                highest_grade = g
                break
        with c4: st.markdown(f"""<div class="metric-box"><div class="metric-label">Top Grade</div><div class="metric-value">{highest_grade}</div></div>""", unsafe_allow_html=True)

        # Grade Distribution Chart for this subject
        st.markdown(f"#### 📊 Grade Distribution for {selected_subject}")
        plot_grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
        subject_grades_data = {g: sub_stats.get(g, 0) for g in plot_grades if g in sub_stats}
        
        if subject_grades_data:
            fig_sub = px.bar(
                x=list(subject_grades_data.keys()), 
                y=list(subject_grades_data.values()),
                labels={'x': 'Grade', 'y': 'Count'},
                title=f"Grade Distribution - {selected_subject}",
                template="plotly_dark",
                color=list(subject_grades_data.keys()),
                color_discrete_map={
                    'O': '#27ae60', 'A+': '#2ecc71', 'A': '#58d68d', 
                    'B+': '#3498db', 'B': '#5dade2', 'C': '#aed6f1', 
                    'P': '#bdc3c7', 'F': '#ef4444'
                }
            )
            fig_sub.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_sub, use_container_width=True)

        # Topper List Table
        st.markdown(f"#### 🏆 Top Performers in {selected_subject}")
        
        subject_students = []
        for s in analyzer.students_data:
            for sub in s.get('Subjects', []):
                if sub.get('Course Name') == selected_subject:
                    subject_students.append({'Seat No': s.get('Seat No'), 'Name': s.get('Name'), 'Grade': sub.get('Grade'), 'PRN': s.get('PRN'), 'SGPA': s.get('SGPA', 0)})
        
        if subject_students:
            df_sub_students = pd.DataFrame(subject_students)
            grade_priority = {g: i for i, g in enumerate(['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'FF', 'Fail', 'AB', 'ABS'])}
            df_sub_students['Grade_Rank'] = df_sub_students['Grade'].map(lambda x: grade_priority.get(x, 100))
            
            # Sort by Grade (Ascending Rank) then SGPA (Descending)
            df_sub_students = df_sub_students.sort_values(by=['Grade_Rank', 'SGPA'], ascending=[True, False])
            toppers_df = df_sub_students.head(10).drop(columns=['Grade_Rank'])
            
            st.dataframe(toppers_df, use_container_width=True)
            
            excel_data = convert_df_to_excel(toppers_df)
            st.download_button(
                label=f"📥 Download {selected_subject} Toppers",
                data=excel_data,
                file_name=f"{selected_subject}_Toppers.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}_dl_sub_toppers"
            )

def render_detailed_data(analyzer, key_prefix="detailed"):
    st.markdown("### <i class='fas fa-list'></i> Complete Student Registry", unsafe_allow_html=True)
    df = pd.DataFrame([ {k:v for k,v in s.items() if k!='Subjects'} for s in analyzer.students_data ])
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        min_sgpa = st.slider("Filter by Min SGPA", 0.0, 10.0, 0.0, key=f'{key_prefix}_min_sgpa_slider') 
    with c2: 
        status = st.selectbox("Filter by Status", ["All", "Pass", "Fail"], key=f'{key_prefix}_status_select') 
    with c3: 
        sort_order = st.selectbox("Sort Order", ["High to Low", "Low to High"], key=f'{key_prefix}_sort_select') 
        
    filtered = df[df['SGPA'] >= min_sgpa]
    if status != "All": filtered = filtered[filtered['Result Status'] == status]
    if sort_order == "High to Low": filtered = filtered.sort_values(by='SGPA', ascending=False)
    else: filtered = filtered.sort_values(by='SGPA', ascending=True)
    
    st.dataframe(filtered, use_container_width=True)

    # EXPORT
    excel_data = convert_df_to_excel(filtered)
    st.download_button(
        label="📥 Download Filtered Data (Excel)",
        data=excel_data,
        file_name="Detailed_Student_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_detailed"
    )

def render_college_overview(fm):
    st.markdown("### 🏛️ Institutional Performance Overview", unsafe_allow_html=True)
    
    with st.spinner("Aggregating institutional data..."):
        files = fm.get_all_result_files()
    
    if not files:
        st.info("No data available. Upload result files to see analytics.")
        return

    # --- AGGREGATION LOGIC ---
    dept_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'sgpa_sum': 0, 'sgpa_count': 0, 'files': 0})
    year_stats = defaultdict(lambda: {'total': 0, 'passed': 0})
    
    total_students = 0
    total_passed = 0
    total_sgpa_sum = 0
    total_sgpa_count = 0
    
    for f in files:
        dept = f.get('department', 'Uncategorized')
        year = f.get('year', 'Unknown')
        summary = f.get('summary', {})
        count = f.get('total_students', 0)
        passed = summary.get('passed_students', 0) if summary else 0
        avg_sgpa = summary.get('average_sgpa', 0) if summary else 0
        
        total_students += count
        total_passed += passed
        if count > 0:
            total_sgpa_sum += (avg_sgpa * count)
            total_sgpa_count += count
        dept_stats[dept]['total'] += count
        dept_stats[dept]['passed'] += passed
        if count > 0:
            dept_stats[dept]['sgpa_sum'] += (avg_sgpa * count)
            dept_stats[dept]['sgpa_count'] += count
        year_stats[year]['total'] += count
        year_stats[year]['passed'] += passed

    # Calculations
    overall_pass_rate = (total_passed / total_students * 100) if total_students else 0
    overall_avg_sgpa = (total_sgpa_sum / total_sgpa_count) if total_sgpa_count else 0
    
    # --- UI RENDERING ---
    
    # 1. Global Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon"><i class="fas fa-university"></i></div><div class="metric-label">Total Students</div><div class="metric-value">{total_students}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color:#4ade80"><i class="fas fa-graduation-cap"></i></div><div class="metric-label">Overall Pass Rate</div><div class="metric-value">{overall_pass_rate:.1f}%</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color:#fbbf24"><i class="fas fa-star"></i></div><div class="metric-label">Institutional Avg SGPA</div><div class="metric-value">{overall_avg_sgpa:.2f}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-box"><div class="metric-icon" style="color:#818cf8"><i class="fas fa-file-alt"></i></div><div class="metric-label">Exams Analyzed</div><div class="metric-value">{len(files)}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Departmental Analysis
    st.markdown("#### 🏢 Department-wise Performance")
    
    dept_data = []
    for d, stats in dept_stats.items():
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] else 0
        avg_sgpa = (stats['sgpa_sum'] / stats['sgpa_count']) if stats['sgpa_count'] else 0
        dept_data.append({'Department': d, 'Pass Rate (%)': round(pass_rate, 1), 'Avg SGPA': round(avg_sgpa, 2), 'Students': stats['total']})
    
    df_dept = pd.DataFrame(dept_data)
    
    if not df_dept.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_pass = px.bar(df_dept, x='Department', y='Pass Rate (%)', color='Department', title="Pass Percentage by Dept", template="plotly_dark")
            fig_pass.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_pass, use_container_width=True)
        
        with c2:
            fig_sgpa = px.bar(df_dept, x='Department', y='Avg SGPA', color='Department', title="Average SGPA by Dept", template="plotly_dark")
            fig_sgpa.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_sgpa, use_container_width=True)
            
    # 3. Year-wise Analysis
    st.markdown("#### 📅 Year-wise Progression")
    year_data = []
    for y, stats in year_stats.items():
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] else 0
        year_data.append({'Year': y, 'Pass Rate (%)': round(pass_rate, 1), 'Students': stats['total']})
    
    df_year = pd.DataFrame(year_data)
    year_order = {'FE': 1, 'SE': 2, 'TE': 3, 'BE': 4}
    df_year['Order'] = df_year['Year'].map(lambda x: year_order.get(x, 5))
    df_year = df_year.sort_values('Order')
    
    if not df_year.empty:
        fig_year = px.line(df_year, x='Year', y='Pass Rate (%)', markers=True, title="Pass Rate Trend across Years", template="plotly_dark")
        fig_year.update_traces(line_color='#a855f7', line_width=4)
        fig_year.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_range=[0, 100])
        st.plotly_chart(fig_year, use_container_width=True)

def render_advanced_analytics(analyzer, key_prefix="adv"):
    st.markdown("### 📈 Advanced Statistical Analysis", unsafe_allow_html=True)
    
    # 1. SGPA Statistics
    valid_students = [s for s in analyzer.students_data if s.get('Has Valid SGPA')]
    sgpas = [s['SGPA'] for s in valid_students]
    
    if sgpas:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("##### SGPA Distribution Statistics")
            st.write(f"**Mean SGPA:** {np.mean(sgpas):.2f}")
            st.write(f"**Median SGPA:** {np.median(sgpas):.2f}")
            try:
                mode_val = float(max(set(sgpas), key=sgpas.count))
                st.write(f"**Mode SGPA:** {mode_val:.2f}")
            except:
                st.write("**Mode SGPA:** N/A")
            st.write(f"**Standard Deviation:** {np.std(sgpas):.2f}")
            st.write(f"**Range:** {np.min(sgpas)} - {np.max(sgpas)}")
            
            p90 = np.percentile(sgpas, 90)
            p10 = np.percentile(sgpas, 10)
            st.markdown("---")
            st.write(f"**Top 10% Cutoff:** > {p90:.2f}")
            st.write(f"**Bottom 10% Cutoff:** < {p10:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_box = px.box(y=sgpas, title="SGPA Box Plot", template="plotly_dark")
            fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 2. Subject Heatmap
    st.markdown("### 🔥 Subject Grade Heatmap", unsafe_allow_html=True)
    summary_list = analyzer.get_subject_grade_summary()
    if summary_list:
        df_sub = pd.DataFrame(summary_list)
        grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
        available_grades = [g for g in grades if g in df_sub.columns]
        
        if available_grades:
            heatmap_data = df_sub.set_index('Course Name')[available_grades]
            fig_heat = px.imshow(
                heatmap_data, 
                labels=dict(x="Grade", y="Subject", color="Count"),
                x=available_grades,
                title="Grade Concentration Heatmap",
                template="plotly_dark",
                aspect="auto",
                color_continuous_scale='Viridis'
            )
            fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_heat, use_container_width=True)