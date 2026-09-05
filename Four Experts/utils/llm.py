import sqlite3
import os

def fill_template(system_prompt, user_query, context=""):
    """تعبئة المحفز الموحد للنماذج"""
    return f"System: {system_prompt}\nContext: {context}\nUser Query: {user_query}"

def database_read_expert(query):
    """خبير القراءة: يولد استعلامات SQL للقراءة فقط"""
    print(f"\n🔍 [Database Read Expert] Processing query: '{query}'")
    sql_query = f"SELECT * FROM family_records WHERE details LIKE '%{query}%';"
    print(f"📄 [Generated SQL Query]: {sql_query}")
    return {
        "expert": "Database Read Expert",
        "type": "read",
        "sql": sql_query,
        "message": f"Executed SQL search for: {query}"
    }

def database_write_expert(query):
    """خبير الكتابة: يولد كود Python لإضافة/تعديل البيانات"""
    print(f"\n✏️ [Database Write Expert] Processing write request: '{query}'")
    python_code = f"# Python DB Write Action\n# Action executed for: {query}\nprint('Database successfully updated!')"
    print(f"🐍 [Generated Python Code]:\n{python_code}")
    return {
        "expert": "Database Write Expert",
        "type": "write",
        "code": python_code,
        "message": f"Successfully processed write action: {query}"
    }

def database_semantic_search_expert(query):
    """خبير البحث الدلالي: يحل الاختصارات ويبحث بالمعنى"""
    print(f"\n🧠 [Database Semantic Search Expert] Vector searching for: '{query}'")
    
    # حل الاختصارات الشائعة مثل MSU
    resolved_query = query
    if "msu" in query.lower():
        resolved_query = query.lower().replace("msu", "Michigan State University")
        print(f"💡 [Abbreviation Resolved]: MSU -> Michigan State University")
        
    return {
        "expert": "Database Semantic Search Expert",
        "type": "semantic",
        "resolved_query": resolved_query,
        "results": [f"Matched record for: {resolved_query}"]
    }

def orchestrator_route(user_query):
    """الموجه الرئيسي Orchestrator: يحدد الخبير المناسب أو يتعامل مع التأكيد البشري"""
    print(f"\n🎯 [Orchestrator] Analyzing Request: '{user_query}'")
    
    query_lower = user_query.lower()
    
    # 1. نظام التأكيد البشري (Human Validation Workflow) للعمليات الحساسة
    if "delete" in query_lower or "حذف" in query_lower:
        print("⚠️ [Orchestrator] Action requires Human Confirmation!")
        return {
            "expert": "Orchestrator",
            "status": "requires_confirmation",
            "message": "Are you sure you want to proceed with this deletion? (Reply 'yes' or 'no')"
        }
        
    # 2. التوجيه لخبير البحث الدلالي
    if "msu" in query_lower or "skill" in query_lower or "مهار" in query_lower:
        return database_semantic_search_expert(user_query)
        
    # 3. التوجيه لخبير الكتابة
    elif "add" in query_lower or "إضافة" in query_lower or "update" in query_lower:
        return database_write_expert(user_query)
        
    # 4. التوجيه التلقائي لخبير القراءة
    else:
        return database_read_expert(user_query)