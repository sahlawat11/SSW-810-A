"""
@date: Created on Mon April 17 14:12:11 2019

@author: Saransh Ahlawat

@description: Python program to read student, instructor and grades file and create summary for students and instructors.
"""

import unittest, os
import sqlite3
from collections import defaultdict
from prettytable import PrettyTable

DB_FILE = "/Users/saranshahlawat/Desktop/Stevens/Semesters/Spring 2019/SSW-810/SSW-810-A/source/data_files/810_startup.db"

class Major:

    def __init__(self, major):
        self.major = major
        self.required_courses = set()
        self.required_electives = set()

    def add_course(self, course, flag):
        if flag == "R":
            self.required_courses.add(course)
        elif flag == "E":
            self.required_electives.add(course)

    def get_required_courses(self, courses_completed):
        result_courses = []
        result_electives = []
        for course in self.required_courses:
            if course not in courses_completed:
                result_courses.append(course)
        
        for elective in self.required_electives:
            if elective not in courses_completed:
                result_electives.append(elective)
            else:
                result_electives = []
                break
        
        return result_courses, result_electives


    def details(self):
        return [self.major, sorted(self.required_courses), sorted(self.required_electives)]

    @staticmethod
    def fields():
        return ["Dept", "Required", "Electives"]


class Student:

    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = dict()
        self.required_courses = list()
        self.required_electives = list()


    def add_course(self, course, grade):
        if grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']:
            self.courses[course] = grade


    def details(self):
        return [self.cwid, self.name, self.major, sorted(self.courses.keys()), sorted(self.required_courses), sorted(self.required_electives)]

    @staticmethod
    def fields():
        return ["CWID", "Name", "Major", "Completed Courses", "Remaining Required", "Remaining Electives"]


class StudentTest(unittest.TestCase):
    def test_init(self):
        student_1 = Student("12345", "Jack", "Computer Science")
        self.assertEqual(student_1.cwid, "12345")
        self.assertEqual(student_1.name, "Jack")
        self.assertEqual(student_1.major, "Computer Science")
        self.assertEqual(student_1.courses, {})
        self.assertEqual(student_1.required_courses, [])
        self.assertEqual(student_1.required_electives, [])
        

    def test_add_course(self):
        student_1 = Student("12345", "Jack", "Computer Science")
        student_1.add_course("SSW 567", "A")
        student_1.add_course("SSW 564", "A-")
        self.assertEqual(student_1.courses, {'SSW 567': 'A', 'SSW 564': 'A-'})
    
    def test_details(self):
        student_1 = Student("10103", "Baldwin, C", "SFEN")
        student_1.add_course("SSW 567", "A")
        student_1.add_course("SSW 564", "A-")
        student_2 = Student("10115", "CS 545", "A")
        student_2.add_course("SSW 540", "A-")
        student_2.add_course("SSW 810", "A")

        self.assertEqual(student_1.details(), ['10103', 'Baldwin, C', 'SFEN', ['SSW 564', 'SSW 567'], [], []])
        self.assertEqual(student_1.details(), ['10103', 'Baldwin, C', 'SFEN', ['SSW 564', 'SSW 567'], [], []])


class Instructor:

    def __init__(self, cwid, name, department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.courses = defaultdict(int)


    def add_course(self, course):
        self.courses[course] += 1

    def details(self):
        for course, students in self.courses.items():
            yield [self.cwid, self.name, self.department, course, students]

    @staticmethod
    def fields():
        return ["CWID", "Name", "Dept", "Course", "Students"]

class InstructorTest(unittest.TestCase):
    def test_init(self):
        instructor_1 = Instructor("12345", "Jack", "Computer Science")

        self.assertEqual(instructor_1.cwid, "12345")
        self.assertEqual(instructor_1.name, "Jack")
        self.assertEqual(instructor_1.department, "Computer Science")
        self.assertEqual(instructor_1.courses, {})
        self.assertEqual(instructor_1.courses['test_key'], 0)

    
    def test_add_course(self):
        instructor_1 = Instructor("12345", "Jack", "Computer Science")
        instructor_1.add_course("SSW 567")
        instructor_1.add_course("SSW 564")
        instructor_1.add_course("SSW 567")

        self.assertEqual(instructor_1.courses, {'SSW 567': 2, 'SSW 564': 1})


class Repository:

    def __init__(self, dir):
        self.students = dict()
        self.instructors = dict()
        self.majors = dict()
        self.add_students(os.path.join(dir, "students.txt"))
        self.add_instructors(os.path.join(dir, "instructors.txt"))
        self.add_grades(os.path.join(dir, "grades.txt"))
        self.add_major_courses(os.path.join(dir, "majors.txt"))
        self.add_remaining_courses()
        self.major_pt()
        self.student_pt()
        self.instructor_pt()


    def add_students(self, students_file_path):
        for cwid, name, major in file_reader(students_file_path, 3, "\t"):
            if cwid not in self.students:
                self.students[cwid] = Student(cwid, name, major)

    
    def add_major_courses(self, major_file_path):
        for major, flag, course in file_reader(major_file_path, 3, "\t"):
            if major not in self.majors:
                self.majors[major] = Major(major)
            self.majors[major].add_course(course, flag)

    def add_remaining_courses(self):
        for student in self.students.values():
            student.required_courses, student.required_electives = self.majors[student.major].get_required_courses(student.courses)


    def add_instructors(self, instructor_file_path):
        for cwid, name, department in file_reader(instructor_file_path, 3, "\t"):
            if cwid not in self.instructors:
                self.instructors[cwid] = Instructor(cwid, name, department)


    def add_grades(self, grades_file_path):
        for scwid, course, grade, icwid in file_reader(grades_file_path, 4, "\t"):
            self.students[scwid].add_course(course, grade)
            self.instructors[icwid].add_course(course)

        
    def student_pt(self):
        pt = PrettyTable(field_names=Student.fields())
        for student in self.students.values():
            details = student.details()
            if details[len(details) - 1] == []:
                details[len(details) - 1] = None
            pt.add_row(details)
        print(pt)


    def major_pt(self):
        pt = PrettyTable(field_names=Major.fields())

        for major in self.majors.values():
            pt.add_row(major.details())
        print(pt)


    def instructor_pt(self):
        pt = PrettyTable(field_names=Instructor.fields())
        for instructor in self.instructors.values():
            for ins in instructor.details():
                pt.add_row(ins)
        print(pt)



class RepositoryTest(unittest.TestCase):

    def test_init(self):
        directory_path = "/Users/saranshahlawat/Desktop/Stevens/Semesters/Spring 2019/SSW-810/SSW-810-A/source/data_files"
        repo_1 = Repository(directory_path)
        repo_1_student_expected_dict = {'10103': ['10103', 'Baldwin, C', 'SFEN', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540', 'SSW 555'], []], '10115': ['10115', 'Wyatt, X', 'SFEN', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540', 'SSW 555'], []], '10172': ['10172', 'Forbes, I', 'SFEN', ['SSW 555', 'SSW 567'], ['SSW 540', 'SSW 564'], ['CS 501', 'CS 513', 'CS 545']], '10175': ['10175', 'Erickson, D', 'SFEN', ['SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540', 'SSW 555'], ['CS 501', 'CS 513', 'CS 545']], '10183': ['10183', 'Chapman, O', 'SFEN', ['SSW 689'], ['SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'], ['CS 501', 'CS 513', 'CS 545']], '11399': ['11399', 'Cordova, I', 'SYEN', ['SSW 540'], ['SYS 612', 'SYS 671', 'SYS 800'], []], '11461': ['11461', 'Wright, U', 'SYEN', ['SYS 611', 'SYS 750', 'SYS 800'], ['SYS 612', 'SYS 671'], ['SSW 540', 'SSW 565', 'SSW 810']], '11658': ['11658', 'Kelly, P', 'SYEN', [], ['SYS 612', 'SYS 671', 'SYS 800'], ['SSW 540', 'SSW 565', 'SSW 810']], '11714': ['11714', 'Morton, A', 'SYEN', ['SYS 611', 'SYS 645'], ['SYS 612', 'SYS 671', 'SYS 800'], ['SSW 540', 'SSW 565', 'SSW 810']], '11788': ['11788', 'Fuller, E', 'SYEN', ['SSW 540'], ['SYS 612', 'SYS 671', 'SYS 800'], []]}
        repo_1_student_result_dict = dict()

        for student_cwid, values in repo_1.students.items():
            repo_1_student_result_dict[student_cwid] = values.details()

        self.assertEqual(repo_1_student_expected_dict, repo_1_student_result_dict)


def file_reader(path, num_fields, sep=",", header=False):
    try:
        fp = open(path, "r")
    except FileNotFoundError:
        print("Can't open", path)
    else:
        with fp:
            for index, line in enumerate(fp):
                line_split = line.strip().split(sep)
                if len(line_split) != num_fields:
                    raise ValueError(f"{path} line: {index+1}: read {len(line_split)} fields but expected {num_fields}")
                
                if index == 0 and header:
                    continue
                    
                yield tuple(line_split)

def get_instructor_summary():
    db = sqlite3.connect(DB_FILE)
    query = "select i.CWID as Instructor_cwid, i.Name, i.Dept, g.Course, count(*) as Student_cnt from HW11_instructors i join HW11_grades g on i.CWID = g.Instructor_CWID group by i.Name, i.Dept, g.Course"
    
    pt = PrettyTable(field_names=Instructor.fields())
    for row in db.execute(query):
        pt.add_row(row)
    print(pt)


def main():
    get_instructor_summary()
    # unittest.main(exit=False, verbosity=2)


if __name__ == '__main__':
    main()
