# Example of the 'Large Class' code smell
# Martin Fowler Refactoring Catalog

class EmployeeManager:
    def __init__(self):
        self.employees = []
        self.departments = {}
        self.salaries = {}
        self.benefits = {}
        self.performance_reviews = {}
        self.attendance_records = {}
        self.training_records = {}
        self.expense_reports = {}
        self.hiring_requests = {}
        self.termination_requests = {}

    def add_employee(self, employee):
        self.employees.append(employee)

    def assign_department(self, employee_id, department):
        self.departments[employee_id] = department

    def set_salary(self, employee_id, salary):
        self.salaries[employee_id] = salary

    def add_benefit(self, employee_id, benefit):
        self.benefits.setdefault(employee_id, []).append(benefit)

    def record_performance_review(self, employee_id, review):
        self.performance_reviews.setdefault(employee_id, []).append(review)

    def record_attendance(self, employee_id, date):
        self.attendance_records.setdefault(employee_id, []).append(date)

    def add_training(self, employee_id, training):
        self.training_records.setdefault(employee_id, []).append(training)

    def submit_expense_report(self, employee_id, report):
        self.expense_reports.setdefault(employee_id, []).append(report)

    def request_hiring(self, position):
        self.hiring_requests[position] = 'pending'

    def request_termination(self, employee_id):
        self.termination_requests[employee_id] = 'pending'

# Usage example (for demonstration only):
if __name__ == "__main__":
    manager = EmployeeManager()
    manager.add_employee({'id': 1, 'name': 'Alice'})
    manager.set_salary(1, 90000)
    manager.assign_department(1, 'Engineering')
