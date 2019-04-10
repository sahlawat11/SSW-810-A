"""
@date: Created on Mon Mar 25 14:12:11 2019

@author: Saransh Ahlawat

@description: Python program to read student, instructor and grades file and create summary for students and instructors.
"""

import unittest, os
from collections import defaultdict
from prettytable import PrettyTable

class Student:

    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = dict()


    def add_course(self, course, grade):
        self.courses[course] = grade


    def details(self):
        return [self.cwid, self.name, sorted(self.courses.keys())]

    @staticmethod
    def fields():
        return ["CWID", "Name", "Completed Courses"]



class StudentTest(unittest.TestCase):
    def test_init(self):
        student_1 = Student("12345", "Jack", "Computer Science")
        self.assertEqual(student_1.cwid, "12345")
        self.assertEqual(student_1.name, "Jack")
        self.assertEqual(student_1.major, "Computer Science")
        self.assertEqual(student_1.courses, {})

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

        self.assertEqual(student_1.details(), ['10103', 'Baldwin, C', ['SSW 564', 'SSW 567']])
        self.assertEqual(student_1.details(), ['10103', 'Baldwin, C', ['SSW 564', 'SSW 567']])


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
        self.add_students(os.path.join(dir, "students.txt"))
        self.add_instructors(os.path.join(dir, "instructors.txt"))
        self.add_grades(os.path.join(dir, "grades.txt"))
        self.student_pt()
        self.instructor_pt()


    def add_students(self, students_file_path):
        for cwid, name, major in file_reader(students_file_path, 3, "\t"):
            if cwid not in self.students:
                self.students[cwid] = Student(cwid, name, major)


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
            pt.add_row(student.details())
        print(pt)


    def instructor_pt(self):
        pt = PrettyTable(field_names=Instructor.fields())
        for instructor in self.instructors.values():
            for ins in instructor.details():
                pt.add_row(ins)
        print(pt)



class RepositoryTest(unittest.TestCase):

    def test_init(self):
        directory_path = "/Users/saranshahlawat/Desktop/Stevens/Semesters/Spring 2019/SSW-810/homework9"
        repo_1 = Repository(directory_path)
        repo_1_student_expected_dict = {'10103': ['10103', 'Baldwin, C', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']], '10115': ['10115', 'Wyatt, X', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']], '10172': ['10172', 'Forbes, I', ['SSW 555', 'SSW 567']], '10175': ['10175', 'Erickson, D', ['SSW 564', 'SSW 567', 'SSW 687']], '10183': ['10183', 'Chapman, O', ['SSW 689']], '11399': ['11399', 'Cordova, I', ['SSW 540']], '11461': ['11461', 'Wright, U', ['SYS 611', 'SYS 750', 'SYS 800']], '11658': ['11658', 'Kelly, P', ['SSW 540']], '11714': ['11714', 'Morton, A', ['SYS 611', 'SYS 645']], '11788': ['11788', 'Fuller, E', ['SSW 540']]}
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


def main():
    unittest.main(exit=False, verbosity=2)

if __name__ == '__main__':
    main()
