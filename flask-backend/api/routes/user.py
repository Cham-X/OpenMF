"""
Routes related to users(admin, extractor and management).
"""

from flask import Blueprint, jsonify, request
from flask.helpers import make_response
from flask_login import login_required, current_user

from api.models.admin import Admin
from api.models.extractor import Extractor
from api.models.management import Management
from api.schema.admin import AdminSchema
from api.schema.extractor import ExtractorSchema
from api.schema.management import ManagementSchema
from api.extansions import db


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)
management_schema = ManagementSchema()
managements_schema = ManagementSchema(many=True)
extractor_schema = ExtractorSchema()
extractors_schema = ExtractorSchema(many=True)

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/profile', methods=["GET"])
@login_required
def profile():
    """
    This route gives profile detail.
    """
    if(current_user.role == "admin"):
        try:
            extractor_members = extractors_schema.dump(current_user.extractor_members)
            management_members = managements_schema.dump(current_user.management_members)
            response = {
                "success": True,
                "message": "admin user fetched.",
                "user": admin_schema.dump(current_user),
                "extractor_members": extractor_members,
                "management_members": management_members
            }
            return make_response(jsonify(response)), 201
        except:
            response = {
                "success": False,
                "message": "Unable to find user, something went wrong."
            }
            return make_response(jsonify(response)), 201

    elif(current_user.role == "extractor"):
        response = {
            "success": True,
            "message": "extractor user fetched.",
            "user": extractor_schema.dump(current_user)
        }
        return make_response(jsonify(response)), 201

    response = {
            "success": True,
            "message": "management user fetched.",
            "user": extractor_schema.dump(current_user)
        }
    return make_response(jsonify(response)), 201


@user.route('/getAdmin/<int:id>', methods=["GET"])
@login_required
def getUser(id):
    """
    This handles searching an admin by id.
    """
    if id == current_user.id:
        response = {
            "success": False,
            "message": "You can't search yourself."
        }
        return make_response(jsonify(response)), 404

    user = Admin.query.filter_by(id=id).first()

    # Check if user with that id exists
    if not user:
        response = {
            "success": False,
            "message": "Admin does not exist."
        }
        return make_response(jsonify(response))

    try:
        extractor_members = extractors_schema.dump(user.extractor_members)
        management_members = managements_schema.dump(user.management_members)
        response = {
            "success": True,
            "message": "Admin user fetched.",
            "user": admin_schema.dump(user),
            "extractor_members": extractor_members,
            "management_members": management_members
        }
        return make_response(jsonify(response)), 201
    except:
        response = {
            "success": False,
            "message": "Unable to find user, something went wrong."
        }
        return make_response(jsonify(response)), 201


@user.route('/getExtractor/<int:id>', methods=["GET"])
def get_extractor(id):
    """
    This handles searching an extractor by id.
    """
    user = Extractor.query.filter_by(id=id).first()

    # Check if user with that id exists
    if not user:
        response = {
            "success": False,
            "message": "Admin does not exist."
        }
        return make_response(jsonify(response))

    response = {
        "success": True,
        "message": "Extractor fetched.",
        "user": extractor_schema.dump(user),
        "admin": admin_schema.dump(user.admin),
    }
    return make_response(jsonify(response))


@user.route('/getManagement/<int:id>', methods=["GET"])
def get_management(id):
    """
    This handles searching a management member by id.
    """
    user = Management.query.filter_by(id=id).first()

    # Check if user with that id exists
    if not user:
        response = {
            "success": False,
            "message": "Management member does not exist."
        }
        return make_response(jsonify(response))

    response = {
        "success": True,
        "message": "Management member fetched.",
        "user": management_schema.dump(user),
        "admin": admin_schema.dump(user.admin),
    }
    return make_response(jsonify(response))


@user.route('/create', methods=['POST'])
def create_user():
    """
    This will only create a new admin.
    """
    # if no data is sent at all
    try:
        req = request.get_json()
    except:
        response = {
            "success": False,
            "message": "Please provide email and password"
        }
        return make_response(jsonify(response))

    # Check if a key is missing
    try:
        email = str(req['email'])
        password = str(req['password'])
        name = str(req['name'])
    except KeyError as err:
        response = {
            "success": False,
            "message": f'please provide {str(err)}'
        }
        return make_response(jsonify(response)), 400

    # Check if already present in db
    user = Admin.query.filter_by(email=email).first()

    if user:
        response = {
            "success": False,
            "message": "Email address already exists"
        }
        return make_response(jsonify(response)), 409

    new_admin = Admin(name=name, email=email, password=password)

    db.session.add(new_admin)
    try:
        db.session.commit()
    except Exception as e:
        response = {
            "success": False,
            "message": e
        }
        return make_response(jsonify(response)), 409

    response = {
        "success": True,
        "message": "User created."
    }
    return make_response(jsonify(response)), 200



# Route for admin to add user
@user.route('/add-user', methods=['POST'])
@login_required
def add_users():
    """
    This will be used by admin
    to create new/add new member.
    """
    if(current_user.role == 'admin'):
        try:
            req = request.get_json()
            email = str(req['email'])
            password = str(req['password'])
            name = str(req['name'])
            role = str(req['role'])
        except:
            response = {
                "success": False,
                "message": "Please provide all parameters"
            }
            return make_response(jsonify(response)), 409

        # For creating extractor member
        if role == "extractor":
            extractor = Extractor.query.filter_by(email=email).first()
            if extractor:
                response = {
                    "success": False,
                    "message": "Extractor member already exists."
                }
                return make_response(response(jsonify(response))), 409
            new_extractor = Extractor(name=name, email=email, password=password, admin=current_user)
            db.session.add(new_extractor)
            try:
                db.session.commit()
            except Exception as e:
                response = {
                    "success": False,
                    "message": e
                }
                return make_response(jsonify(response))
            response = {
                "success": True,
                "message": "Extractor member created."
            }
            return make_response(jsonify(response)), 200

        # For creating management member
        elif role == "management":
            management = Management.query.filter_by(email=email).first()
            if management:
                response = {
                    "success": False,
                    "message": "Extractor member already exists."
                }
                return make_response(response(jsonify(response))), 409
            new_management = Management(name=name, email=email, password=password, admin=current_user)
            db.session.add(new_management)
            try:
                db.session.commit()
            except Exception as e:
                response = {
                    "success": False,
                    "message": e
                }
                return make_response(jsonify(response))
            response = {
                "success": True,
                "message": "Management member created."
            }
            return make_response(jsonify(response)), 200

        # For non-valid role
        else:
            response = {
                "success": False,
                "message": "Please provide a valid role."
            }
            return make_response(jsonify(response)), 409

    else:
        response = {
            "success": False,
            "message": "Only an admin can use this route."
        }
        return make_response(jsonify(response)), 404


# Route for admin to view all his users
@user.route('/all-users', methods=['GET'])
@login_required
def all_users():
    """
    This handles listing of all members of an admin.
    """
    if(current_user.role == "admin"):
        extractors = Extractor.query.filter_by(admin_id=current_user.id).filter_by(role="extractor").all()
        managements = Management.query.filter_by(admin_id=current_user.id).filter_by(role="management").all()

        extractors_json = extractors_schema.dump(extractors)
        managements_json = managements_schema.dump(managements)
        response = {
            "success": True,
            "message": "Extractor and management members fetched.",
            "extractor_members": extractors_json,
            "management_members": managements_json,
        }
        return make_response(jsonify(response)), 200
    response = {
        "success": False,
        "message": "Only an admin can use this route."
    }
    return make_response(jsonify(response)), 404


# Route to udate role of an user
@user.route('/role-update', methods=['PUT'])
@login_required
def roleupdate():
    """
    This handles role updation.
    """
    if current_user.role == 'admin':
        try:
            req = request.get_json()
            email = str(req['email'])
            password = str(req['password'])
            new_role = str(req['new_role'])
        except:
            response = {
                "success": False,
                "message": "Please provide all parameters"
            }
            return make_response(jsonify(response)), 409

        if new_role == "extractor":
            user = Management.query.filter_by(admin=current_user).filter_by(email=email).first()
            if not user:
                response = {
                    "success": False,
                    "message": f"{email} is not a management member."
                }
                return make_response(jsonify(response))

            if not user.check_password(password):
                response = {
                    "success": False,
                    "message": "wrong password."
                }
                return make_response(jsonify(response)), 409

            new_extractor = Extractor(name=user.name, email=user.email, password=password, admin=user.admin)
            db.session.add(new_extractor)
            db.session.delete(user)
            db.session.commit()
            response = {
                "success": True,
                "message": f"User {user.email} has changed to {new_role}."
            }
            return make_response(jsonify(response)), 200

        elif new_role == "management":
            user = Extractor.query.filter_by(admin=current_user).filter_by(email=email).first()
            if not user:
                response = {
                    "success": False,
                    "message": f"{email} is not a extractor member."
                }
                return make_response(jsonify(response))

            if not user.check_password(password):
                response = {
                    "success": False,
                    "message": "wrong password."
                }
                return make_response(jsonify(response)), 409

            new_management = Management(name=user.name, email=user.email,password=password, admin=user.admin)
            db.session.add(new_management)
            db.session.delete(user)
            db.session.commit()
            response = {
                "success": True,
                "message": f"User {user.email} has changed to {new_role}."
            }
            return make_response(jsonify(response)), 200

        else:
            response = {
                "success": False,
                "message": "Please provide a valid role."
            }
            return make_response(jsonify(response)), 409
    response = {
        "success": False,
        "message": "Only admin can use this route."
    }
    return make_response(jsonify(response)), 404


@user.route('/delete-user', methods=['DELETE'])
@login_required
def deleteuser():
    """
    This will be used by admin
    to delete any member's account
    """
    # Check if email is provided or not
    if current_user.role == "admin":
        try:
            req = request.get_json()
            email = str(req['email'])
        except:
            response = {
                "success": False,
                "message": "Please provide email address of member."
            }
            return make_response(jsonify(response)), 409

        user = Extractor.query.filter_by(admin=current_user).filter_by(email=email).first() or Management.query.filter_by(admin=current_user).filter_by(email=email).first()

        if not user:
            response = {
                "success": False,
                "message": "User not found.",
            }
            return make_response(jsonify(response))
        db.session.delete(user)
        db.session.commit()
        response = {
            "success": True,
            "message": "User deleted."
        }
        return make_response(jsonify(response)), 200

    response = {
        "success": False,
        "message": "Only admin can use this route."
    }
    return make_response(jsonify(response)), 404


@user.route('/delete', methods=["DELETE"])
@login_required
def delete():
    """
    This route will handle user deletion.
    """
    db.session.delete(current_user)
    db.session.commit()
    response = {
        "success": True,
        "message": "User deleted."
    }
    return make_response(jsonify(response)), 200