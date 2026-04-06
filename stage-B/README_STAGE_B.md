# 🔷 שלב ב': שאילתות ואילוצים - דוח מפורט

## 📌 מבוא לשלב ב'
בשלב זה ביצענו תשאול מעמיק של בסיס הנתונים באמצעות שאילתות מתקדמות, הוספנו אילוצים עסקיים, והדגמנו ניהול עסקאות (Transactions) עם COMMIT ו-ROLLBACK.

### קבצי שלב ב':
- `Queries.sql` - 8 שאילתות SELECT + 3 UPDATE + 3 DELETE
- `Constraints.sql` - 8 אילוצים עם ALTER TABLE וניסיונות הפרה
- `RollbackCommit.sql` - הדגמות של ROLLBACK ו-COMMIT
- `backup2.sql` - גיבוי מעודכן של בסיס הנתונים

---

## 🔍 PAIR 1: Workload Distribution per Station (JOIN vs CTE)

### PAIR 1A: Using JOIN + GROUP BY - קוד, הרצה ותוצאה
![S2_pair1a_code.png](../screenshots/screenshots-S2/S2_pair1a_code.png)
![S2_pair1a_execution.png](../screenshots/screenshots-S2/S2_pair1a_execution.png)
![S2_pair1a_result.png](../screenshots/screenshots-S2/S2_pair1a_result.png)

### PAIR 1B: Using CTE - קוד, הרצה ותוצאה
![S2_pair1b_code.png](../screenshots/screenshots-S2/S2_pair1b_code.png)
![S2_pair1b_execution.png](../screenshots/screenshots-S2/S2_pair1b_execution.png)
![S2_pair1b_result.png](../screenshots/screenshots-S2/S2_pair1b_result.png)

**הבדל יעילות:**
- **PAIR 1A (JOIN):** סריקה ישירה, מהיר עם indexes, כ-1 pass בלבד
- **PAIR 1B (CTE):** קריא יותר, ביצועים דומים עם indexes טובים

---

## 🔍 PAIR 2: High-Priority Chefs (IN vs EXISTS)

### PAIR 2A: Using IN - קוד, הרצה ותוצאה
![S2_pair2a_code.png](../screenshots/screenshots-S2/S2_pair2a_code.png)
![S2_pair2a_execution.png](../screenshots/screenshots-S2/S2_pair2a_execution.png)
![S2_pair2a_result.png](../screenshots/screenshots-S2/S2_pair2a_result.png)

### PAIR 2B: Using EXISTS - קוד, הרצה ותוצאה
![S2_pair2b_code.png](../screenshots/screenshots-S2/S2_pair2b_code.png)
![S2_pair2b_execution.png](../screenshots/screenshots-S2/S2_pair2b_execution.png)
![S2_pair2b_result.png](../screenshots/screenshots-S2/S2_pair2b_result.png)

**הבדל יעילות:**
- **PAIR 2A (IN):** יוצר רשימה זמנית, טוב עם תוצאה קטנה
- **PAIR 2B (EXISTS):** קורלטיבי, מוצא רק הימצאות, יעיל עם תוצאה גדולה

---

## 🔍 PAIR 3: Order Duration (EXTRACT vs DATE_TRUNC)

### PAIR 3A: Using EXTRACT - קוד, הרצה ותוצאה
![S2_pair3a_code.png](../screenshots/screenshots-S2/S2_pair3a_code.png)
![S2_pair3a_execution.png](../screenshots/screenshots-S2/S2_pair3a_execution.png)
![S2_pair3a_result.png](../screenshots/screenshots-S2/S2_pair3a_result.png)

### PAIR 3B: Using DATE_TRUNC - קוד, הרצה ותוצאה
![S2_pair3b_code.png](../screenshots/screenshots-S2/S2_pair3b_code.png)
![S2_pair3b_execution.png](../screenshots/screenshots-S2/S2_pair3b_execution.png)
![S2_pair3b_result.png](../screenshots/screenshots-S2/S2_pair3b_result.png)

**הבדל יעילות:**
- **PAIR 3A (EXTRACT):** גמישות מקסימלית, כל חלק בנפרד
- **PAIR 3B (DATE_TRUNC):** מצוין לקיבוץ זמנים, timezone-safe

---

## 🔍 PAIR 4: Monthly Station Trends (EXTRACT vs DATE_TRUNC)

### PAIR 4A: Using EXTRACT - קוד, הרצה ותוצאה
![S2_pair4a_code.png](../screenshots/screenshots-S2/S2_pair4a_code.png)
![S2_pair4a_execution.png](../screenshots/screenshots-S2/S2_pair4a_execution.png)
![S2_pair4a_result.png](../screenshots/screenshots-S2/S2_pair4a_result.png)

### PAIR 4B: Using DATE_TRUNC - קוד, הרצה ותוצאה
![S2_pair4b_code.png](../screenshots/screenshots-S2/S2_pair4b_code.png)
![S2_pair4b_execution.png](../screenshots/screenshots-S2/S2_pair4b_execution.png)
![S2_pair4b_result.png](../screenshots/screenshots-S2/S2_pair4b_result.png)

**הבדל יעילות:**
- **PAIR 4A (EXTRACT):** מספר קריאות לפונקציה
- **PAIR 4B (DATE_TRUNC):** פחות קריאות, consistent bucketing

---

## 📊 QUERY 5: Hygiene Inspection Scores
![S2_query5_code.png](../screenshots/screenshots-S2/S2_query5_code.png)
![S2_query5_execution.png](../screenshots/screenshots-S2/S2_query5_execution.png)
![S2_query5_result.png](../screenshots/screenshots-S2/S2_query5_result.png)

---

## 📊 QUERY 6: Chef Productivity
![S2_query6_code.png](../screenshots/screenshots-S2/S2_query6_code.png)
![S2_query6_execution.png](../screenshots/screenshots-S2/S2_query6_execution.png)
![S2_query6_result.png](../screenshots/screenshots-S2/S2_query6_result.png)

---

## 📊 QUERY 7: Active Tasks by Priority
![S2_query7_code.png](../screenshots/screenshots-S2/S2_query7_code.png)
![S2_query7_execution.png](../screenshots/screenshots-S2/S2_query7_execution.png)
![S2_query7_result.png](../screenshots/screenshots-S2/S2_query7_result.png)

---

## 📊 QUERY 8: Temperature Anomalies
![S2_query8_code.png](../screenshots/screenshots-S2/S2_query8_code.png)
![S2_query8_execution.png](../screenshots/screenshots-S2/S2_query8_execution.png)
![S2_query8_result.png](../screenshots/screenshots-S2/S2_query8_result.png)

---

## ✏️ UPDATE 1: Orders Ready
**לפני:** ![S2_update1_before.png](../screenshots/screenshots-S2/S2_update1_before.png)
**הרצה:** ![S2_update1_execution.png](../screenshots/screenshots-S2/S2_update1_execution.png)
**אחרי:** ![S2_update1_after.png](../screenshots/screenshots-S2/S2_update1_after.png)

---

## ✏️ UPDATE 2: Chef Station Assignment
**לפני:** ![S2_update2_before.png](../screenshots/screenshots-S2/S2_update2_before.png)
**הרצה:** ![S2_update2_execution.png](../screenshots/screenshots-S2/S2_update2_execution.png)
**אחרי:** ![S2_update2_after.png](../screenshots/screenshots-S2/S2_update2_after.png)

---

## ✏️ UPDATE 3: Next Inspection Date
**לפני:** ![S2_update3_before.png](../screenshots/screenshots-S2/S2_update3_before.png)
**הרצה:** ![S2_update3_execution.png](../screenshots/screenshots-S2/S2_update3_execution.png)
**אחרי:** ![S2_update3_after.png](../screenshots/screenshots-S2/S2_update3_after.png)

---

## 🗑️ DELETE 1: Old Cancelled Orders
**לפני:** ![S2_delete1_before.png](../screenshots/screenshots-S2/S2_delete1_before.png)
**הרצה:** ![S2_delete1_execution.png](../screenshots/screenshots-S2/S2_delete1_execution.png)
**אחרי:** ![S2_delete1_after.png](../screenshots/screenshots-S2/S2_delete1_after.png)

---

## 🗑️ DELETE 2: Duplicate Prep Logs
**לפני:** ![S2_delete2_before.png](../screenshots/screenshots-S2/S2_delete2_before.png)
**הרצה:** ![S2_delete2_execution.png](../screenshots/screenshots-S2/S2_delete2_execution.png)
**אחרי:** ![S2_delete2_after.png](../screenshots/screenshots-S2/S2_delete2_after.png)

---

## 🗑️ DELETE 3: Tasks for Cancelled Orders
**לפני:** ![S2_delete3_before.png](../screenshots/screenshots-S2/S2_delete3_before.png)
**הרצה:** ![S2_delete3_execution.png](../screenshots/screenshots-S2/S2_delete3_execution.png)
**אחרי:** ![S2_delete3_after.png](../screenshots/screenshots-S2/S2_delete3_after.png)

---

## 🔒 CONSTRAINT 1: Finish Time After Start
**ALTER:** ![S2_constraint1_alter.png](../screenshots/screenshots-S2/S2_constraint1_alter.png)
**הפרה:** ![S2_constraint1_violation.png](../screenshots/screenshots-S2/S2_constraint1_violation.png)
**שגיאה:** ![S2_constraint1_error.png](../screenshots/screenshots-S2/S2_constraint1_error.png)

---

## 🔒 CONSTRAINT 2: Positive Prep Time
**ALTER:** ![S2_constraint2_alter.png](../screenshots/screenshots-S2/S2_constraint2_alter.png)
**הפרה:** ![S2_constraint2_violation.png](../screenshots/screenshots-S2/S2_constraint2_violation.png)
**שגיאה:** ![S2_constraint2_error.png](../screenshots/screenshots-S2/S2_constraint2_error.png)

---

## 🔒 CONSTRAINT 3: Next Inspection After Current
**ALTER:** ![S2_constraint3_alter.png](../screenshots/screenshots-S2/S2_constraint3_alter.png)
**הפרה:** ![S2_constraint3_violation.png](../screenshots/screenshots-S2/S2_constraint3_violation.png)
**שגיאה:** ![S2_constraint3_error.png](../screenshots/screenshots-S2/S2_constraint3_error.png)

---

## 🔒 CONSTRAINT 4: Valid Task Status
**ALTER:** ![S2_constraint4_alter.png](../screenshots/screenshots-S2/S2_constraint4_alter.png)
**הפרה:** ![S2_constraint4_violation.png](../screenshots/screenshots-S2/S2_constraint4_violation.png)
**שגיאה:** ![S2_constraint4_error.png](../screenshots/screenshots-S2/S2_constraint4_error.png)

---

## 🔒 CONSTRAINT 5: Unique Station Names
**ALTER:** ![S2_constraint5_alter.png](../screenshots/screenshots-S2/S2_constraint5_alter.png)
**הפרה:** ![S2_constraint5_violation.png](../screenshots/screenshots-S2/S2_constraint5_violation.png)
**שגיאה:** ![S2_constraint5_error.png](../screenshots/screenshots-S2/S2_constraint5_error.png)

---

## 🔒 CONSTRAINT 6: Hire Date Not Future
**ALTER:** ![S2_constraint6_alter.png](../screenshots/screenshots-S2/S2_constraint6_alter.png)
**הפרה:** ![S2_constraint6_violation.png](../screenshots/screenshots-S2/S2_constraint6_violation.png)
**שגיאה:** ![S2_constraint6_error.png](../screenshots/screenshots-S2/S2_constraint6_error.png)

---

## 🔒 CONSTRAINT 7: Priority Level (1-5)
**הפרה:** ![S2_constraint7_violation.png](../screenshots/screenshots-S2/S2_constraint7_violation.png)
**שגיאה:** ![S2_constraint7_error.png](../screenshots/screenshots-S2/S2_constraint7_error.png)

---

## 🔒 CONSTRAINT 8: Cleanliness Score (1.0-10.0)
**הפרה:** ![S2_constraint8_violation.png](../screenshots/screenshots-S2/S2_constraint8_violation.png)
**שגיאה:** ![S2_constraint8_error.png](../screenshots/screenshots-S2/S2_constraint8_error.png)

---

## 🔄 ROLLBACK - Transaction Undo
![S2_rollback_step1.png](../screenshots/screenshots-S2/S2_rollback_step1.png)
![S2_rollback_step2.png](../screenshots/screenshots-S2/S2_rollback_step2.png)
![S2_rollback_step3.png](../screenshots/screenshots-S2/S2_rollback_step3.png)

---

## 🔄 COMMIT - Transaction Permanent
![S2_commit_step1.png](../screenshots/screenshots-S2/S2_commit_step1.png)
![S2_commit_step2.png](../screenshots/screenshots-S2/S2_commit_step2.png)
![S2_commit_step3.png](../screenshots/screenshots-S2/S2_commit_step3.png)

---

**סטטוס:** ✅ שלב ב' הושלם
**עדכון:** 06/04/2026
