from flask import Flask, render_template
import sqlite3

DB_FILE = "/Users/saranshahlawat/Desktop/Stevens/Semesters/Spring 2019/SSW-810/SSW-810-A/source/data_files/810_startup.db"

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello! Please use "/instructor_courses" after your base url for viewing the courses taught by instructors.'


@app.route('/instructor_courses')
def template_demo():
    db = sqlite3.connect(DB_FILE)
    query = "select i.CWID as Instructor_cwid, i.Name, i.Dept, g.Course, count(*) as Student_cnt from HW11_instructors i join HW11_grades g on i.CWID = g.Instructor_CWID group by i.Name, i.Dept, g.Course"
    data = db.execute(query)
    students = [{'cwid': cwid, 'name': name, 'dept': dept, 'course': course,
                 'student_cnt': student_cnt} for cwid, name, dept, course, student_cnt in data]

    return render_template('base.html',
                           title="Stevens Repository",
                           page_header="Stevens Student Repository",
                           page_sub_header="Number of students by course and instructor",
                           students=students)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
