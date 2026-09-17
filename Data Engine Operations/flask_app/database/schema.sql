-- جدول بيانات المرضى والحالات النفسية
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول سجلات الصدمات والأحداث
CREATE TABLE IF NOT EXISTS trauma_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(50),
    trauma_type VARCHAR(100),
    description TEXT,
    embedding TEXT, -- تخزين المتجهات 1536-vector بصيغة JSON string
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- جدول التقييمات والتشخيصات الطبية
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(50),
    diagnostic_summary TEXT,
    ptsd_severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'New',
    embedding TEXT, -- تخزين المتجهات 1536-vector بصيغة JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);