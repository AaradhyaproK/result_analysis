import streamlit as st
import requests
import datetime
import hashlib
import time
from typing import List, Dict
from firebase_config import FIREBASE_CONFIG


FIREBASE_REST_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents"

class FirebaseManager:
    def __init__(self):
        self.id_token = st.session_state.get('id_token')
        self.user_id = st.session_state.get('user_id')
    
    def _set_session_token(self, token, uid):
        self.id_token = token
        self.user_id = uid
        st.session_state['id_token'] = token
        st.session_state['user_id'] = uid

    def sign_in_with_email_password(self, email: str, password: str):
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
            auth_data = {"email": email, "password": password, "returnSecureToken": True}
            response = requests.post(auth_url, json=auth_data)
            result = response.json()
            if response.status_code == 200:
                self._set_session_token(result.get('idToken'), result.get('localId'))
                return True, result
            else:
                return False, result.get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def create_user_with_email_password(self, email: str, password: str, name: str):
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['apiKey']}"
            auth_data = {"email": email, "password": password, "displayName": name, "returnSecureToken": True}
            response = requests.post(auth_url, json=auth_data)
            result = response.json()
            if response.status_code == 200:
                self._set_session_token(result.get('idToken'), result.get('localId'))
                return True, result
            else:
                return False, result.get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def firestore_request(self, method, path, data=None):
        if not self.id_token: return None
        url = f"{FIREBASE_REST_URL}/{path}"
        headers = {"Authorization": f"Bearer {self.id_token}", "Content-Type": "application/json"}
        try:
            if method == "GET": response = requests.get(url, headers=headers)
            elif method == "POST": response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH": response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE": response = requests.delete(url, headers=headers)
            else: return None
            
            if response.status_code not in [200, 201, 409]:
                if response.status_code != 404:
                    st.error(f"DB Error {response.status_code}: {response.text}")
                return None
            return response.json()
        except Exception as e:
            st.error(f"Request Exception: {str(e)}")
            return None
    
    def _to_firestore_value(self, value):
        if value is None: return {"nullValue": None}
        elif isinstance(value, bool): return {"booleanValue": value}
        elif isinstance(value, int): return {"integerValue": str(value)}
        elif isinstance(value, float): return {"doubleValue": value}
        elif isinstance(value, str): return {"stringValue": value}
        elif isinstance(value, datetime.datetime): return {"timestampValue": value.isoformat() + "Z"}
        elif isinstance(value, list): return {"arrayValue": {"values": [self._to_firestore_value(v) for v in value]}}
        elif isinstance(value, dict): return {"mapValue": {"fields": {k: self._to_firestore_value(v) for k, v in value.items()}}}
        else: return {"stringValue": str(value)}

    def create_user(self, email: str, password: str, role: str, name: str):
        success, result = self.create_user_with_email_password(email, password, name)
        if not success:
            st.error(f"❌ Auth Creation Failed: {result}")
            return None
        
        user_id = result.get('localId')
        user_data = {
            "fields": {
                "email": self._to_firestore_value(email),
                "role": self._to_firestore_value(role.lower()),
                "name": self._to_firestore_value(name),
                "user_id": self._to_firestore_value(user_id),
                "created_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "last_login": self._to_firestore_value(datetime.datetime.utcnow())
            }
        }
        
        response = self.firestore_request("POST", f"users?documentId={user_id}", user_data)
        if not response or 'error' in response:
             response = self.firestore_request("PATCH", f"users/{user_id}", user_data)

        if response:
            return user_id
        return None
    
    def verify_user(self, email: str, password: str):
        success, result = self.sign_in_with_email_password(email, password)
        if not success: return False, f"Login failed: {result}"
        
        user_doc = self.firestore_request("GET", f"users/{self.user_id}")
        if not user_doc: return False, "User profile not found."
        
        role = user_doc.get('fields', {}).get('role', {}).get('stringValue', '')
        if not role: return False, "User role missing."

        user_data = {
            'email': user_doc.get('fields', {}).get('email', {}).get('stringValue', ''),
            'role': role,
            'name': user_doc.get('fields', {}).get('name', {}).get('stringValue', ''),
            'uid': self.user_id
        }
        return True, user_data

    def save_result_data(self, file_name: str, exam_tag: str, department: str, year: str, students_data: List[Dict], uploaded_by: str, summary: Dict):
        if not self.id_token: return None
        
        batch_data = {
            "fields": {
                "file_name": self._to_firestore_value(file_name),
                "exam_tag": self._to_firestore_value(exam_tag),
                "department": self._to_firestore_value(department),
                "year": self._to_firestore_value(year),
                "uploaded_by": self._to_firestore_value(uploaded_by),
                "uploaded_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "total_students": self._to_firestore_value(len(students_data)),
                "students_data": self._to_firestore_value(students_data),
                "summary": self._to_firestore_value(summary)
            }
        }
        
        doc_id = f"result_{int(time.time())}_{hashlib.md5(file_name.encode()).hexdigest()[:10]}"
        with st.spinner("Saving data to Cloud..."):
            result = self.firestore_request("POST", f"result_files?documentId={doc_id}", batch_data)
        
        if result:
            st.success("Success! Data archived securely.")
            return doc_id
        return None

    def get_all_result_files(self):
        if not self.id_token: return []
        result = self.firestore_request("GET", "result_files")
        if not result or 'documents' not in result: return []
        
        files = []
        for doc in result['documents']:
            file_data = self._convert_from_firestore(doc)
            file_data['id'] = doc['name'].split('/')[-1]
            files.append(file_data)
        return sorted(files, key=lambda x: x.get('uploaded_at', ''), reverse=True)

    @st.cache_data(ttl=3600)
    def get_all_student_identifiers(_self):
        files = _self.get_all_result_files()
        identifiers = {}
        for file_data in files:
            for student in file_data.get('students_data', []):
                prn = student.get('PRN', '').strip()
                name = student.get('Name', '').strip()
                if prn:
                    identifiers[prn] = name
        return identifiers

    def get_student_history(self, search_term: str):
        files = self.get_all_result_files()
        student_history = {}
        search_term = search_term.lower().strip()
        
        for file_data in files:
            exam_tag = file_data.get('exam_tag', file_data.get('file_name', 'Unknown Exam'))
            upload_date = file_data.get('uploaded_at')
            
            for student in file_data.get('students_data', []):
                s_name = student.get('Name', '').lower()
                s_prn = student.get('PRN', '').strip()
                is_match = (search_term == s_prn.lower()) or (search_term in s_name)
                
                if is_match:
                    if s_prn not in student_history:
                        student_history[s_prn] = {
                            'Name': student.get('Name'),
                            'PRN': s_prn,
                            'Mother': student.get('Mother Name'),
                            'Results': []
                        }
                    
                    result_entry = {
                        'Exam': exam_tag,
                        'Date': upload_date,
                        'SGPA': student.get('SGPA', 0),
                        'Result': student.get('Result Status'),
                        'Credits': student.get('Credits'),
                        'Seat': student.get('Seat No'),
                        'Subjects': student.get('Subjects', [])
                    }
                    if isinstance(result_entry['Date'], str):
                        try:
                            result_entry['Date'] = datetime.datetime.fromisoformat(result_entry['Date'].replace('Z', '+00:00'))
                        except:
                            pass
                    student_history[s_prn]['Results'].append(result_entry)
        
        for prn in student_history:
            student_history[prn]['Results'].sort(key=lambda x: x['Date'] if isinstance(x['Date'], datetime.datetime) else datetime.datetime.min)
            
        return list(student_history.values())

    def _convert_from_firestore(self, doc):
        fields = doc.get('fields', {})
        result = {}
        for key, value in fields.items():
            if 'stringValue' in value: result[key] = value['stringValue']
            elif 'integerValue' in value: result[key] = int(value['integerValue'])
            elif 'doubleValue' in value: result[key] = float(value['doubleValue'])
            elif 'booleanValue' in value: result[key] = value['booleanValue']
            elif 'timestampValue' in value:
                try: result[key] = datetime.datetime.fromisoformat(value['timestampValue'].replace('Z', '+00:00'))
                except: result[key] = value['timestampValue']
            elif 'arrayValue' in value:
                vals = value['arrayValue'].get('values', [])
                result[key] = [self._convert_single_value(i) for i in vals]
            elif 'mapValue' in value:
                result[key] = self._convert_from_firestore({'fields': value['mapValue']['fields']})
        return result

    def _convert_single_value(self, value):
        if 'stringValue' in value: return value['stringValue']
        elif 'integerValue' in value: return int(value['integerValue'])
        elif 'doubleValue' in value: return float(value['doubleValue'])
        elif 'booleanValue' in value: return value['booleanValue']
        elif 'mapValue' in value: return self._convert_from_firestore({'fields': value['mapValue']['fields']})
        return None