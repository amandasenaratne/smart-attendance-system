from attendance.attendance_service import process_recognized_face

print("Testing attendance module...")

process_recognized_face("Ishara")
process_recognized_face("Ishara")   # duplicate
process_recognized_face("Nimali")



