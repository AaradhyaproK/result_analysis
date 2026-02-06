import streamlit as st
import PyPDF2
import re
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from typing import Dict, Optional

class AdvancedResultAnalyzer:
    def __init__(self):
        self.students_data = []
        self.raw_text = ""
    
    def extract_text_from_pdf(self, uploaded_file):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            self.raw_text = text
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None
    
    def parse_comprehensive_data(self, text):
        students = []
        blocks = re.split(r'(?=SEAT NO\.:)', text)
        
        for block in blocks:
            if "SEAT NO.:" not in block: continue
            try:
                seat_match = re.search(r'SEAT NO\.:\s*([A-Z0-9]+)', block)
                seat_no = seat_match.group(1) if seat_match else "Unknown"
                name_match = re.search(r'NAME\s*:\s*(.*?)\s+MOTHER', block)
                name = name_match.group(1).strip() if name_match else "Unknown"
                mother_match = re.search(r'MOTHER\s*:\s*(.*?)\s+PRN', block)
                mother = mother_match.group(1).strip() if mother_match else "Unknown"
                prn_match = re.search(r'PRN\s*:\s*([A-Z0-9]+)', block)
                prn = prn_match.group(1).strip() if prn_match else "Unknown"
                sgpa_match = re.search(r'(?:FIRST|SECOND|THIRD|FOURTH)?\s*YEAR\s*SGPA\s*:\s*([0-9\.]+|--)', block)
                sgpa_raw = sgpa_match.group(1) if sgpa_match else "0.0"
                try: sgpa = float(sgpa_raw)
                except: sgpa = 0.0
                credits_match = re.search(r'TOTAL CREDITS EARNED\s*:\s*(\d+)', block)
                credits = int(credits_match.group(1)) if credits_match else 0
                
                subjects = self.parse_subject_grades(block)
                passed_subjects = sum(1 for sub in subjects if sub['Grade'] not in ['F', 'FF', 'AB', 'IC', 'ABS', 'Fail'])
                total_subjects = len(subjects)
                has_valid_sgpa = sgpa > 0
                result_status = 'Pass' if has_valid_sgpa else 'Fail'
                
                students.append({
                    'Seat No': seat_no, 'Name': name, 'Mother Name': mother, 'PRN': prn,
                    'SGPA': sgpa, 'SGPA_Raw': sgpa_raw, 'Credits': credits,
                    'Subjects': subjects, 'Passed Subjects': passed_subjects,
                    'Total Subjects': total_subjects, 'Result Status': result_status,
                    'Has Valid SGPA': has_valid_sgpa
                })
            except Exception: continue
        return students
    
    def parse_subject_grades(self, block_text):
        subjects = []
        lines = block_text.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\d{5,}[A-Z]?', line):
                parts = line.split()
                if len(parts) > 6:
                    grade = parts[-5]
                    course_code = parts[0]
                    course_name = " ".join(parts[1:min(len(parts), 4)]) 
                    subjects.append({'Course Code': course_code, 'Course Name': course_name, 'Grade': grade})
        return subjects
    
    def get_result_summary(self):
        if not self.students_data: return {}
        total = len(self.students_data)
        passed = sum(1 for s in self.students_data if s['Result Status'] == 'Pass')
        valid_sgpa_students = [s for s in self.students_data if s.get('Has Valid SGPA')]
        avg_sgpa = sum(s['SGPA'] for s in valid_sgpa_students) / len(valid_sgpa_students) if valid_sgpa_students else 0
        return {
            'total_students': total, 'passed_students': passed,
            'failed_students': total - passed, 'average_sgpa': round(avg_sgpa, 2),
            'pass_percentage': round((passed / total * 100) if total > 0 else 0, 1)
        }

    def get_top_students(self, n=10):
        valid = [s for s in self.students_data if s.get('Has Valid SGPA')]
        return sorted(valid, key=lambda x: x['SGPA'], reverse=True)[:n]
    
    def get_failed_students(self):
        return [s for s in self.students_data if s['Result Status'] == 'Fail']
        
    def predict_next_sgpa(self, student_history: Dict) -> Optional[float]:
        results = student_history.get('Results', [])
        if len(results) < 2: return None
        sorted_results = results 
        X = np.array([i for i, r in enumerate(sorted_results)]).reshape(-1, 1)
        Y = np.array([r.get('SGPA', 0.0) for r in sorted_results])
        model = LinearRegression()
        model.fit(X, Y)
        next_index = len(results)
        prediction = model.predict([[next_index]])
        return round(max(0.0, min(10.0, prediction[0])), 2)

    def get_subject_grade_summary(self) -> Dict:
        if not self.students_data: return {}
        subject_grades = defaultdict(lambda: defaultdict(int))
        course_code_to_name = {}
        
        for student in self.students_data:
            for subject in student.get('Subjects', []):
                course_code = subject.get('Course Code')
                course_name = subject.get('Course Name', 'Unknown Subject')
                grade = subject.get('Grade', 'N/A')
                if course_code and grade and grade not in ['IC', 'ABS', 'N/A']:
                    course_code_to_name[course_code] = course_name 
                    if grade in ['FF', 'Fail']: grade = 'F' 
                    subject_grades[course_code]['Total Students'] += 1
                    subject_grades[course_code][grade] += 1
        
        summary_list = []
        for code, data in subject_grades.items():
            row = {'Course Name': course_code_to_name.get(code, code), 'Total Students': data.pop('Total Students')}
            grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
            for g in grades: row[g] = data.get(g, 0)
            failures = row['F']
            row['Failure Rate (%)'] = round((failures / row['Total Students']) * 100, 1) if row['Total Students'] > 0 else 0
            summary_list.append(row)
        return summary_list