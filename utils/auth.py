def check_login(staff_no):
    # Dummy example: Map staff_no to role
    roles = {
        '1001': 'admin',
        '1002': 'staff',
        '1003': 'staff'
    }
    return roles.get(staff_no)

