class Person:
    def person_info(self):
        print("This is a person")


class Student:
    def student_info(self):
        print("This is a student")


class Graduate(Person, Student):
    pass


g = Graduate()
g.person_info()
g.student_info()
