from approle import Role, db

def create_roles():
    # Define roles
    roles = [
        {'id': 1, 'name': 'Admin'},
        {'id': 2, 'name': 'Teacher'},
        {'id': 3, 'name': 'Staff'},
        {'id': 4, 'name': 'Student'}
    ]

    # Add roles if they do not already exist
    for role in roles:
        existing_role = Role.query.filter_by(id=role['id']).first()
        if not existing_role:
            new_role = Role(id=role['id'], name=role['name'])
            db.session.add(new_role)

    db.session.commit()
    print("Roles created successfully!")

if __name__ == "__main__":
    create_roles()




# # create_roles.py
# from approle import Role, User, db

# def create_roles():
#     admin = Role(id=1, name='Admin')
#     teacher = Role(id=2, name='Teacher')
#     staff = Role(id=3, name='Staff')
#     student = Role(id=4, name='Student')

#     db.session.add(admin)
#     db.session.add(teacher)
#     db.session.add(staff)
#     db.session.add(student)

#     db.session.commit()
#     print("Roles created successfully!")

# # Function calling will create 4 roles as planned!
# create_roles()